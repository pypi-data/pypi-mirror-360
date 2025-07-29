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

from functools import partial

from cubicweb import AuthenticationError
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.response import Response
from pyramid.security import forget, remember

from cubicweb_api.routes import VIEW_DEFAULTS, ApiRoutes, get_route_name
from cubicweb_api.util import get_cw_repo


def login_view(request: Request):
    """
    See the openapi/openapi_template.yml
    file for more information about this route.
    """
    request_params = request.openapi_validated.body
    login: str = request_params["login"]
    pwd: str = request_params["password"]

    repo = get_cw_repo(request)
    with repo.internal_cnx() as cnx:
        try:
            cwuser = repo.authenticate_user(cnx, login, password=pwd)
        except AuthenticationError:
            raise AuthenticationError("Invalid credentials")

        headers = remember(
            request,
            cwuser.eid,
        )
        return Response(headers=headers, status=204)


def logout_view(request: Request):
    """
    See the openapi/openapi_template.yml
    file for more information about this route.
    """
    headers = forget(request)
    return Response(headers=headers, status=204)


def includeme(config: Configurator):
    add_view = partial(config.add_view, **VIEW_DEFAULTS)

    add_view(
        view=login_view,
        route_name=get_route_name(ApiRoutes.login),
        anonymous_or_connected=None,
    )
    add_view(
        view=logout_view,
        route_name=get_route_name(ApiRoutes.logout),
        anonymous_or_connected=None,
    )
