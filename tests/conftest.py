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
from analytix.reports import AnalyticsReport
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
def tokens():
    return Tokens(
        access_token="a1b2c3d4e5",
        expires_in=3599,
        scope="https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
        token_type="Bearer",
        refresh_token="f6g7h8i9j0",
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
def group():
    return Group(
        kind="youtube#group",
        etag="f6g7h8i9j0",
        id="a1b2c3d4e5",
        published_at=dt.datetime(2022, 11, 30, 12, 34, 56, 789000, tzinfo=pytz.utc),
        title="Barney the Dinosaur",
        item_count=69,
        item_type="youtube#video",
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
                {"name": "likes", "dataType": "INTEGER", "columnType": "METRIC"},
                {"name": "comments", "dataType": "INTEGER", "columnType": "METRIC"},
                {"name": "grossRevenue", "dataType": "FLOAT", "columnType": "METRIC"},
            ],
            "rows": [
                ["2022-06-20", 778, 8, 0, 2.249],
                ["2022-06-21", 1062, 32, 8, 3.558],
                ["2022-06-22", 946, 38, 6, 2.91],
                ["2022-06-23", 5107, 199, 15, 24.428],
                ["2022-06-24", 2137, 61, 2, 6.691],
                ["2022-06-25", 1005, 31, 6, 4.316],
                ["2022-06-26", 888, 12, 1, 4.206],
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


@pytest.fixture()
def report(response_data):
    return AnalyticsReport(json.loads(response_data), TimeBasedActivity())


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
