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
import json

from test.util import ApiBaseTC, check_missing_custom_header_response


class ApiLoginTC(ApiBaseTC):
    def test_successful_login_returns_204(self):
        response = self.webapp.post(
            self.get_api_path("login"),
            params=json.dumps({"login": self.admlogin, "password": self.admpassword}),
            content_type="application/json",
            headers=self.custom_headers,
            status=204,
        )

        assert response.body == b""

    def test_wrong_password_returns_401(self):
        response = self.webapp.post(
            self.get_api_path("login"),
            params=json.dumps({"login": self.admlogin, "password": "INVALID PASSWORD"}),
            content_type="application/json",
            headers=self.custom_headers,
            status=401,
        ).json

        assert response == {
            "data": None,
            "message": "Invalid credentials",
            "title": "AuthenticationError",
        }

    def test_wrong_login_returns_401(self):
        response = self.webapp.post(
            self.get_api_path("login"),
            params=json.dumps(
                {"login": "a_login_that_does_not_exist", "password": "PASSWORD"}
            ),
            content_type="application/json",
            headers=self.custom_headers,
            status=401,
        ).json

        assert response == {
            "data": None,
            "message": "Invalid credentials",
            "title": "AuthenticationError",
        }

    def test_invalid_login_type(self):
        response = self.webapp.post(
            self.get_api_path("login"),
            params=json.dumps({"login": 5, "password": "PASSWORD"}),
            content_type="application/json",
            headers=self.custom_headers,
            status=400,
        ).json

        assert response == {
            "data": [
                {
                    "exception": "ValidationError",
                    "field": "login",
                    "message": "5 is not of type 'string'",
                }
            ],
            "message": "Your request could not be validated against the openapi "
            "specification.",
            "title": "OpenApiValidationError",
        }

    def test_invalid_password_type(self):
        response = self.webapp.post(
            self.get_api_path("login"),
            params=json.dumps({"login": "login", "password": 5}),
            content_type="application/json",
            headers=self.custom_headers,
            status=400,
        ).json

        assert response == {
            "data": [
                {
                    "exception": "ValidationError",
                    "field": "password",
                    "message": "5 is not of type 'string'",
                }
            ],
            "message": "Your request could not be validated against the openapi "
            "specification.",
            "title": "OpenApiValidationError",
        }

    def test_wrong_content_type_returns_400(self):
        response = self.webapp.post(
            self.get_api_path("login"),
            params=json.dumps({"login": self.admlogin, "password": self.admpassword}),
            content_type="text/plain",
            headers=self.custom_headers,
            status=400,
        ).json

        assert response == {
            "data": [
                {
                    "exception": "RequestBodyValidationError",
                    "message": "Content for the following mimetype not found: "
                    "text/plain. Valid mimetypes: ['application/json']",
                }
            ],
            "message": "Your request could not be validated against the openapi "
            "specification.",
            "title": "OpenApiValidationError",
        }

    def test_wrong_params_returns_400(self):
        response = self.webapp.post(
            self.get_api_path("login"),
            params=json.dumps({"test": "testing"}),
            content_type="application/json",
            headers=self.custom_headers,
            status=400,
        ).json

        assert response == {
            "data": [
                {
                    "exception": "ValidationError",
                    "field": "login/password",
                    "message": "'login' is a required property",
                },
                {
                    "exception": "ValidationError",
                    "field": "login/password",
                    "message": "'password' is a required property",
                },
            ],
            "message": "Your request could not be validated against the openapi "
            "specification.",
            "title": "OpenApiValidationError",
        }

    def test_missing_login_data_returns_400(self):
        response = self.webapp.post(
            self.get_api_path("login"),
            content_type="application/json",
            headers=self.custom_headers,
            status=400,
        ).json

        assert response == {
            "data": [
                {
                    "exception": "MissingRequiredRequestBody",
                    "message": "Missing required request body",
                }
            ],
            "message": "Your request could not be validated against the openapi "
            "specification.",
            "title": "OpenApiValidationError",
        }

    def test_missing_custom_headers_returns_400(self):
        response = self.webapp.post(
            self.get_api_path("login"),
            status=400,
        ).json
        check_missing_custom_header_response(response)
        response = self.webapp.post(
            self.get_api_path("login"),
            params=json.dumps({"login": self.admlogin, "password": self.admpassword}),
            content_type="application/json",
            status=400,
        ).json
        check_missing_custom_header_response(response)


class ApiLoginDisabledDefaultTC(ApiBaseTC):
    def includeme(self, config):
        config.include("cubicweb.pyramid.auth")
        config.include("cubicweb.pyramid.session")

    def test_login_is_disabled(self):
        """check that it is disabled when omitting from 'cubicweb.includes'"""
        self.webapp.post(
            self.get_api_path("login"),
            params=json.dumps({"login": self.admlogin, "password": self.admpassword}),
            content_type="application/json",
            headers=self.custom_headers,
            status=404,
        )
