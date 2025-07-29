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


class ApiMountedOnBaseUrlTC(ApiBaseTC):
    @classmethod
    def init_config(cls, config):
        super().init_config(config)
        config.global_set_option("base-url", "https://testing.cubicweb/base_path")
        config.global_set_option("receives-base-url-path", True)

    def test_served_on_base_url_path(self):
        self.webapp.get(
            "https://testing.cubicweb/base_path/api/v1/schema",
            headers=self.custom_headers,
            status=200,
        )


class ApiMountedOnRootTC(ApiBaseTC):
    @classmethod
    def init_config(cls, config):
        super().init_config(config)
        config.global_set_option("base-url", "https://testing.cubicweb/base_path")
        config.global_set_option("receives-base-url-path", False)

    def test_served_on_base_url_path(self):
        self.webapp.get(
            "https://testing.cubicweb/api/v1/schema",
            headers=self.custom_headers,
            status=200,
        )


class ApiMountedCustomPrefixTC(ApiBaseTC):
    settings = {
        "cubicweb.includes": ["cubicweb.pyramid.auth"],
        "cubicweb_api.enable_login_route": "yes",
        "cubicweb_api.api_path_prefix": "custom/url",
    }

    def test_served_on_base_url_path(self):
        self.webapp.get(
            "https://testing.cubicweb/custom/url/v1/schema",
            headers=self.custom_headers,
            status=200,
        )


if __name__ == "__main__":
    from unittest import main

    main()
