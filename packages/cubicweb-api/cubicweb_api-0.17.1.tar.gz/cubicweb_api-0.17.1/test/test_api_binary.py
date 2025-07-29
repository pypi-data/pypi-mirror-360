# copyright 2023-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
import json

import webtest

from test.util import ApiBaseTC


class ApiBinaryTC(ApiBaseTC):
    def upload_file(self) -> int:
        self.login_request()
        queries = [
            {
                "query": "Insert EntityWithBinary X: X binary %(binary_ref)s",
                "params": {
                    "binary_ref": {"type": "binary_reference", "ref": "test_file"}
                },
            }
        ]
        response = self.webapp.post(
            self.get_api_path("rql"),
            params={
                "queries": json.dumps(queries),
                "test_file": webtest.Upload("filename.txt", b"content"),
            },
            content_type="multipart/form-data",
            headers=self.custom_headers,
        )
        return response.json["result_sets"][0]["rows"][0][0]

    def test_download_binary(self):
        eid = self.upload_file()
        response = self.webapp.get(
            self.get_api_path("binary"),
            params={"eid": eid, "attribute": "binary"},
        )
        assert response.body, b"content"

    def test_unknown_eid(self):
        response = self.webapp.get(
            self.get_api_path("binary"),
            params={"eid": 1227, "attribute": "binary"},
            status=400,
        )
        assert response.json == {
            "title": "KeyError",
            "message": "No entity with eid 1227 in the repository",
            "data": None,
        }

    def test_unknown_attribute(self):
        eid = self.upload_file()
        response = self.webapp.get(
            self.get_api_path("binary"),
            params={"eid": eid, "attribute": "unknown"},
            status=400,
        )
        assert response.json == {
            "title": "KeyError",
            "message": "'No relation named unknown in schema'",
            "data": None,
        }

    def test_attribute_not_binary(self):
        eid = self.upload_file()
        response = self.webapp.get(
            self.get_api_path("binary"),
            params={"eid": eid, "attribute": "name"},
            status=400,
        )
        assert response.json == {
            "title": "KeyError",
            "message": "Attribute 'name' of entity 'EntityWithBinary' is not of type Bytes",
            "data": None,
        }

    def test_no_file_present(self):
        self.login_request()
        response = self.webapp.post(
            self.get_api_path("rql"),
            params=json.dumps(
                [
                    {
                        "query": "Insert EntityWithBinary X",
                        "params": {},
                    }
                ]
            ),
            content_type="application/json",
            headers=self.custom_headers,
        )
        eid = response.json["result_sets"][0]["rows"][0][0]

        response = self.webapp.get(
            self.get_api_path("binary"),
            params={"eid": eid, "attribute": "binary"},
            status=204,
        )
        assert response.body == b""

    def test_no_params_sent(self):
        response = self.webapp.get(
            self.get_api_path("binary"),
            status=400,
        ).json
        assert response == {
            "data": [
                {
                    "exception": "MissingRequiredParameter",
                    "field": "eid",
                    "message": "Missing required query parameter: eid",
                },
                {
                    "exception": "MissingRequiredParameter",
                    "field": "attribute",
                    "message": "Missing required query parameter: attribute",
                },
            ],
            "message": "Your request could not be validated against the openapi "
            "specification.",
            "title": "OpenApiValidationError",
        }

    def test_wrong_eid_type(self):
        response = self.webapp.get(
            self.get_api_path("binary"),
            params={"eid": "this is wrong", "attribute": "binary"},
            status=400,
        ).json
        assert response == {
            "data": [
                {
                    "exception": "ParameterValidationError",
                    "field": "eid",
                    "message": "Failed to cast value to integer type: this is wrong",
                }
            ],
            "message": "Your request could not be validated against the openapi "
            "specification.",
            "title": "OpenApiValidationError",
        }

    def test_wrong_attribute_type(self):
        response = self.webapp.get(
            self.get_api_path("binary"),
            params={"eid": 5, "attribute": 5},
            status=400,
        ).json
        assert response == {
            "data": [
                {
                    "exception": "ValidationError",
                    "field": "attribute",
                    "message": "'5' does not match '^[a-z_][a-z0-9_]+$'",
                }
            ],
            "message": "Your request could not be validated against the openapi "
            "specification.",
            "title": "OpenApiValidationError",
        }
