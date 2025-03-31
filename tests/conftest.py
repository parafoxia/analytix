# Copyright (c) 2021-present, Ethan Henderson
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import datetime as dt
import json
from pathlib import Path
from typing import Any
from typing import Iterator
from unittest import mock

import pytest
import pytz

from analytix.auth.scopes import Scopes
from analytix.auth.secrets import AuthContext
from analytix.auth.secrets import ClientSecrets
from analytix.auth.secrets import Secrets
from analytix.auth.tokens import Tokens
from analytix.auth.tokens import _ExpiresIn
from analytix.client import Client
from analytix.client import SessionContext
from analytix.groups import Group
from analytix.groups import GroupItem
from analytix.groups import GroupItemList
from analytix.groups import GroupList
from analytix.queries import ReportQuery
from analytix.reports.features import Dimensions
from analytix.reports.features import ExactlyOne
from analytix.reports.features import Filters
from analytix.reports.features import Metrics
from analytix.reports.features import OneOrMore
from analytix.reports.features import Optional
from analytix.reports.features import Required
from analytix.reports.features import SortOptions
from analytix.reports.features import ZeroOrMore
from analytix.reports.features import ZeroOrOne
from analytix.reports.interfaces import Report
from analytix.reports.resources import ColumnHeader
from analytix.reports.resources import ColumnType
from analytix.reports.resources import DataType
from analytix.reports.resources import ResultTable
from analytix.reports.types import TimeBasedActivity
from tests import MockFile
from tests import MockResponse

# NEW ------------------------------------------------------------------


@pytest.fixture()
def client_secrets() -> ClientSecrets:
    return ClientSecrets(
        client_id="client_id",
        client_secret="client_secret",
        redirect_uris=["http://localhost/"],
        auth_uri="https://accounts.google.com/o/oauth2/auth",
        token_uri="https://oauth2.googleapis.com/token",
        client_email=None,
        auth_provider_x509_cert_url="https://www.googleapis.com/oauth2/v1/certs",
        client_x509_cert_url=None,
    )


@pytest.fixture()
def client_secrets_file(client_secrets: ClientSecrets) -> Iterator[MockFile]:
    data = {
        "installed": {
            "client_id": client_secrets.client_id,
            "project_id": "barney-the-dinosaur",
            "client_secret": client_secrets.client_secret,
            "redirect_uris": client_secrets.redirect_uris,
            "auth_uri": client_secrets.auth_uri,
            "token_uri": client_secrets.token_uri,
            "auth_provider_x509_cert_url": client_secrets.auth_provider_x509_cert_url,
        }
    }
    return MockFile(json.dumps(data).encode("utf-8"))


@pytest.fixture()
def auth_context(client_secrets) -> AuthContext:
    return AuthContext(
        client_id=client_secrets.client_id,
        client_secret=client_secrets.client_secret,
        redirect_uri="http://localhost:8080",
        auth_uri=(
            "https://accounts.google.com/o/oauth2/auth"
            "?client_id=client_id"
            "&nonce=token"
            "&response_type=code"
            "&redirect_uri=http%3A%2F%2Flocalhost%3A8080&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyt-analytics.readonly"
            "&state=token"
            "&access_type=offline"
        ),
        token_uri=client_secrets.token_uri,
        state="token",
    )


@pytest.fixture()
def secrets(client_secrets: ClientSecrets) -> Secrets:
    return Secrets(type="installed", resource=client_secrets, scopes=Scopes.READONLY)


@pytest.fixture()
def tokens() -> Tokens:
    return Tokens(
        access_token="access_token",
        expires_in=_ExpiresIn(default=3599),
        scope="https://www.googleapis.com/auth/yt-analytics.readonly",
        token_type="Bearer",
        refresh_token="refresh_token",
        id_token="id_token",
    )


@pytest.fixture()
def tokens_json(tokens: Tokens) -> str:
    return json.dumps(
        {
            "access_token": tokens.access_token,
            "expires_in": tokens.expires_in,
            "scope": tokens.scope,
            "token_type": tokens.token_type,
            "refresh_token": tokens.refresh_token,
            "id_token": tokens.id_token,
        }
    )


@pytest.fixture()
def tokens_file(tokens_json: str) -> Iterator[MockFile]:
    data = json.loads(tokens_json)
    file = MockFile(json.dumps(data).encode("utf-8"))
    with mock.patch.object(Path, "open", return_value=file):
        yield file


@pytest.fixture()
def public_jwks() -> str:
    return json.dumps(
        {
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "alg": "RS256",
                    "kid": "420",
                    "n": "3O1ym3_YzGYXHm-Pd6toEDvCx_KsL-68m3N8dOf9bb17GnRoUfUL4HLBFCnpqcmmwqT9Cm9TWuskyynht0c1AWFsW6a8eDeJu_lTwFnydgzQn4EU-yeIE82GbvriC-3SmPLUApNALZCgWmWjDlAFB94SybR9TA3Qqb9IPc0c5QXTCeBmJzhfOBJ5VlMwYsWnftuGxjT4lvlGNO1Ifqa09CedKr5TuNS7L3joMI4RRtejuC_p3LsBgnZ_7kV5C4t4n8USBBnyNms6GQvBoqHLctL56fNHva7vY-dsEZ4VNUeYRjIIuQ6BaAoCZQbbhTfJDBsRBRdq41aOw92xSlGA4Q",
                    "e": "AQAB",
                }
            ]
        }
    )


@pytest.fixture()
def id_token() -> str:
    return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZG1pbiI6dHJ1ZSwiaWF0IjoxNTE2MjM5MDIyLCJuYW1lIjoiQmFybmV5IHRoZSBEaW5vc2F1ciIsInN1YiI6IjEyMzQ1Njc4OTAifQ.glf1K2N9SacjpaK2W_PkqB7Ga-KwmEEpcQUFUhHmfYvd-2eWjWJN3oatXF4gkwh9O7tSqO3QW_REfpgbD-odCn3CZtZGffDEoIkujRwbr8rwnrnDK0aakspEsHBfPPctwOI6SpSqAn4LWdyK5SWzES8NnzJp6OiSXALPW92JkN9Z_pTktO1VL1IQm-NcXz3jOfqewneEkesdm8vesxd1mIeUelkKWpqg0UlT48GKZlkn08BU5GUWCLWxLj96qee4PGmfHsGb6uPx2iqL0BMI9JbKSo6MnkCmjZKwCzJdsYDYfncoDdbm3O_qUCVU4Br7T2HP3YUe-c01zwnzyXqP0A"


@pytest.fixture()
def id_token_payload() -> dict[str, Any]:
    return {
        "admin": True,
        "iat": 1516239022,
        "name": "Barney the Dinosaur",
        "sub": "1234567890",
    }


@pytest.fixture()
def session_context() -> SessionContext:
    return SessionContext("access_token", Scopes.READONLY)


@pytest.fixture()
def client(client_secrets_file: MockFile) -> Client:
    with mock.patch.object(Path, "open", return_value=client_secrets_file):
        client = Client("secrets.json")
    return client


# OLD ------------------------------------------------------------------


@pytest.fixture()
def group(client):
    return Group(
        kind="youtube#group",
        etag="f6g7h8i9j0",
        id="a1b2c3d4e5",
        published_at=dt.datetime(2022, 11, 30, 12, 34, 56, 789000, tzinfo=pytz.utc),
        title="Barney the Dinosaur",
        item_count=69,
        item_type="youtube#video",
        client=client,
    )


@pytest.fixture()
def group_list(group):
    return GroupList(
        kind="youtube#groupListResponse",
        etag="f6g7h8i9j0",
        items=[group],
        next_page_token="a1b2c3d4e5",
    )


@pytest.fixture()
def empty_group_list():
    return GroupList(
        kind="youtube#groupListResponse",
        etag=None,
        items=[],
        next_page_token=None,
    )


@pytest.fixture()
def group_item(group_item_data):
    return GroupItem.from_json(group_item_data)


@pytest.fixture()
def group_item_list(group_item):
    return GroupItemList(
        kind="youtube#groupItemListResponse",
        etag="a1b2c3d4e5",
        items=[group_item],
    )


@pytest.fixture()
def group_data():
    return {
        "kind": "youtube#group",
        "etag": "f6g7h8i9j0",
        "id": "a1b2c3d4e5",
        "snippet": {
            "publishedAt": "2022-11-30T12:34:56.789Z",
            "title": "Barney the Dinosaur",
        },
        "contentDetails": {
            "itemCount": "69",
            "itemType": "youtube#video",
        },
    }


@pytest.fixture()
def group_list_data(group_data):
    return {
        "kind": "youtube#groupListResponse",
        "etag": "f6g7h8i9j0",
        "items": [group_data],
        "nextPageToken": "a1b2c3d4e5",
    }


@pytest.fixture()
def empty_group_list_data():
    return {
        "kind": "youtube#groupListResponse",
        "items": [],
    }


@pytest.fixture()
def group_item_list_data(group_item_data):
    return {
        "kind": "youtube#groupItemListResponse",
        "etag": "a1b2c3d4e5",
        "items": [group_item_data],
    }


@pytest.fixture()
def group_item_data():
    return {
        "kind": "youtube#groupItem",
        "etag": "f6g7h8i9j0",
        "id": "e5d4c3b2a1",
        "groupId": "a1b2c3d4e5",
        "resource": {
            "kind": "youtube#video",
            "id": "j0i9h8g7f6",
        },
    }


@pytest.fixture()
def response_data():
    return json.dumps(
        {
            "kind": "youtubeAnalytics#resultTable",
            "columnHeaders": [
                {"name": "day", "dataType": "STRING", "columnType": "DIMENSION"},
                {"name": "views", "dataType": "INTEGER", "columnType": "METRIC"},
            ],
            "rows": [
                ["2022-06-20", 778],
                ["2022-06-21", 1062],
                ["2022-06-22", 946],
                ["2022-06-23", 5107],
                ["2022-06-24", 2137],
                ["2022-06-25", 1005],
                ["2022-06-26", 888],
            ],
        }
    ).encode("utf-8")


@pytest.fixture()
def error_response_data():
    return json.dumps(
        {"error": {"code": 403, "message": "You ain't allowed, son."}}
    ).encode("utf-8")


@pytest.fixture()
def auth_error_response_data():
    return json.dumps(
        {"error": "403", "error_description": "You ain't allowed, son."}
    ).encode("utf-8")


@pytest.fixture()
def response(response_data):
    return MockResponse(response_data, 200)


@pytest.fixture()
def error_response(error_response_data):
    return MockResponse(error_response_data, 403, "You ain't allowed in son.")


@pytest.fixture()
def auth_error_response(auth_error_response_data):
    return MockResponse(auth_error_response_data, 403, "You ain't allowed in son.")


# @pytest.fixture()
# def report(response_data):
#     return Report(json.loads(response_data), TimeBasedActivity())


@pytest.fixture()
def group_list_response(group_list_data):
    return MockResponse(json.dumps(group_list_data).encode("utf-8"), 200)


@pytest.fixture()
def group_item_list_response(group_item_list_data):
    return MockResponse(json.dumps(group_item_list_data).encode("utf-8"), 200)


@pytest.fixture()
def column_header_dimension():
    return ColumnHeader("day", DataType.STRING, ColumnType.DIMENSION)


@pytest.fixture()
def column_header_dimension_data():
    return {
        "name": "day",
        "dataType": "STRING",
        "columnType": "DIMENSION",
    }


@pytest.fixture()
def column_header_metric():
    return ColumnHeader("views", DataType.INTEGER, ColumnType.METRIC)


@pytest.fixture()
def column_header_metric_data():
    return {
        "name": "views",
        "dataType": "INTEGER",
        "columnType": "METRIC",
    }


@pytest.fixture()
def column_headers(column_header_dimension, column_header_metric):
    return [column_header_dimension, column_header_metric]


@pytest.fixture()
def column_headers_data(column_header_dimension_data, column_header_metric_data):
    return [column_header_dimension_data, column_header_metric_data]


@pytest.fixture()
def row_data():
    return [
        ["2022-06-20", 778],
        ["2022-06-21", 1062],
        ["2022-06-22", 946],
        ["2022-06-23", 5107],
        ["2022-06-24", 2137],
        ["2022-06-25", 1005],
        ["2022-06-26", 888],
    ]


@pytest.fixture()
def result_table(column_headers, row_data):
    return ResultTable(
        "youtubeAnalytics#resultTable",
        column_headers,
        row_data,
    )


@pytest.fixture()
def result_table_data(column_headers_data, row_data):
    return {
        "kind": "youtubeAnalytics#resultTable",
        "columnHeaders": column_headers_data,
        "rows": row_data,
    }


@pytest.fixture()
def report_type():
    return TimeBasedActivity()


@pytest.fixture()
def report(result_table_data, report_type):
    return Report(result_table_data, report_type)


@pytest.fixture()
def empty_report(result_table_data, report_type):
    result_table_data["rows"] = []
    return Report(result_table_data, report_type)


@pytest.fixture()
def report_csv():
    return """day,views
2022-06-20,778
2022-06-21,1062
2022-06-22,946
2022-06-23,5107
2022-06-24,2137
2022-06-25,1005
2022-06-26,888
"""


@pytest.fixture()
def report_tsv(report_csv):
    return report_csv.replace(",", "\t")


@pytest.fixture()
def dimensions_required() -> Dimensions:
    return Dimensions(Required("day", "month"))


@pytest.fixture()
def dimensions_exactly_one() -> Dimensions:
    return Dimensions(ExactlyOne("day", "month"))


@pytest.fixture()
def dimensions_one_or_more() -> Dimensions:
    return Dimensions(OneOrMore("day", "month"))


@pytest.fixture()
def dimensions_optional() -> Dimensions:
    return Dimensions(Optional("day", "month"))


@pytest.fixture()
def dimensions_zero_or_one() -> Dimensions:
    return Dimensions(ZeroOrOne("day", "month"))


@pytest.fixture()
def dimensions_zero_or_more() -> Dimensions:
    return Dimensions(ZeroOrMore("day", "month"))


@pytest.fixture()
def filters_required() -> Filters:
    return Filters(Required("country", "video"))


@pytest.fixture()
def filters_required_locked() -> Filters:
    return Filters(Required("country==US", "video"))


@pytest.fixture()
def filters_exactly_one() -> Filters:
    return Filters(ExactlyOne("country", "video"))


@pytest.fixture()
def filters_one_or_more() -> Filters:
    return Filters(OneOrMore("country", "video"))


@pytest.fixture()
def filters_optional() -> Filters:
    return Filters(Optional("country", "video"))


@pytest.fixture()
def filters_zero_or_one() -> Filters:
    return Filters(ZeroOrOne("country", "video"))


@pytest.fixture()
def filters_zero_or_more() -> Filters:
    return Filters(ZeroOrMore("country", "video"))


@pytest.fixture()
def metrics() -> Metrics:
    return Metrics("views", "likes", "comments")


@pytest.fixture()
def sort_options() -> SortOptions:
    return SortOptions("views", "likes", "comments")


@pytest.fixture()
def sort_options_descending() -> SortOptions:
    return SortOptions("views", "likes", "comments", descending_only=True)


@pytest.fixture()
def query() -> ReportQuery:
    return ReportQuery(
        dimensions=["day", "country"],
        filters={"continent": "002", "deviceType": "MOBILE"},
        metrics=["views", "likes", "comments"],
        sort_options=["shares", "dislikes"],
        start_date=dt.date(2021, 1, 1),
        end_date=dt.date(2021, 12, 31),
    )
