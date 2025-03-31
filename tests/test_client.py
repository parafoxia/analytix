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

import logging
from pathlib import Path
from unittest import mock
from unittest.mock import PropertyMock

import pytest

from analytix.auth.scopes import Scopes
from analytix.auth.secrets import AuthContext
from analytix.auth.secrets import Secrets
from analytix.auth.tokens import Tokens
from analytix.client import Client
from analytix.client import SessionContext
from analytix.groups.groups import GroupItemList
from analytix.groups.groups import GroupList
from analytix.queries import ReportQuery
from analytix.reports.interfaces import Report
from tests import MockContextManager
from tests import MockFile
from tests import MockResponse


def test_client_loads_secrets(client: Client, secrets: Secrets) -> None:
    assert client._secrets == secrets


def test_client_invalid_tokens_file(client_secrets_file: MockFile) -> None:
    with (
        mock.patch.object(Path, "open", return_value=client_secrets_file),
        pytest.raises(ValueError) as exc_info,
    ):
        Client("secrets.json", tokens_file="tokens.txt")

    assert str(exc_info.value) == "tokens file must be a JSON file"


def test_client_no_tokens_file(client_secrets_file: MockFile) -> None:
    with mock.patch.object(Path, "open", return_value=client_secrets_file):
        client = Client("secrets.json", tokens_file=None)
    assert client._tokens_file is None


def test_client_context_manager(client: Client) -> None:
    with client:
        assert isinstance(client, Client)


def test_client_secrets_property(client: Client, secrets: Secrets) -> None:
    assert client.secrets == secrets


def test_client_authorise_with_existing_tokens(
    client: Client,
    tokens: Tokens,
    tokens_file: MockFile,
    caplog,
) -> None:
    with (
        mock.patch.object(client, "_tokens_file", tokens_file),
        mock.patch.object(Tokens, "load_from", return_value=tokens),
        mock.patch.object(Tokens, "are_scoped_for", return_value=True),
        mock.patch.object(Tokens, "expired", PropertyMock(return_value=False)),
        mock.patch.object(Client, "refresh_tokens", return_value=tokens),
        mock.patch.object(
            Secrets,
            "auth_context",
            side_effect=RuntimeError("[side effect] failed to load existing tokens"),
        ),
        caplog.at_level(logging.DEBUG),
    ):
        assert client.authorise() == tokens
        assert "Authorisation complete!" in caplog.text


def test_client_authorise_with_existing_tokens_no_scoped(
    client: Client,
    tokens: Tokens,
    tokens_file: MockFile,
    caplog,
) -> None:
    with (
        mock.patch.object(client, "_tokens_file", tokens_file),
        mock.patch.object(Tokens, "load_from", return_value=tokens),
        mock.patch.object(Tokens, "are_scoped_for", return_value=False),
        mock.patch.object(Tokens, "expired", PropertyMock(return_value=False)),
        mock.patch.object(Client, "refresh_tokens", return_value=tokens),
        mock.patch.object(
            Secrets,
            "auth_context",
            side_effect=RuntimeError("[side effect] failed to load existing tokens"),
        ),
        caplog.at_level(logging.DEBUG),
        pytest.raises(RuntimeError) as exc_info,
    ):
        assert client.authorise() == tokens
        assert "The client needs to be authorised, starting flow..." in caplog.text

    # This is just to make sure something else isn't happening.
    assert str(exc_info.value) == "[side effect] failed to load existing tokens"


def test_client_authorise_with_existing_tokens_expired(
    client: Client,
    tokens: Tokens,
    tokens_file: MockFile,
    caplog,
) -> None:
    with (
        mock.patch.object(client, "_tokens_file", tokens_file),
        mock.patch.object(Tokens, "load_from", return_value=tokens),
        mock.patch.object(Tokens, "are_scoped_for", return_value=True),
        mock.patch.object(Tokens, "expired", PropertyMock(return_value=True)),
        mock.patch.object(Client, "refresh_tokens", return_value=None),
        mock.patch.object(
            Secrets,
            "auth_context",
            side_effect=RuntimeError("[side effect] failed to load existing tokens"),
        ),
        caplog.at_level(logging.DEBUG),
        pytest.raises(RuntimeError) as exc_info,
    ):
        assert client.authorise() == tokens
        assert "The client needs to be authorised, starting flow..." in caplog.text

    # This is just to make sure something else isn't happening.
    assert str(exc_info.value) == "[side effect] failed to load existing tokens"


def test_client_authorise_new_tokens(
    client: Client,
    auth_context: AuthContext,
    tokens: Tokens,
    tokens_file: MockFile,
    caplog,
) -> None:
    with (
        mock.patch.object(client, "_tokens_file", tokens_file),
        mock.patch.object(Tokens, "load_from", return_value=tokens),
        mock.patch.object(Tokens, "are_scoped_for", return_value=False),
        mock.patch.object(
            Secrets,
            "auth_context",
            return_value=MockContextManager(auth_context),
        ),
        mock.patch.object(AuthContext, "open_browser", return_value=True),
        mock.patch.object(AuthContext, "fetch_tokens", return_value=tokens),
        mock.patch.object(Tokens, "save_to", return_value=None) as mock_save_to,
        caplog.at_level(logging.DEBUG),
    ):
        assert client.authorise() == tokens
        mock_save_to.assert_called_once_with(client._tokens_file)

    assert "The client needs to be authorised, starting flow..." in caplog.text
    assert "Authorisation complete!" in caplog.text


def test_client_authorise_new_tokens_over_console(
    client: Client,
    auth_context: AuthContext,
    tokens: Tokens,
    tokens_file: MockFile,
    caplog,
    capfd,
) -> None:
    with (
        mock.patch.object(client, "_tokens_file", tokens_file),
        mock.patch.object(Tokens, "load_from", return_value=tokens),
        mock.patch.object(Tokens, "are_scoped_for", return_value=False),
        mock.patch.object(
            Secrets,
            "auth_context",
            return_value=MockContextManager(auth_context),
        ),
        mock.patch.object(AuthContext, "open_browser", return_value=False),
        mock.patch.object(AuthContext, "fetch_tokens", return_value=tokens),
        mock.patch.object(Tokens, "save_to", return_value=None) as mock_save_to,
        caplog.at_level(logging.DEBUG),
    ):
        assert client.authorise() == tokens
        mock_save_to.assert_called_once_with(client._tokens_file)

    assert "The client needs to be authorised, starting flow..." in caplog.text
    assert "Authorisation complete!" in caplog.text
    out, _ = capfd.readouterr()
    assert "Follow this link to authorise the client:" in out


def test_client_authorise_new_tokens_forced(
    client: Client,
    auth_context: AuthContext,
    tokens: Tokens,
    tokens_file: MockFile,
    caplog,
) -> None:
    with (
        mock.patch.object(client, "_tokens_file", tokens_file),
        mock.patch.object(
            Secrets,
            "auth_context",
            return_value=MockContextManager(auth_context),
        ),
        mock.patch.object(AuthContext, "open_browser", return_value=True),
        mock.patch.object(AuthContext, "fetch_tokens", return_value=tokens),
        mock.patch.object(Tokens, "save_to", return_value=None) as mock_save_to,
        caplog.at_level(logging.DEBUG),
    ):
        assert client.authorise(force=True) == tokens
        mock_save_to.assert_called_once_with(client._tokens_file)

    assert "The client needs to be authorised, starting flow..." in caplog.text
    assert "Authorisation complete!" in caplog.text


def test_client_refresh_tokens(client: Client, tokens: Tokens) -> None:
    with (
        mock.patch.object(Tokens, "refresh", return_value=tokens),
        mock.patch.object(Tokens, "save_to", return_value=None) as mock_save_to,
    ):
        assert client.refresh_tokens(tokens) == tokens

    mock_save_to.assert_called_once_with(client._tokens_file)


def test_client_refresh_tokens_failed(client: Client, tokens: Tokens) -> None:
    with mock.patch.object(Tokens, "refresh", return_value=None):
        assert client.refresh_tokens(tokens) == None


def test_client_session_use_existing_tokens(
    client: Client,
    tokens: Tokens,
    caplog,
) -> None:
    with caplog.at_level(logging.DEBUG):
        with client.session(tokens=tokens):
            assert client._session_ctx.access_token == tokens.access_token

        assert client._session_ctx is None

    assert "New client session created" in caplog.text


def test_client_session_create_new_tokens(
    client: Client,
    tokens: Tokens,
    caplog,
) -> None:
    with (
        caplog.at_level(logging.DEBUG),
        mock.patch.object(Client, "authorise", return_value=tokens),
    ):
        with client.session():
            assert client._session_ctx.access_token == tokens.access_token

        assert client._session_ctx is None

    assert "New client session created" in caplog.text


def test_client_fetch_report(
    client: Client,
    report: Report,
    tokens: Tokens,
    response: MockResponse,
) -> None:
    with (
        mock.patch.object(Client, "authorise", return_value=tokens),
        mock.patch.object(ReportQuery, "validate", return_value=None),
        mock.patch.object(Client, "_request", return_value=response),
    ):
        assert client.fetch_report().resource.data == report.resource.data


def test_client_fetch_groups(
    client: Client,
    tokens: Tokens,
    group_list: GroupList,
    group_list_response: MockResponse,
) -> None:
    with (
        mock.patch.object(Client, "authorise", return_value=tokens),
        mock.patch.object(Client, "_request", return_value=group_list_response),
    ):
        assert client.fetch_groups() == group_list


def test_client_fetch_group_items(
    client: Client,
    tokens: Tokens,
    group_item_list: GroupItemList,
    group_item_list_response: MockResponse,
) -> None:
    with (
        mock.patch.object(Client, "authorise", return_value=tokens),
        mock.patch.object(Client, "_request", return_value=group_item_list_response),
    ):
        assert client.fetch_group_items("1") == group_item_list
