from cubicweb import AuthenticationError
from pyramid.config import Configurator

from cubicweb_api import ApiException


class AnonymousOrConnectedUserPredicate:
    def __init__(self, value, config):
        self.value = value

    def text(self):
        return f"anonymous_or_connected = {self.value}"

    phash = text

    def __call__(self, context, request):
        if (
            request.authenticated_userid is not None
            or request.registry["cubicweb.repository"].config["anonymous-user"]
            is not None
        ):
            return True
        raise ApiException(AuthenticationError())


def includeme(config: Configurator):
    config.add_view_predicate(
        "anonymous_or_connected", AnonymousOrConnectedUserPredicate
    )
