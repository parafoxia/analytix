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

import builtins
import datetime as dt
import json
import os
import shutil
import typing as t

import httpx
import mock
import pytest
import pytest_asyncio

from analytix import AsyncAnalytics
from analytix.errors import APIError, AuthenticationError
from analytix.report_types import TimeBasedActivity
from analytix.secrets import Secrets
from analytix.tokens import Tokens
from tests.paths import JSON_OUTPUT_PATH, MOCK_DATA_PATH
from tests.test_secrets import SECRETS_PATH, secrets, secrets_dict  # noqa
from tests.test_tokens import TOKENS_PATH, tokens, tokens_dict  # noqa


async def test_load_from_secrets_file(secrets_dict):
    client = await AsyncAnalytics.with_secrets(SECRETS_PATH)
    assert isinstance(client.secrets, Secrets)

    assert client.secrets.client_id == secrets_dict["client_id"]
    assert client.secrets.project_id == secrets_dict["project_id"]
    assert client.secrets.auth_uri == secrets_dict["auth_uri"]
    assert client.secrets.token_uri == secrets_dict["token_uri"]
    assert (
        client.secrets.auth_provider_x509_cert_url
        == secrets_dict["auth_provider_x509_cert_url"]
    )
    assert client.secrets.client_secret == secrets_dict["client_secret"]
    assert client.secrets.redirect_uris == secrets_dict["redirect_uris"]


async def test_load_from_non_existent_secrets_file():
    with pytest.raises(FileNotFoundError) as exc:
        await AsyncAnalytics.with_secrets(SECRETS_PATH.parent / "does-not.exist")
    assert f"{exc.value}" == "you must provided a valid path to a secrets file"


@pytest_asyncio.fixture()
async def client() -> AsyncAnalytics:
    return await AsyncAnalytics.with_secrets(SECRETS_PATH)


def test_str_output(client):
    output = "test-secrets"

    assert str(client) == output
    assert f"{client}" == output


def test_authorised_property_no_tokens(client):
    assert not client.authorised


def test_authorised_property_with_tokens(client):
    client._tokens = {"access_token": "whatever"}
    assert client.authorised


async def test_session_close(client):
    await client.close_session()
    assert client._session.is_closed


async def test_load_existing_tokens(client, tokens_dict):
    tokens = await client._try_load_tokens(TOKENS_PATH)
    assert isinstance(tokens, Tokens)
    assert tokens.access_token == tokens_dict["access_token"]
    assert tokens.expires_in == tokens_dict["expires_in"]
    assert tokens.refresh_token == tokens_dict["refresh_token"]
    assert tokens.scope == tokens_dict["scope"]
    assert tokens.token_type == tokens_dict["token_type"]


async def test_load_non_existent_tokens(client):
    tokens = await client._try_load_tokens(TOKENS_PATH.parent / "does-not.exist")
    assert tokens is None


async def test_authorise_with_tokens(client):
    with mock.patch.object(Tokens, "awrite") as mock_write:
        mock_write.return_value = None
        tokens = await client.authorise(token_path=TOKENS_PATH)
        assert isinstance(tokens, Tokens)


async def test_authorise_with_tokens_non_path_and_dir(client):
    data_dir = "./tests/data"
    token_dest = data_dir + "/tokens.json"
    token_src = data_dir + "/test_tokens.json"
    shutil.copyfile(token_src, token_dest)

    tokens = await client.authorise(token_path="./tests/data")
    assert isinstance(tokens, Tokens)
    os.remove(token_dest)


async def test_authorise_without_tokens(client, tokens_dict):
    with mock.patch.object(builtins, "input") as mock_input:
        with mock.patch.object(httpx.AsyncClient, "post") as mock_post:
            with mock.patch.object(Tokens, "awrite") as mock_write:
                mock_write.return_value = None
                mock_post.return_value = httpx.Response(
                    status_code=200, json=tokens_dict, request=mock.Mock()
                )

                tokens = await client.authorise(token_path=TOKENS_PATH, force=True)

                mock_post.assert_awaited_once()
                mock_write.assert_awaited_once()
                mock_input.assert_called_once()
                assert isinstance(tokens, Tokens)


async def test_refresh_access_tokens(client):
    with mock.patch.object(httpx.AsyncClient, "post") as mock_post:
        with mock.patch.object(Tokens, "awrite") as mock_write:
            mock_write.return_value = None
            mock_post.return_value = httpx.Response(
                status_code=200,
                request=mock.Mock(),
                json={
                    "access_token": "a",
                    "expires_in": 10000,
                    "refresh_token": "b",
                    "scope": "c",
                    "token_type": "Swearer",
                },
            )

            await client.authorise(token_path=TOKENS_PATH)
            await client.refresh_access_token()
            tokens = client._tokens

            mock_write.assert_awaited_once()
            mock_post.assert_awaited_once()

            assert tokens.access_token == "a"
            assert tokens.expires_in == 10000
            assert tokens.refresh_token == "b"
            assert tokens.scope == "c"
            assert tokens.token_type == "Swearer"


async def test_refresh_access_tokens_with_no_tokens(client, caplog):
    caplog.set_level(30)
    await client.refresh_access_token()
    assert client._tokens is None
    assert "There are no tokens to refresh" in caplog.text


async def test_retrieve_token_refresh_token_failure(client, tokens):
    with mock.patch.object(httpx.AsyncClient, "post") as mock_post:
        mock_post.return_value = httpx.Response(
            status_code=403,
            request=mock.Mock(),
            json={"error": {"code": 403, "message": "You suck"}},
        )

        client._tokens = tokens

        with mock.patch.object(builtins, "input") as mock_input:
            mock_input.return_value = "lol ecks dee"

            # If we get here, refreshing failed, and we can also test
            # retrieval failure.
            with pytest.raises(AuthenticationError) as exc:
                await client.refresh_access_token()
            assert str(exc.value) == "Authentication failure (403): You suck"


async def test_needs_refresh_with_valid(client):
    with mock.patch.object(httpx.AsyncClient, "get") as mock_get:
        mock_get.return_value = httpx.Response(
            status_code=200,
            request=mock.Mock(),
            json={"expires_in": 10000},
        )

        await client.authorise(token_path=TOKENS_PATH)
        needs_refresh = await client.needs_refresh()

        mock_get.assert_awaited_once()
        assert not needs_refresh


async def test_needs_refresh_with_invalid(client):
    with mock.patch.object(httpx.AsyncClient, "get") as mock_get:
        obj = mock.Mock()
        obj.is_error = True

        await client.authorise(token_path=TOKENS_PATH)
        needs_refresh = await client.needs_refresh()

        mock_get.assert_awaited_once()
        assert needs_refresh


async def test_needs_refresh_with_no_tokens(client):
    client._tokens = None
    needs_refresh = await client.needs_refresh()
    assert not needs_refresh


async def test_update_check(client):
    with mock.patch.object(httpx.AsyncClient, "get") as mock_get:
        mock_get.return_value = httpx.Response(
            status_code=200,
            request=mock.Mock(),
            json={"info": {"version": "9999.9.9"}},
        )

        latest = await client.check_for_updates()
        mock_get.assert_called_once()
        assert latest == "9999.9.9"


async def test_update_check_failure(client):
    with mock.patch.object(httpx.AsyncClient, "get") as mock_get:
        obj = mock.Mock()
        obj.is_error = True
        mock_get.return_value = obj

        latest = await client.check_for_updates()
        mock_get.assert_called_once()
        assert latest is None


@pytest.fixture()
def request_data():
    with open(MOCK_DATA_PATH) as f:
        return json.load(f)


async def test_retrieve(client, request_data, tokens):
    with mock.patch.object(httpx.AsyncClient, "get") as mock_get:
        client._tokens = tokens

        mock_get.return_value = httpx.Response(
            status_code=200,
            request=mock.Mock(),
            json=request_data,
        )

        report = await client.retrieve(
            dimensions=("day",),
            start_date=dt.date(2022, 1, 1),
            end_date=dt.date(2022, 1, 31),
            skip_update_check=True,
            skip_refresh_check=True,
        )
        mock_get.assert_called_once()
        assert report.data == request_data
        assert isinstance(report.type, TimeBasedActivity)


async def test_retrieve_version_check(client, request_data, tokens):
    with mock.patch.object(httpx.AsyncClient, "get") as mock_get:
        client._tokens = tokens

        mock_get.return_value = httpx.Response(
            status_code=200,
            request=mock.Mock(),
            json=request_data,
        )

        with mock.patch.object(AsyncAnalytics, "check_for_updates") as mock_check:
            mock_check.return_value == "9999.9.9"

            report = await client.retrieve(
                dimensions=("day",),
                start_date=dt.date(2022, 1, 1),
                end_date=dt.date(2022, 1, 31),
                skip_refresh_check=True,
            )
            mock_get.assert_called_once()
            assert report.data == request_data
            assert isinstance(report.type, TimeBasedActivity)


async def test_retrieve_no_validate(client, request_data, tokens):
    with mock.patch.object(httpx.AsyncClient, "get") as mock_get:
        client._tokens = tokens

        mock_get.return_value = httpx.Response(
            status_code=200,
            request=mock.Mock(),
            json=request_data,
        )

        report = await client.retrieve(
            dimensions=("day",),
            start_date=dt.date(2022, 1, 1),
            end_date=dt.date(2022, 1, 31),
            skip_validation=True,
            skip_update_check=True,
            skip_refresh_check=True,
        )
        mock_get.assert_called_once()
        assert report.data == request_data
        assert isinstance(report.type, TimeBasedActivity)


async def test_retrieve_with_refresh_check(client, request_data, tokens):
    with mock.patch.object(httpx.AsyncClient, "get") as mock_get:
        client._tokens = tokens

        mock_get.return_value = httpx.Response(
            status_code=200,
            request=mock.Mock(),
            json=request_data,
        )

        with mock.patch.object(AsyncAnalytics, "needs_refresh") as mock_check:
            mock_check.return_value = False

            report = await client.retrieve(
                dimensions=("day",),
                start_date=dt.date(2022, 1, 1),
                end_date=dt.date(2022, 1, 31),
                skip_update_check=True,
            )
            mock_get.assert_called_once()
            assert report.data == request_data
            assert isinstance(report.type, TimeBasedActivity)


@pytest.fixture()
def tokens() -> Tokens:
    return Tokens.from_file(TOKENS_PATH)


@pytest.fixture()
def tokens_dict() -> dict[str, t.Any]:
    with open(TOKENS_PATH) as f:
        data = json.load(f)

    return t.cast(t.Dict[str, t.Any], data)


async def test_retrieve_with_refresh(client, tokens, tokens_dict):
    with mock.patch.object(AsyncAnalytics, "needs_refresh") as mock_check:
        mock_check.return_value = True

        with mock.patch.object(AsyncAnalytics, "authorise") as mock_auth:
            mock_auth.return_value = tokens
            client._tokens = tokens
            client._token_path = JSON_OUTPUT_PATH

            with mock.patch.object(httpx.AsyncClient, "post") as mock_post:
                mock_post.return_value = httpx.Response(
                    status_code=200,
                    request=mock.Mock(),
                    json=tokens_dict,
                )

                # Because we are using fake credentials, this will
                # always error, so we might as well just test that now.
                with pytest.raises(APIError) as exc:
                    await client.retrieve(skip_update_check=True)
                assert (
                    str(exc.value)
                    == "API returned 401: Request had invalid authentication credentials. Expected OAuth 2 access token, login cookie or other valid authentication credential. See https://developers.google.com/identity/sign-in/web/devconsole-project."
                )

    os.remove(JSON_OUTPUT_PATH)


async def test_retrieve_with_no_authorisation(client, tokens, request_data):
    client._tokens = tokens

    with mock.patch.object(httpx.AsyncClient, "get") as mock_get:
        mock_get.return_value = httpx.Response(
            status_code=200,
            request=mock.Mock(),
            json=request_data,
        )

        with mock.patch.object(AsyncAnalytics, "authorise") as mock_auth:
            mock_auth.return_value = tokens
            await client.retrieve(
                force_authorisation=True,
                skip_refresh_check=True,
                skip_update_check=True,
            )

            mock_auth.assert_called_once()
            mock_get.assert_called_once()
