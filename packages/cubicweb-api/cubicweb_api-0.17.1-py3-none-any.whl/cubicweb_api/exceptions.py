import logging

from cubicweb import AuthenticationError, Forbidden, QueryError, Unauthorized
from pyramid.config import Configurator
from pyramid.request import Request
from rql import RQLException
from yams import UnknownType, ValidationError

from cubicweb_api.httperrors import get_http_500_error, get_http_error
from cubicweb_api.transaction import InvalidTransaction

log = logging.getLogger(__name__)


class ApiException(Exception):
    def __init__(self, original_exception: Exception):
        self.original_exception = original_exception


def api_exception_view(api_exception: ApiException, request: Request):
    wrapped_exception = api_exception.original_exception
    exception_name = api_exception.original_exception.__class__.__name__
    if isinstance(wrapped_exception, ValidationError):
        wrapped_exception.translate(request.cw_cnx._)
    # RQL errors -> 400
    if isinstance(
        wrapped_exception,
        ValidationError | QueryError | UnknownType | RQLException | InvalidTransaction,
    ):
        return get_http_error(
            400,
            exception_name,
            str(wrapped_exception),
        )
    # Authentication and Unauthorized -> 401
    if isinstance(wrapped_exception, AuthenticationError | Unauthorized):
        return get_http_error(
            401,
            exception_name,
            str(wrapped_exception),
        )
    # Forbidden -> 403
    if isinstance(wrapped_exception, Forbidden):
        return get_http_error(
            403,
            exception_name,
            str(wrapped_exception),
        )
    # Default case -> 500
    log.exception(
        f"Request to {request.path_qs} raised the following exception: ",
        exc_info=wrapped_exception,
    )
    return get_http_500_error()


def includeme(config: Configurator):
    config.add_exception_view(api_exception_view, context=ApiException)
