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
from unittest import mock

import pytest
import pytz

from analytix.auth import Scopes, Secrets, Tokens
from analytix.client import Client
from analytix.groups import Group, GroupItem, GroupItemList, GroupList
from analytix.queries import ReportQuery
from analytix.reports.features import (
    Dimensions,
    ExactlyOne,
    Filters,
    Metrics,
    OneOrMore,
    Optional,
    Required,
    SortOptions,
    ZeroOrMore,
    ZeroOrOne,
)
from analytix.reports.interfaces import Report
from analytix.reports.resources import ColumnHeader, ColumnType, DataType, ResultTable
from analytix.reports.types import TimeBasedActivity
from analytix.shard import Shard
from tests import CustomBaseClient, MockResponse

# AUTH


@pytest.fixture()
def secrets():
    return Secrets(
        type="installed",
        client_id="a1b2c3d4e5",
        project_id="rickroll",
        auth_uri="https://accounts.google.com/o/oauth2/auth",
        token_uri="https://oauth2.googleapis.com/token",
        auth_provider_x509_cert_url="https://www.googleapis.com/oauth2/v1/certs",
        client_secret="f6g7h8i9j0",
        redirect_uris=["http://localhost"],
    )


@pytest.fixture()
def legacy_secrets():
    return Secrets(
        type="installed",
        client_id="a1b2c3d4e5",
        project_id="rickroll",
        auth_uri="https://accounts.google.com/o/oauth2/auth",
        token_uri="https://oauth2.googleapis.com/token",
        auth_provider_x509_cert_url="https://www.googleapis.com/oauth2/v1/certs",
        client_secret="f6g7h8i9j0",
        redirect_uris=["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
    )


@pytest.fixture()
def tokens():
    return Tokens(
        access_token="a1b2c3d4e5",
        expires_in=3599,
        scope="https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
        token_type="Bearer",
        refresh_token="f6g7h8i9j0",
    )


@pytest.fixture()
def full_tokens(id_token):
    return Tokens(
        access_token="a1b2c3d4e5",
        expires_in=3599,
        scope="https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
        token_type="Bearer",
        refresh_token="f6g7h8i9j0",
        id_token=id_token,
    )


@pytest.fixture()
def refreshed_tokens():
    return Tokens(
        access_token="5e4d3c2b1a",
        expires_in=3599,
        scope="https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
        token_type="Bearer",
        refresh_token="f6g7h8i9j0",
    )


@pytest.fixture()
def public_jwks():
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
def id_token():
    return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZG1pbiI6dHJ1ZSwiaWF0IjoxNTE2MjM5MDIyLCJuYW1lIjoiQmFybmV5IHRoZSBEaW5vc2F1ciIsInN1YiI6IjEyMzQ1Njc4OTAifQ.glf1K2N9SacjpaK2W_PkqB7Ga-KwmEEpcQUFUhHmfYvd-2eWjWJN3oatXF4gkwh9O7tSqO3QW_REfpgbD-odCn3CZtZGffDEoIkujRwbr8rwnrnDK0aakspEsHBfPPctwOI6SpSqAn4LWdyK5SWzES8NnzJp6OiSXALPW92JkN9Z_pTktO1VL1IQm-NcXz3jOfqewneEkesdm8vesxd1mIeUelkKWpqg0UlT48GKZlkn08BU5GUWCLWxLj96qee4PGmfHsGb6uPx2iqL0BMI9JbKSo6MnkCmjZKwCzJdsYDYfncoDdbm3O_qUCVU4Br7T2HP3YUe-c01zwnzyXqP0A"


@pytest.fixture()
def id_token_payload():
    return {
        "admin": True,
        "iat": 1516239022,
        "name": "Barney the Dinosaur",
        "sub": "1234567890",
    }


@pytest.fixture()
def secrets_data():
    return json.dumps(
        {
            "installed": {
                "client_id": "a1b2c3d4e5",
                "project_id": "rickroll",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "f6g7h8i9j0",
                "redirect_uris": ["http://localhost"],
            }
        }
    )


@pytest.fixture()
def tokens_data():
    return json.dumps(
        {
            "access_token": "a1b2c3d4e5",
            "expires_in": 3599,
            "scope": "https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
            "token_type": "Bearer",
            "refresh_token": "f6g7h8i9j0",
        }
    )


@pytest.fixture()
def refreshed_tokens_data():
    return json.dumps(
        {
            "access_token": "5e4d3c2b1a",
            "expires_in": 3599,
            "scope": "https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
            "token_type": "Bearer",
        }
    )


@pytest.fixture()
def auth_params():
    return {
        "client_id": "a1b2c3d4e5",
        "nonce": "34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927",
        "response_type": "code",
        "redirect_uri": "http://localhost:8080",
        "scope": "https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
        "state": "34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927",
        "access_type": "offline",
    }


@pytest.fixture()
def auth_params_readonly():
    return {
        "client_id": "a1b2c3d4e5",
        "nonce": "34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927",
        "response_type": "code",
        "redirect_uri": "http://localhost:8080",
        "scope": "https://www.googleapis.com/auth/yt-analytics.readonly",
        "state": "34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927",
        "access_type": "offline",
    }


@pytest.fixture()
def auth_params_monetary_readonly():
    return {
        "client_id": "a1b2c3d4e5",
        "nonce": "34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927",
        "response_type": "code",
        "redirect_uri": "http://localhost:8080",
        "scope": "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
        "state": "34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927",
        "access_type": "offline",
    }


@pytest.fixture()
def auth_params_port_80():
    return {
        "client_id": "a1b2c3d4e5",
        "nonce": "34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927",
        "response_type": "code",
        "redirect_uri": "http://localhost",
        "scope": "https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
        "state": "34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927",
        "access_type": "offline",
    }


# GROUPS


@pytest.fixture()
def group(shard):
    return Group(
        kind="youtube#group",
        etag="f6g7h8i9j0",
        id="a1b2c3d4e5",
        published_at=dt.datetime(2022, 11, 30, 12, 34, 56, 789000, tzinfo=pytz.utc),
        title="Barney the Dinosaur",
        item_count=69,
        item_type="youtube#video",
        shard=shard,
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


# MIXINS


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


# SHARD


@pytest.fixture()
def shard(tokens: Tokens):
    return Shard(Scopes.ALL, tokens)


# @pytest.fixture()
# def report(response_data):
#     return Report(json.loads(response_data), TimeBasedActivity())


@pytest.fixture()
def group_list_response(group_list_data):
    return MockResponse(json.dumps(group_list_data).encode("utf-8"), 200)


@pytest.fixture()
def group_item_list_response(group_item_list_data):
    return MockResponse(json.dumps(group_item_list_data).encode("utf-8"), 200)


# CLIENT


@pytest.fixture()
def base_client(secrets_data):
    with mock.patch.object(Path, "read_text", return_value=secrets_data):
        # We use a subclass of BaseClient as the original has an
        # abstract method. This custom one doesn't actually implement
        # anything, but it does allow us to split client tests into two
        # separate files.
        return CustomBaseClient("secrets.json")


@pytest.fixture()
def client(secrets_data):
    with mock.patch.object(Path, "read_text", return_value=secrets_data):
        return Client("secrets.json")


# REPORTS


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


# QUERIES


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
