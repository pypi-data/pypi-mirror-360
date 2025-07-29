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
from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_api.transaction import InvalidTransaction, Transaction


class ApiTransactionTC(CubicWebTC):
    def test_transaction(self):
        queries = [
            {
                "query": "INSERT CWUser U: U login %(login)s, U upassword 'AZJEJAZO'",
                "params": {"login": "ginger"},
            },
            {
                "query": "INSERT CWGroup G: G name %(name)s",
                "params": {"name": "chickens"},
            },
            {
                "query": "SET U in_group G WHERE U eid %(ginger_eid)s, G eid %(chickens_eid)s",
                "params": {
                    "ginger_eid": {
                        "type": "query_reference",
                        "queryIndex": 0,
                        "row": 0,
                        "column": 0,
                    },
                    "chickens_eid": {
                        "type": "query_reference",
                        "queryIndex": 1,
                        "row": 0,
                        "column": 0,
                    },
                },
            },
        ]
        transaction = Transaction(queries)
        with self.admin_access.cnx() as cnx:
            rsets = transaction.execute(cnx)
            ginger_eid = rsets[0][0][0]
            ginger = cnx.entity_from_eid(ginger_eid)
            assert ginger.login == "ginger"
            assert "chickens" in [group.name for group in ginger.in_group]

    def test_wrong_query_index_raises(self):
        for queryIndex, row, column in [
            (-1, 0, 0),
            (3, 0, 0),
            (0, -1, 0),
            (0, 1, 0),
            (0, 0, -1),
            (0, 0, 1),
        ]:
            queries = [
                {
                    "query": "INSERT CWUser U: U login %(login)s, U upassword 'AZJEJAZO'",
                    "params": {"login": "ginger"},
                },
                {
                    "query": "INSERT CWGroup G: G name %(name)s",
                    "params": {"name": "chickens"},
                },
                {
                    "query": "SET U in_group G WHERE U eid %(ginger_eid)s, G eid %(chickens_eid)s",
                    "params": {
                        "ginger_eid": {
                            "type": "query_reference",
                            "queryIndex": queryIndex,
                            "row": row,
                            "column": column,
                        },
                        "chickens_eid": {
                            "type": "query_reference",
                            "queryIndex": 1,
                            "row": 0,
                            "column": 0,
                        },
                    },
                },
            ]
            transaction = Transaction(queries)
            with self.admin_access.cnx() as cnx:
                with self.assertRaises(
                    InvalidTransaction,
                    msg=(
                        f"reference {{queryIndex: {queryIndex}, row: {row}, column:{column}}}"
                        "should be invalid"
                    ),
                ):
                    transaction.execute(cnx)

    def test_malformed_query_ref_raises(self):
        queries = [
            {
                "query": "INSERT CWUser U: U login %(login)s, U upassword 'AZJEJAZO'",
                "params": {"login": "ginger"},
            },
            {
                "query": "INSERT CWGroup G: G name %(name)s",
                "params": {"name": "chickens"},
            },
            {
                "query": "SET U in_group G WHERE U eid %(ginger_eid)s, G eid %(chickens_eid)s",
                "params": {
                    "ginger_eid": {"queryIndex": 0, "row": 0, "column": 0},
                    "chickens_eid": {
                        "type": "query_reference",
                        "queryIndex": 1,
                    },
                },
            },
        ]
        transaction = Transaction(queries)
        with self.admin_access.cnx() as cnx:
            with self.assertRaises(
                InvalidTransaction,
                msg="Malformed query ref should be invalid",
            ):
                transaction.execute(cnx)
