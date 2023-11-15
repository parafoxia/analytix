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
import logging
import re
from pathlib import Path
from unittest import mock

import pytest

from analytix import auth
from analytix.auth import Scopes, Tokens
from analytix.client import BaseClient, Client
from analytix.errors import AuthorisationError
from analytix.reports import Report
from analytix.shard import Shard
from tests import MockFile, MockResponse


def test_client_init(client: Client, secrets):
    assert client._secrets == secrets
    assert client._scopes == Scopes.READONLY


def test_client_init_bad_tokens_file(secrets_data):
    with mock.patch.object(Path, "read_text", return_value=secrets_data):
        with pytest.raises(ValueError, match="tokens file must be a JSON file"):
            Client("secrets.json", tokens_file="tokens")


@mock.patch("platform.uname", return_value=mock.Mock(release="microsoft-standard"))
def test_client_init_wsl(mock_uname, secrets_data):
    with mock.patch.object(Path, "read_text", return_value=secrets_data):
        client = Client("secrets.json")
        assert not client._auto_open_browser


@mock.patch("platform.uname", return_value=mock.Mock(release="22.6.0"))
def test_client_init_non_wsl(mock_uname, secrets_data):
    with mock.patch.object(Path, "read_text", return_value=secrets_data):
        client = Client("secrets.json")
        assert client._auto_open_browser


def test_client_context_manager(client: Client, secrets_data):
    with mock.patch.object(Path, "read_text", return_value=secrets_data):
        with Client("secrets.json") as client:
            assert client._scopes == client._scopes


@mock.patch("os.fspath", return_value="tokens.json")
def test_client_authorise_with_existing(
    mock_fspath, client: Client, tokens, tokens_data, caplog
):
    with caplog.at_level(logging.INFO):
        f = MockFile(tokens_data)
        client._tokens_file = f

        with mock.patch.object(Path, "open", return_value=f):
            with mock.patch.object(Client, "refresh_access_token", return_value=tokens):
                auth_tokens = client.authorise()
                assert auth_tokens.access_token == tokens.access_token

        assert "Existing tokens are valid -- no authorisation necessary" in caplog.text


@mock.patch.object(Tokens, "save_to", return_value=None)
@mock.patch.object(auth, "run_flow", return_value="rickroll")
@mock.patch("webbrowser.open", return_value=True)
@mock.patch("os.fspath", return_value="tokens.json")
def test_client_authorise_with_existing_forced(
    mock_fspath,
    mock_webbrowser_open,
    mock_run_flow,
    mock_save_to,
    client: Client,
    tokens,
    tokens_data,
    caplog,
):
    with caplog.at_level(logging.DEBUG):
        f = MockFile(tokens_data)
        client._tokens_file = f

        with mock.patch.object(Path, "open", return_value=f) as mock_file_open:
            with mock.patch.object(
                Client, "_request", return_value=MockResponse(tokens_data, 200)
            ):
                client._auto_open_browser = True
                tokens = client.authorise(force=True)
                assert tokens.access_token == "a1b2c3d4e5"

            assert (
                "Authorisation necessary -- starting authorisation flow" in caplog.text
            )
            assert "Authorisation code: rickroll" in caplog.text
            assert "Authorisation complete!" in caplog.text
            mock_file_open.assert_not_called()


@mock.patch.object(Tokens, "save_to", return_value=None)
@mock.patch.object(auth, "run_flow", return_value="rickroll")
@mock.patch("webbrowser.open", return_value=True)
@mock.patch.object(Client, "scopes_are_sufficient", return_value=False)
@mock.patch("os.fspath", return_value="tokens.json")
def test_client_authorise_with_existing_scopes_insufficient(
    mock_fspath,
    mock_scopes_are_sufficient,
    mock_open,
    mock_run_flow,
    mock_save_to,
    client: Client,
    tokens,
    tokens_data,
    caplog,
):
    with caplog.at_level(logging.DEBUG):
        f = MockFile(tokens_data)
        client._tokens_file = f

        with mock.patch.object(Path, "open", return_value=f):
            with mock.patch.object(
                Client, "_request", return_value=MockResponse(tokens_data, 200)
            ):
                client._auto_open_browser = True
                tokens = client.authorise()
                assert tokens.access_token == "a1b2c3d4e5"

            assert (
                "Authorisation necessary -- starting authorisation flow" in caplog.text
            )
            assert "Authorisation code: rickroll" in caplog.text
            assert "Authorisation complete!" in caplog.text


@mock.patch.object(Tokens, "save_to", return_value=None)
@mock.patch.object(auth, "run_flow", return_value="rickroll")
@mock.patch("webbrowser.open", return_value=True)
@mock.patch.object(Path, "is_file", return_value=False)
def test_client_authorise_from_scratch_auto_open_success(
    mock_is_file,
    mock_open,
    mock_run_flow,
    mock_save_to,
    client: Client,
    tokens_data,
    caplog,
):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(
            Client, "_request", return_value=MockResponse(tokens_data, 200)
        ):
            client._auto_open_browser = True
            tokens = client.authorise()
            assert tokens.access_token == "a1b2c3d4e5"

        assert "Authorisation necessary -- starting authorisation flow" in caplog.text
        assert "Authorisation code: rickroll" in caplog.text
        assert "Authorisation complete!" in caplog.text


@mock.patch.object(Tokens, "save_to", return_value=None)
@mock.patch.object(auth, "run_flow", return_value="rickroll")
@mock.patch("webbrowser.open", return_value=False)
@mock.patch.object(Path, "is_file", return_value=False)
def test_client_authorise_from_scratch_auto_open_failure(
    mock_is_file,
    mock_open,
    mock_run_flow,
    mock_save_to,
    client: Client,
    tokens_data,
    caplog,
):
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(RuntimeError, match="web browser failed to open"):
            client.authorise()

        assert "Authorisation necessary -- starting authorisation flow" in caplog.text


@mock.patch.object(Tokens, "save_to", return_value=None)
@mock.patch.object(auth, "run_flow", return_value="rickroll")
@mock.patch.object(Path, "is_file", return_value=False)
def test_client_authorise_from_scratch_console(
    mock_is_file,
    mock_run_flow,
    mock_save_to,
    client: Client,
    tokens_data,
    caplog,
    capsys,
):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(
            Client, "_request", return_value=MockResponse(tokens_data, 200)
        ):
            client._auto_open_browser = False
            tokens = client.authorise()
            assert tokens.access_token == "a1b2c3d4e5"

        assert "Authorisation necessary -- starting authorisation flow" in caplog.text
        assert "Authorisation code: rickroll" in caplog.text
        assert "Authorisation complete!" in caplog.text

        captured = capsys.readouterr()
        assert "You need to authorise analytix." in captured.out


@mock.patch.object(Tokens, "save_to", return_value=None)
@mock.patch.object(auth, "run_flow", return_value="rickroll")
@mock.patch("webbrowser.open", return_value=True)
@mock.patch.object(Path, "is_file", return_value=False)
def test_client_authorise_from_scratch_console_bad_request(
    mock_is_file,
    mock_open,
    mock_run_flow,
    mock_save_to,
    client: Client,
    tokens_data,
    auth_error_response,
    caplog,
    capsys,
):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(Client, "_request", return_value=auth_error_response):
            with pytest.raises(
                AuthorisationError,
                match=re.escape("could not authorise: You ain't allowed, son. (403)"),
            ):
                client.authorise()

        assert "Authorisation necessary -- starting authorisation flow" in caplog.text
        assert "Authorisation code: rickroll" in caplog.text


@mock.patch.object(Client, "token_is_valid", return_value=True)
def test_client_refresh_access_token_dont_force_valid_tokens(
    mock_token_is_valid, client: Client, tokens
):
    assert tokens.access_token == client.refresh_access_token(tokens).access_token


@mock.patch.object(Tokens, "save_to", return_value=None)
@mock.patch.object(Client, "token_is_valid", return_value=False)
def test_client_refresh_access_token_dont_force_invalid_tokens(
    mock_token_is_valid, mock_save_to, client: Client, tokens, refreshed_tokens
):
    with mock.patch.object(
        BaseClient, "refresh_access_token", return_value=refreshed_tokens
    ):
        refreshed = client.refresh_access_token(tokens)
        assert refreshed.access_token == refreshed_tokens.access_token


@mock.patch.object(Tokens, "save_to", return_value=None)
@mock.patch.object(Client, "token_is_valid", return_value=True)
def test_client_refresh_access_token_force_valid_tokens(
    mock_token_is_valid, mock_save_to, client: Client, tokens, refreshed_tokens
):
    with mock.patch.object(
        BaseClient, "refresh_access_token", return_value=refreshed_tokens
    ):
        refreshed = client.refresh_access_token(tokens, force=True)
        assert refreshed.access_token == refreshed_tokens.access_token


def test_client_fetch_report(client: Client, tokens, report: Report):
    with mock.patch.object(Client, "authorise", return_value=tokens):
        with mock.patch.object(Shard, "fetch_report", return_value=report):
            report = client.fetch_report(
                dimensions=("day",),
                metrics=("views", "likes", "comments", "grossRevenue"),
                start_date=dt.date(2022, 6, 20),
                end_date=dt.date(2022, 6, 26),
            )

            assert report.shape == (7, 2)


def test_client_fetch_groups(client: Client, tokens, group_list):
    with mock.patch.object(Client, "authorise", return_value=tokens):
        with mock.patch.object(Shard, "fetch_groups", return_value=group_list):
            groups = client.fetch_groups()
            assert len(groups.items) == 1


def test_client_fetch_group_items(client: Client, tokens, group, group_item_list):
    with mock.patch.object(Client, "authorise", return_value=tokens):
        with mock.patch.object(
            Shard, "fetch_group_items", return_value=group_item_list
        ):
            group_items = client.fetch_group_items(group.id)
            assert len(group_items.items) == 1
