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

from __future__ import annotations

import datetime as dt
import json
import sys
from asyncio import AbstractEventLoop
from pathlib import Path

import pytest
import pytz
from aiohttp import ClientSession

from analytix import AsyncClient, Client, oidc
from analytix.errors import AuthorisationError, RefreshTokenExpired
from analytix.groups import Group, GroupItem, GroupItemList, GroupList
from analytix.reports import AnalyticsReport
from analytix.reports.types import TimeBasedActivity
from analytix.shard import Shard
from tests import (
    MockAsyncFile,
    MockResponse,
    create_auth_params,
    create_group_item_data,
    create_group_item_list_data,
    create_group_list_data,
    create_request_data,
    create_secrets,
    create_secrets_file,
    create_tokens,
    create_tokens_file,
)

if sys.version_info >= (3, 8):
    from unittest import mock
else:
    import mock


@pytest.fixture()
@mock.patch("builtins.open", mock.mock_open(read_data=create_secrets_file()))
def client():
    return Client("secrets.json")


@pytest.fixture()
@mock.patch("builtins.open", mock.mock_open(read_data=create_secrets_file()))
def shard_client(client: Client):
    client._shard = Shard(client._session, client._secrets, create_tokens())
    client._active_tokens = "sandstorm"
    return client


def test_client_init(client: Client):
    assert isinstance(client._loop, AbstractEventLoop)
    assert client._secrets == create_secrets()
    assert isinstance(client._session, ClientSession)

    assert client._tokens_dir == Path(".")
    assert client._ws_port == 8080
    assert client._auto_open_browser == False
    assert not client._active_tokens
    assert not client._shard


@mock.patch("builtins.open", mock.mock_open(read_data=create_secrets_file()))
def test_client_init_tokens_dir_as_file():
    with pytest.raises(
        NotADirectoryError, match="the token directory must not be a file"
    ):
        Client("secrets.json", tokens_dir="./tokens.json")


def test_client_str(client: Client):
    assert str(client) == "rickroll"
    assert f"{client}" == "rickroll"


def test_client_repr(client: Client):
    assert repr(client) == "Client(project_id='rickroll')"
    assert f"{client!r}" == "Client(project_id='rickroll')"


def test_client_eq(client: Client):
    with mock.patch("builtins.open", mock.mock_open(read_data=create_secrets_file())):
        print(repr(client), repr(Client("secrets.json")))
        assert client == Client("secrets.json")

    with mock.patch(
        "builtins.open", mock.mock_open(read_data=create_secrets_file(other=True))
    ):
        print(repr(client), repr(Client("secrets.json")))
        assert not client == Client("secrets.json")

    assert not client == create_secrets()


def test_client_ne(client: Client):
    with mock.patch("builtins.open", mock.mock_open(read_data=create_secrets_file())):
        assert not client != Client("secrets.json")

    with mock.patch(
        "builtins.open", mock.mock_open(read_data=create_secrets_file(other=True))
    ):
        assert client != Client("secrets.json")

    assert client != create_secrets()


@pytest.mark.dependency()
def test_client_teardown(client: Client):
    assert not client._session.closed
    client.teardown()
    assert client._session.closed


@pytest.mark.dependency(depends=["test_client_teardown"])
@mock.patch("builtins.open", mock.mock_open(read_data=create_secrets_file()))
def test_client_context_manager(client: Client):
    with Client("secrets.json") as other:
        assert client == other
        assert not other._session.closed

    assert other._session.closed


def test_client_active_tokens_property(client: Client):
    assert client.active_tokens == client._active_tokens
    assert not client.active_tokens


# def test_client_get_existing_tokens_when_active(shard_client: Client):
#     assert shard_client._get_existing_tokens("sandstorm") == create_tokens()


# def test_client_get_existing_tokens_when_no_tokens_dir(client: Client):
#     client._tokens_dir = None
#     assert not client._get_existing_tokens("sandstorm")


# def test_client_get_existing_tokens_no_existing_file(client: Client):
#     assert not client._get_existing_tokens("sandstorm")


# @mock.patch("aiofiles.open")
# @mock.patch.object(Path, "exists", return_value=True)
# def test_client_get_existing_tokens_existing_file(_, mock_open, client: Client):
#     mock_open.return_value = MockAsyncFile(create_tokens_file())
#     client._tokens_dir = Path("./tokens")
#     assert client._get_existing_tokens("sandstorm") == create_tokens()


@mock.patch.object(AsyncClient, "_get_existing_tokens", return_value=create_tokens())
@mock.patch.object(Shard, "refresh_access_token", return_value=False)
def test_client_authenticate_existing_tokens_no_refresh(_, __, client: Client, caplog):
    client.authorise("sandstorm")
    assert client._shard == Shard(client._session, client._secrets, create_tokens())
    assert client.active_tokens == "sandstorm"
    assert "Authorisation complete!" in caplog.text


@mock.patch.object(AsyncClient, "_get_existing_tokens", return_value=create_tokens())
@mock.patch.object(Shard, "refresh_access_token", return_value=True)
@mock.patch("aiofiles.open")
def test_client_authenticate_existing_tokens_with_refresh(
    mock_open, _, __, client: Client, caplog
):
    f = MockAsyncFile(create_tokens_file())
    mock_open.return_value = f

    client.authorise("sandstorm")

    assert client._shard == Shard(client._session, client._secrets, create_tokens())
    assert client.active_tokens == "sandstorm"
    assert "Authorisation complete!" in caplog.text
    assert f.write_data == create_tokens_file()


@pytest.mark.dependency()
@mock.patch.object(AsyncClient, "_get_existing_tokens", return_value=None)
@mock.patch.object(oidc, "authenticate", return_value="barney")
@mock.patch.object(
    ClientSession, "post", return_value=MockResponse(create_tokens_file())
)
@mock.patch("os.urandom", return_value=b"rickroll")
@mock.patch("aiofiles.open")
def test_client_authenticate_auth_flow(
    mock_open, _, __, ___, ____, client: Client, caplog
):
    f = MockAsyncFile(create_tokens_file())
    mock_open.return_value = f

    client.authorise("sandstorm")

    data = {
        "code": "barney",
        "client_id": "a1b2c3d4e5",
        "client_secret": "f6g7h8i9j0",
        "redirect_uri": "http://localhost:8080",
        "grant_type": "authorization_code",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    assert f"Auth parameters: {create_auth_params()}" in caplog.text
    assert "Auth code: barney" in caplog.text
    assert f"Token data: {data} / Token headers: {headers}" in caplog.text
    assert f"Tokens: {create_tokens_file()}"

    assert client._shard == Shard(client._session, client._secrets, create_tokens())
    assert f.write_data == create_tokens_file()
    assert client.active_tokens == "sandstorm"
    assert "Authorisation complete!" in caplog.text


@pytest.mark.dependency(depends=["test_client_authenticate_auth_flow"])
@mock.patch.object(AsyncClient, "_get_existing_tokens", return_value=create_tokens())
@mock.patch.object(
    Shard,
    "refresh_access_token",
    side_effect=RefreshTokenExpired("your refresh token has expired"),
)
@mock.patch.object(oidc, "authenticate", return_value="barney")
@mock.patch.object(
    ClientSession,
    "post",
    return_value=MockResponse(
        '{"error": "rick_roll", "error_description": "You gave up."}', ok=False
    ),
)
@mock.patch("os.urandom", return_value=b"rickroll")
@mock.patch("aiofiles.open")
def test_client_authenticate_auth_flow_request_not_ok(
    mock_open, _, __, ___, ____, _____, client: Client, caplog
):
    with pytest.raises(
        AuthorisationError, match=r"could not authorise: You gave up. \(rick_roll\)"
    ):
        client.authorise("sandstorm")


@pytest.mark.dependency(depends=["test_client_authenticate_auth_flow"])
@mock.patch.object(AsyncClient, "_get_existing_tokens", return_value=create_tokens())
@mock.patch.object(
    Shard,
    "refresh_access_token",
    side_effect=RefreshTokenExpired("your refresh token has expired"),
)
@mock.patch.object(oidc, "authenticate", return_value="barney")
@mock.patch.object(
    ClientSession, "post", return_value=MockResponse(create_tokens_file())
)
@mock.patch("os.urandom", return_value=b"rickroll")
@mock.patch("aiofiles.open")
def test_client_authenticate_auth_flow_refresh_token_expired(
    mock_open, _, __, ___, ____, _____, client: Client, caplog
):
    client.authorise("sandstorm")
    assert "Refresh token expired, starting auth flow" in caplog.text

    # We don't need to check everything else.
    assert "Authorisation complete!" in caplog.text


@pytest.mark.dependency(depends=["test_client_authenticate_auth_flow"])
@mock.patch.object(AsyncClient, "_get_existing_tokens", return_value=None)
@mock.patch.object(oidc, "authenticate", return_value="barney")
@mock.patch.object(
    ClientSession, "post", return_value=MockResponse(create_tokens_file())
)
@mock.patch("os.urandom", return_value=b"rickroll")
@mock.patch("webbrowser.open", return_value=True)
@mock.patch("aiofiles.open")
def test_client_authenticate_auth_flow_open_browser(
    mock_open, mock_wb, __, ___, ____, _____, client: Client, caplog
):
    client._auto_open_browser = True
    client.authorise("sandstorm")

    # If it gets to this point, it works fine.
    assert "Authorisation complete!" in caplog.text


@pytest.mark.dependency(depends=["test_client_authenticate_auth_flow"])
@mock.patch.object(AsyncClient, "_get_existing_tokens", return_value=None)
@mock.patch.object(oidc, "authenticate", return_value="barney")
@mock.patch.object(
    ClientSession, "post", return_value=MockResponse(create_tokens_file())
)
@mock.patch("os.urandom", return_value=b"rickroll")
@mock.patch("webbrowser.open", return_value=False)
@mock.patch("aiofiles.open")
def test_client_authenticate_auth_flow_open_browser_fails(
    mock_open, mock_wb, __, ___, ____, _____, client: Client, caplog
):
    client._auto_open_browser = True

    with pytest.raises(
        RuntimeError,
        match="web browser failed to open — if you use WSL, refer to the docs",
    ):
        client.authorise("sandstorm")


@mock.patch.object(
    ClientSession, "get", return_value=MockResponse(create_request_data())
)
@mock.patch.object(AsyncClient, "authorise", return_value=None)
def test_client_retrieve_report(_, __, shard_client: AsyncClient, caplog):
    assert shard_client.retrieve_report(
        dimensions=("day",),
        metrics=("views", "likes", "comments", "grossRevenue"),
        start_date=dt.date(2022, 6, 20),
        end_date=dt.date(2022, 6, 26),
    ) == AnalyticsReport(json.loads(create_request_data()), TimeBasedActivity())
    assert "Created report of shape (7, 5)!" in caplog.text


@mock.patch.object(
    ClientSession, "get", return_value=MockResponse(create_group_list_data())
)
@mock.patch.object(AsyncClient, "authorise", return_value=None)
def test_client_fetch_groups(_, __, shard_client: AsyncClient):
    assert shard_client.fetch_groups() == GroupList(
        kind="youtube#groupListResponse",
        etag="f6g7h8i9j0",
        items=[
            Group(
                kind="youtube#group",
                etag="f6g7h8i9j0",
                id="a1b2c3d4e5",
                published_at=dt.datetime(
                    2022, 11, 30, 12, 34, 56, 789000, tzinfo=pytz.utc
                ),
                title="Barney the Dinosaur",
                item_count=69,
                item_type="youtube#video",
            )
        ],
        next_page_token="a1b2c3d4e5",
    )


@mock.patch.object(
    ClientSession, "get", return_value=MockResponse(create_group_item_list_data())
)
@mock.patch.object(AsyncClient, "authorise", return_value=None)
def test_client_fetch_group_items(_, __, shard_client: AsyncClient):
    assert shard_client.fetch_group_items("a1b2c3d4e5") == GroupItemList(
        kind="youtube#groupItemListResponse",
        etag="a1b2c3d4e5",
        items=[GroupItem.from_json(json.loads(create_group_item_data()))],
    )