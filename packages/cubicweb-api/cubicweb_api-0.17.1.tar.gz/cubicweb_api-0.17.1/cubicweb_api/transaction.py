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
from cgi import FieldStorage
from typing import Literal, TypeGuard

from cubicweb import Binary
from cubicweb.rset import ResultSet
from cubicweb.server.session import Connection
from typing_extensions import TypedDict


class BinaryReference(TypedDict):
    type: Literal["binary_reference"]
    ref: str


class QueryReference(TypedDict):
    type: Literal["query_reference"]
    queryIndex: int
    row: int
    column: int


QueryParams = dict[str, str | int | float | Binary | QueryReference | BinaryReference]


class Query(TypedDict):
    query: str
    params: QueryParams | None


class InvalidTransaction(Exception):
    pass


def is_query_reference(value: object) -> TypeGuard[QueryReference]:
    return (
        isinstance(value, dict)
        and "type" in value
        and "queryIndex" in value
        and "row" in value
        and "column" in value
        and value["type"] == "query_reference"
    )


def is_binary_reference(value: object) -> TypeGuard[BinaryReference]:
    return (
        isinstance(value, dict)
        and "type" in value
        and "ref" in value
        and value["type"] == "binary_reference"
    )


class BinaryResolver:
    def __init__(self, body: dict):
        self.body = body

    def resolve(self, binary_id: str):
        field: FieldStorage | None = self.body.get(binary_id, None)
        if field is None:
            raise InvalidTransaction(f"Could not find binary of id {binary_id}")
        return Binary(field.file.read())


def resolve_query_reference(value: QueryReference, rset_list: list[ResultSet]):
    query_idx = value["queryIndex"]
    if query_idx >= len(rset_list):
        raise InvalidTransaction(
            "A query reference index refers to a request which has not yet been executed"
        )
    if query_idx < 0:
        raise InvalidTransaction("A query reference index must be a natural integer.")
    row = value["row"]
    current_rset = rset_list[query_idx]
    if row < 0 or row >= len(current_rset):
        raise InvalidTransaction(
            "A query reference row refers to an incorrect row number."
        )
    column = value["column"]
    if column < 0 or column >= len(current_rset[row]):
        raise InvalidTransaction(
            "A query reference column refers to an incorrect column number."
        )
    return rset_list[query_idx][row][column]


class Transaction:
    def __init__(
        self, queries: list[Query], binary_resolver: BinaryResolver | None = None
    ):
        self.queries = queries
        self.binary_resolver = binary_resolver

    def execute(self, cnx: Connection) -> list[ResultSet]:
        rset_list: list[ResultSet] = []
        for query in self.queries:
            try:
                resolved_params = self.resolve_parameter_references(
                    query.get("params"), rset_list
                )
                rset = cnx.execute(query["query"], resolved_params)
            except Exception:
                cnx.rollback()
                raise
            rset_list.append(rset)
        cnx.commit()
        return rset_list

    def resolve_parameter_references(
        self, params: QueryParams | None, rset_list: list[ResultSet]
    ) -> dict | None:
        if not params:
            return None
        modified_params = params.copy()
        for key, value in params.items():
            if is_query_reference(value):
                modified_params[key] = resolve_query_reference(value, rset_list)
            elif is_binary_reference(value):
                if self.binary_resolver is None:
                    raise InvalidTransaction(
                        f"Key '{key}': Unsupported reference to file '{value}'. "
                        "Make sure you sent your data in multipart/form-data format."
                    )
                modified_params[key] = self.binary_resolver.resolve(value["ref"])
            elif isinstance(value, dict):
                raise InvalidTransaction(
                    f"Key '{key}': Invalid parameter reference '{value}'. "
                    "Supported reference types are 'query_reference' and 'binary_reference'."
                )
            elif (
                not isinstance(value, int)
                and not isinstance(value, float)
                and not isinstance(value, str)
                and not isinstance(value, bool)
                and value is not None
            ):
                raise InvalidTransaction(
                    f"Key '{key}': Unsupported parameter type '{type(value)}' for value '{value}'"
                )
        return modified_params
