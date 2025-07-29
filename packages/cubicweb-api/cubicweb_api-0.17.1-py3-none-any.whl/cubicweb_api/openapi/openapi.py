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
from os import path
from pathlib import Path

import yaml
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.response import Response
from pyramid_openapi3 import (
    RequestValidationError,
    ResponseValidationError,
    openapi_validation_error,
)

from cubicweb_api.constants import API_ROUTE_NAME_PREFIX
from cubicweb_api.httperrors import get_http_500_error, get_http_error
from cubicweb_api.util import (
    get_cw_all_in_one_config,
    get_openapi_spec_server_url,
)

log = logging.getLogger(__name__)

OPENAPI_PYRAMID_KEY = "x-pyramid-route-name"


def get_template_file_path() -> Path:
    """
    Gets the path to the OpenApi specification template file.
    This file should not be written to. It serves as a base to generate OpenApi specification files
    specific to a CubicWeb instance.

    :return: OpenApi template file path.
    """
    return Path(path.dirname(__file__), "openapi_template.yaml")


def get_production_file_path(config: Configurator) -> str:
    """
    Gets the path to the generated OpenApi specification from the instance's home.
    This file needs "write" permission as it will be generated from the template.

    :param config: The pyramid configuration
    :return: OpenApi specification file path.
    """
    return path.join(get_cw_all_in_one_config(config).apphome, "openapi.yaml")


def generate_openapi_file(server_url, file_path):
    """
    Generates the OpenAPi specification file from the template
    and the CubicWeb instance's configuration.

    :param config: The pyramid configuration
    """
    spec_dict: dict = yaml.safe_load(get_template_file_path().open())
    paths_dict: dict[str, dict] | None = spec_dict["paths"]
    for path_str, path_item in paths_dict.items():
        # Update the pyramid route name
        path_item[OPENAPI_PYRAMID_KEY] = (
            f"{API_ROUTE_NAME_PREFIX}{path_item[OPENAPI_PYRAMID_KEY]}"
        )

    # Add the server base url in the specification
    # to make sure OpenApi can detect the current server
    spec_dict["servers"] = [{"url": server_url}]
    if path.exists(file_path):
        with open(file_path) as file:
            if yaml.safe_load(file) == spec_dict:
                log.info(f"Not writing already up to date {file_path}")
                return

    log.info(f"Writing {file_path}")
    with open(file_path, "w") as file:
        yaml.dump(spec_dict, file)


def setup_openapi(config: Configurator):
    """
    Setup the OpenApi specification for the current CubicWeb instance and registers OpenApi routes.

    :param config: The pyramid configuration
    """
    config.include("pyramid_openapi3")
    server_url = get_openapi_spec_server_url(config)
    file_path = get_production_file_path(config)
    generate_openapi_file(server_url, file_path)
    # TODO block access if anonymous access is disabled and user is not connected
    # Add a route to download the OpenApi specification in YAML format
    config.pyramid_openapi3_spec(
        get_production_file_path(config),
        route="openapi.yaml",
    )
    # Add a route to explore the API using Swagger UI
    config.pyramid_openapi3_add_explorer(route="openapi")
    config.registry.settings["pyramid_openapi3.enable_endpoint_validation"] = True
    config.registry.settings["pyramid_openapi3.enable_request_validation"] = True
    # Do not validate responses as it could slow down the server
    config.registry.settings["pyramid_openapi3.enable_response_validation"] = False
    # Update OpenApi exception views to use our API error format
    config.add_exception_view(
        view=custom_openapi_validation_error, context=RequestValidationError
    )
    config.add_exception_view(
        view=custom_openapi_validation_error, context=ResponseValidationError
    )


def custom_openapi_validation_error(
    context: RequestValidationError | ResponseValidationError, request: Request
) -> Response:
    """
    Overrides default pyramid_openapi3 errors to match the API format.
    """
    error_response = openapi_validation_error(context, request)

    status = error_response.status_code
    body = error_response.json_body
    if status == 500:
        return get_http_500_error()
    if status == 400:
        return get_http_error(
            error_response.status_code,
            "OpenApiValidationError",
            "Your request could not be validated against the openapi specification.",
            body,
        )

    return get_http_error(error_response.status_code, "OpenAPI Error", "", body)
