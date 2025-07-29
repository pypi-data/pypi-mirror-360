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
from test.util import ApiBaseTC


class ApiCurrentUserTC(ApiBaseTC):
    def test_current_user_returns_user_as_json(self):
        self.login_request()
        response = self.webapp.get(self.get_api_path("current-user"), status=200).json

        assert response["login"] == self.admlogin
        assert response["dcTitle"] == self.admlogin
        assert isinstance(response["eid"], int)

    def test_current_user_anonymous(self):
        response = self.webapp.get(self.get_api_path("current-user"), status=200).json

        assert response["login"] == "anon"
        assert response["dcTitle"] == "anon"
        assert isinstance(response["eid"], int)
