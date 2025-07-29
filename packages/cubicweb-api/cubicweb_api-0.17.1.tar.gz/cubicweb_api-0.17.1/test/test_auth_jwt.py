# copyright 2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
from test.util import ApiBaseTC


class AuthJWTDisabledTC(ApiBaseTC):
    def test_JWT_disabled_default(self):
        self.login_request()

        jwt_present = False
        for cookie in self.webapp.cookiejar:
            if cookie.name == "CW_JWT":
                jwt_present = True

        self.assertFalse(jwt_present)


class AuthJWTEnabledTC(ApiBaseTC):
    settings = {
        **ApiBaseTC.settings,
        "cubicweb.auth.authtkt.session.secret": "test",
    }

    def includeme(self, config):
        config.include("cubicweb.pyramid.auth")
        config.include("cubicweb.pyramid.session")
        config.include("cubicweb_api.auth.routes")
        config.include("cubicweb_api.auth.jwt")

    def test_JWT_enabled(self):
        self.login_request()

        jwt_present = False
        for cookie in self.webapp.cookiejar:
            if cookie.name == "CW_JWT":
                jwt_present = True

        self.assertTrue(jwt_present)
