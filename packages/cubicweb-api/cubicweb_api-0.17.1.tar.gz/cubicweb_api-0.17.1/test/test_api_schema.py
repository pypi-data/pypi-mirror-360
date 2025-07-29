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
from cubicweb.schema_exporters import JSONSchemaExporter

from test.util import ApiBaseTC


class ApiSchemaTC(ApiBaseTC):
    def test_get_schema(self):
        schema = self.webapp.get(
            self.get_api_path("schema"),
        ).json
        exporter = JSONSchemaExporter()
        exported_schema = exporter.export_as_dict(self.repo.schema)

        assert exported_schema == schema
