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

import json

from analytix import oidc


class MockFile:
    def __init__(self, data):
        self.read_data = data
        self.write_data = ""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        ...

    def read(self):
        return self.read_data

    def write(self, data):
        self.write_data += data


class MockAsyncFile:
    def __init__(self, data):
        self.read_data = data
        self.write_data = ""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        ...

    async def read(self):
        return self.read_data

    async def write(self, data):
        self.write_data = data


class MockResponse:
    def __init__(self, data, ok=True):
        self.data = data
        self.ok = ok
        self.status = 200 if ok else 400
        self.reason = "" if ok else "Too bad sucker!"

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        ...

    async def json(self):
        return json.loads(self.data)


def create_secrets_file(other=False):
    return json.dumps(
        {
            "installed": {
                "client_id": "a1b2c3d4e5",
                "project_id": "barney" if other else "rickroll",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "f6g7h8i9j0",
                "redirect_uris": ["http://localhost"],
            }
        }
    )


def create_secrets():
    return oidc.Secrets(
        type="installed",
        client_id="a1b2c3d4e5",
        project_id="rickroll",
        auth_uri="https://accounts.google.com/o/oauth2/auth",
        token_uri="https://oauth2.googleapis.com/token",
        auth_provider_x509_cert_url="https://www.googleapis.com/oauth2/v1/certs",
        client_secret="f6g7h8i9j0",
        redirect_uris=["http://localhost"],
    )


def create_tokens_file():
    return json.dumps(
        {
            "access_token": "a1b2c3d4e5",
            "expires_in": 3599,
            "scope": "https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
            "token_type": "Bearer",
            "refresh_token": "f6g7h8i9j0",
        }
    )


def create_tokens():
    return oidc.Tokens(
        access_token="a1b2c3d4e5",
        expires_in=3599,
        scope="https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
        token_type="Bearer",
        refresh_token="f6g7h8i9j0",
    )


def create_auth_params():
    return {
        "client_id": "a1b2c3d4e5",
        "nonce": "34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927",
        "response_type": "code",
        "redirect_uri": "http://localhost:8080",
        "scope": "https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
        "state": "34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927",
        "access_type": "offline",
    }


def create_request_data():
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
    )


def create_group_data():
    return json.dumps(
        {
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
    )


def create_group_list_data():
    return json.dumps(
        {
            "kind": "youtube#groupListResponse",
            "etag": "f6g7h8i9j0",
            "items": [json.loads(create_group_data())],
            "nextPageToken": "a1b2c3d4e5",
        }
    )


def create_group_item_data():
    return json.dumps(
        {
            "kind": "youtube#groupItem",
            "etag": "f6g7h8i9j0",
            "id": "e5d4c3b2a1",
            "groupId": "a1b2c3d4e5",
            "resource": {
                "kind": "youtube#video",
                "id": "j0i9h8g7f6",
            },
        }
    )


def create_group_item_list_data():
    return json.dumps(
        {
            "kind": "youtube#groupItemListResponse",
            "etag": "a1b2c3d4e5",
            "items": [json.loads(create_group_item_data())],
        }
    )
