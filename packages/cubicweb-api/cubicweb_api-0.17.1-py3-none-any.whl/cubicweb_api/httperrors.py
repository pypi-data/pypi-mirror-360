# copyright 2022-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact https://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
import logging

from pyramid.httpexceptions import HTTPError, exception_response

log = logging.getLogger(__name__)


def get_http_error(
    code: int, title: str, message: str, data: dict | None = None
) -> HTTPError:
    """
    Generates an HTTPError object with the given information.
    ALl parameters except the error code will be serialized in the JSON body.

    :param code: The HTTP error code
    :param title: The error title
    :param message: The error message
    :param data: A dictionary containing additional data to describe the error
    :return: An HTTPError object
    """
    return exception_response(
        code,
        json_body={
            "title": title,
            "message": message,
            "data": data,
        },
    )


def get_http_500_error() -> HTTPError:
    """
    Returns an HTTP 500 error without content as it could lead to security leaks

    :return: An HTTPError with the code set to 500
    """
    return get_http_error(
        500,
        "ServerError",
        "The server encountered an error. Please contact support.",
    )
