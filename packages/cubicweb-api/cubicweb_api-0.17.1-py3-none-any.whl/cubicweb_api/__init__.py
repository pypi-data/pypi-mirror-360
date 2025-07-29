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
"""cubicweb-api application package

This cube is the new api which will be integrated in CubicWeb 4.
"""

import base64
from datetime import date, datetime, time

from cubicweb import Binary
from pyramid.config import Configurator
from pyramid.interfaces import IViewDeriverInfo
from pyramid.renderers import JSON

from cubicweb_api.exceptions import ApiException
from cubicweb_api.util import get_api_path_prefix


def datetime_adapter(obj: datetime | date | time, request):
    """
    Converts datetime, date and time object to an ISO string for JSON serialization
    :param obj: the object to convert
    :param request: the current request
    :return:
    """
    return obj.isoformat()


def binary_adapter(binary: Binary, request):
    return base64.b64encode(binary.read()).decode("ascii")


def api_exception_view_deriver(view, info: IViewDeriverInfo):
    if info.options.get("use_api_exceptions"):

        def wrapper_view(context, request):
            try:
                response = view(context, request)
            except Exception as e:
                raise ApiException(e) from e
            return response

        return wrapper_view
    return view


def includeme(config: Configurator):
    json_renderer = JSON()
    json_renderer.add_adapter(datetime, datetime_adapter)
    json_renderer.add_adapter(date, datetime_adapter)
    json_renderer.add_adapter(time, datetime_adapter)
    json_renderer.add_adapter(Binary, binary_adapter)

    api_exception_view_deriver.options = ("use_api_exceptions",)
    config.add_view_deriver(api_exception_view_deriver)

    config.include(".exceptions")
    config.include(".predicates")

    config.add_renderer("cubicweb_api_json", json_renderer)
    config.include(".routes", route_prefix=get_api_path_prefix(config))
