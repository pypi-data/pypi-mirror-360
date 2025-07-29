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
from http import cookiejar as http_cookiejar

from test.util import ApiBaseTC, check_missing_custom_header_response


class ApiLogoutTC(ApiBaseTC):
    def test_successful_logout_returns_204(self):
        response = self.webapp.post(
            self.get_api_path("logout"),
            headers=self.custom_headers,
            status=204,
        )

        assert response.body == b""

    def test_missing_custom_headers_returns_400(self):
        response = self.webapp.post(
            self.get_api_path("logout"),
            status=400,
        ).json
        check_missing_custom_header_response(response)

    def test_cannot_reuse_token(self):
        response = self.webapp.get(self.get_api_path("current-user")).json
        self.assertEqual("anon", response["login"])
        self.login_request()
        response = self.webapp.get(self.get_api_path("current-user")).json
        self.assertEqual(self.admlogin, response["login"])

        # simulate that the cookies have been stolen and that someone attempts to reuse them
        stolen_jar = http_cookiejar.CookieJar()
        for cookie in self.webapp.cookiejar:
            stolen_jar.set_cookie(cookie)

        self.webapp.post(
            self.get_api_path("logout"),
            headers=self.custom_headers,
            status=204,
        )

        response = self.webapp.get(self.get_api_path("current-user")).json
        self.assertEqual("anon", response["login"])

        self.webapp.cookiejar = stolen_jar

        # check that we can't reuse the cookie
        response = self.webapp.get(self.get_api_path("current-user")).json
        self.assertEqual("anon", response["login"])


class ApiLogoutDisabledDefaultTC(ApiBaseTC):
    def includeme(self, config):
        config.include("cubicweb.pyramid.auth")
        config.include("cubicweb.pyramid.session")

    def test_logout_is_disabled(self):
        """check that it is disabled when omitting from 'cubicweb.includes'"""
        self.webapp.post(
            self.get_api_path("logout"),
            headers=self.custom_headers,
            status=404,
        )
