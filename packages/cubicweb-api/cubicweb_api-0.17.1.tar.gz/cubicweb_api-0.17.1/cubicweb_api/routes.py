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
from enum import Enum
from functools import partial

from cubicweb import Binary
from cubicweb._exceptions import UnknownEid
from cubicweb.entities import AnyEntity
from cubicweb.pyramid.core import Connection
from cubicweb.rset import ResultSet
from cubicweb.schema_exporters import JSONSchemaExporter
from cubicweb.sobjects.services import GcStatsService, StatsService
from pyramid.config import Configurator
from pyramid.request import Request
from yams.schema import RelationDefinitionSchema
from yams.types import DefinitionName

from cubicweb_api.constants import (
    API_ROUTE_NAME_PREFIX,
)
from cubicweb_api.httperrors import get_http_error
from cubicweb_api.openapi.openapi import setup_openapi
from cubicweb_api.transaction import BinaryResolver, Transaction
from cubicweb_api.util import get_cw_repo

log = logging.getLogger(__name__)


VIEW_DEFAULTS = dict(
    request_method="POST",
    renderer="cubicweb_api_json",
    # CSRF protection using tokens only apply if the api is used by <form/> HTML components
    # This API is more generic thus we use custom HTTP headers
    # Each request expects the header "X-Client-Name: <YOUR_CLIENT>" to be set
    #
    # More information about CSRF protection in the OWASP cheatsheet:
    # https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#custom-request-headers
    # Note: Only the multipart route is subject to CSRF, but we add the custom
    #       header on all routes for consistency
    require_csrf=False,
    openapi=True,
    use_api_exceptions=True,
    anonymous_or_connected=True,
)


class ApiRoutes(Enum):
    """
    All the available routes as listed in the openapi/openapi_template.yml file.
    """

    schema = "schema"
    rql = "rql"
    binary = "binary"
    login = "login"
    logout = "logout"
    current_user = "current_user"
    siteinfo = "siteinfo"
    help = "help"


def get_route_name(route_name: ApiRoutes) -> str:
    """
    Generates a unique route name using the api
    prefix to prevent clashes with routes from other cubes.

    :param route_name: The route name base
    :return: The generated route name
    """
    return f"{API_ROUTE_NAME_PREFIX}{route_name.value}"


def schema_view(request: Request):
    """
    See the openapi/openapi_template.yml
    file for more information about this route.
    """
    repo = get_cw_repo(request)
    exporter = JSONSchemaExporter()
    exported_schema = exporter.export_as_dict(repo.schema)
    return exported_schema


def _transaction_result_to_json(rsets: list[ResultSet]):
    json_result = {
        "result_sets": [
            {
                "column_names": rset.variables,
                "rows": rset.rows,
            }
            for rset in rsets
        ]
    }
    return json_result


def rql_multipart_view(request: Request):
    """
    See the openapi/openapi_template.yml
    file for more information about this route.
    """
    body = request.openapi_validated.body

    queries = body["queries"]

    # XXX: `queries" property is correctly parsed as an array of records but
    # openapi-core doesn't support `schema.additionalProperties` which we would
    # normally use to check form-data fields corresponding to binary params.
    # A workaround is to get these binary params from the pyramid request
    # itself instead of retrieving them from the validated body.
    transaction = Transaction(queries, BinaryResolver(request.params))
    return _transaction_result_to_json(transaction.execute(request.cw_cnx))


def rql_view(request: Request):
    """
    See the openapi/openapi_template.yml
    file for more information about this route.
    """
    queries = request.openapi_validated.body
    transaction = Transaction(queries)
    return _transaction_result_to_json(transaction.execute(request.cw_cnx))


def binary_view(request: Request):
    request_params = request.openapi_validated.parameters.query
    eid: int = request_params["eid"]
    attribute_name: DefinitionName = request_params["attribute"]
    cw_cnx: Connection = request.cw_cnx

    try:
        entity: AnyEntity = cw_cnx.entity_from_eid(eid)
        rel_def: RelationDefinitionSchema = entity.e_schema.relation_definition(
            attribute_name
        )
    except (UnknownEid, KeyError) as e:
        return get_http_error(
            400,
            "KeyError",
            str(e),
        )

    if rel_def.object.type != "Bytes":
        return get_http_error(
            400,
            "KeyError",
            f"Attribute '{attribute_name}' of "
            f"entity '{entity.cw_etype}' is not of type Bytes",
        )
    attribute = getattr(entity, attribute_name)
    if attribute is None:
        request.response.status_code = 204
        request.response.content_type = None
    else:
        binary: Binary = attribute
        request.response.content_type = "application/octet-stream"
        request.response.body = binary.read()
    return request.response


def current_user_view(request: Request) -> dict:
    """
    See the openapi/openapi_template.yml
    file for more information about this route.
    """
    user = request.cw_cnx.user
    return {"eid": user.eid, "login": user.login, "dcTitle": user.dc_title()}


def siteinfo_view(request: Request):
    """
    display debugging information about the current website
    """
    repo = get_cw_repo(request)
    version_configuration = repo.get_versions()

    pyvalue = {
        "config_type": repo.vreg.config.name,
        "config_mode": repo.vreg.config.mode,
        "instance_home": repo.vreg.config.apphome,
        "cubicweb": version_configuration.get("cubicweb", "no version configuration"),
        "cubes": {
            pk.replace("system.version.", ""): version
            for pk, version in request.cw_cnx.execute(
                "Any K,V WHERE P is CWProperty, P value V, P pkey K, "
                'P pkey ~="system.version.%"',
                build_descr=False,
            )
        },
        "base_url": repo.config["base-url"],
        "datadir_url": getattr(repo.vreg.config, "datadir_url", None),
    }

    return {
        "info": {
            "pyvalue": pyvalue,
            "stats": StatsService(request.cw_cnx).call(),
        },
        "registry": {
            x: {a: [str(klass) for klass in b] for a, b in y.items()}
            for x, y in repo.vreg.items()
        },
        "gc": GcStatsService(request.cw_cnx).call(),
    }


def includeme(config: Configurator):
    setup_openapi(config)
    config.pyramid_openapi3_register_routes()

    add_view = partial(config.add_view, **VIEW_DEFAULTS)

    add_view(
        view=schema_view,
        route_name=get_route_name(ApiRoutes.schema),
        request_method="GET",
    )

    add_view(
        view=rql_multipart_view,
        route_name=get_route_name(ApiRoutes.rql),
        header="Content-Type:multipart/form-data",
    )

    add_view(
        view=rql_view,
        route_name=get_route_name(ApiRoutes.rql),
    )

    add_view(
        view=binary_view,
        route_name=get_route_name(ApiRoutes.binary),
        request_method="GET",
        renderer=None,
    )

    add_view(
        view=current_user_view,
        route_name=get_route_name(ApiRoutes.current_user),
        request_method="GET",
    )

    add_view(
        view=siteinfo_view,
        route_name=get_route_name(ApiRoutes.siteinfo),
        request_method="GET",
    )
