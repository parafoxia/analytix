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
import logging
import re
from pathlib import Path
from unittest import mock

import pytest

from analytix import utils
from analytix.auth import Scopes, Tokens
from analytix.client import Client
from analytix.errors import APIError, IdTokenError, MissingOptionalComponents
from tests import CustomBaseClient, MockResponse


def test_base_client_init(base_client: CustomBaseClient, secrets):
    assert base_client._secrets == secrets
    assert base_client._scopes == Scopes.READONLY


def test_base_client_context_manager(base_client: CustomBaseClient, secrets_data):
    with mock.patch.object(Path, "read_text", return_value=secrets_data):
        with CustomBaseClient("secrets.json") as client:
            assert client._scopes == base_client._scopes


def test_base_client_token_is_valid_true(base_client: CustomBaseClient, caplog):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(
            CustomBaseClient, "_request", return_value=MockResponse("", 200)
        ):
            assert base_client.token_is_valid("rickroll")

        assert "Access token does not need refreshing" in caplog.text


def test_base_client_token_is_valid_false(base_client: CustomBaseClient, caplog):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(
            CustomBaseClient, "_request", side_effect=APIError(400, "token is dead son")
        ):
            assert not base_client.token_is_valid("rickroll")

        assert "Access token needs refreshing" in caplog.text


def test_base_client_scopes_are_sufficient_readonly(
    base_client: CustomBaseClient, caplog
):
    with caplog.at_level(logging.DEBUG):
        assert base_client.scopes_are_sufficient(Scopes.READONLY.formatted)
        assert base_client.scopes_are_sufficient(Scopes.ALL.formatted)
        assert "Stored scopes are sufficient" in caplog.text

        assert not base_client.scopes_are_sufficient(Scopes.MONETARY_READONLY.formatted)
        assert "Stored scopes are insufficient" in caplog.text


def test_base_client_scopes_are_sufficient_monetary_readonly(
    base_client: CustomBaseClient, caplog
):
    with caplog.at_level(logging.DEBUG):
        base_client._scopes = Scopes.MONETARY_READONLY

        assert base_client.scopes_are_sufficient(Scopes.MONETARY_READONLY.formatted)
        assert base_client.scopes_are_sufficient(Scopes.ALL.formatted)
        assert "Stored scopes are sufficient" in caplog.text

        assert not base_client.scopes_are_sufficient(Scopes.READONLY.formatted)
        assert "Stored scopes are insufficient" in caplog.text


def test_base_client_scopes_are_sufficient_all(base_client: CustomBaseClient, caplog):
    with caplog.at_level(logging.DEBUG):
        base_client._scopes = Scopes.ALL

        assert base_client.scopes_are_sufficient(Scopes.ALL.formatted)
        assert "Stored scopes are sufficient" in caplog.text

        assert not base_client.scopes_are_sufficient(Scopes.READONLY.formatted)
        assert not base_client.scopes_are_sufficient(Scopes.MONETARY_READONLY.formatted)
        assert "Stored scopes are insufficient" in caplog.text


@mock.patch.object(utils, "can_use", return_value=False)
def test_base_client_decode_id_token_no_jwt(
    mock_can_use, base_client: Client, full_tokens: Tokens
):
    with pytest.raises(
        MissingOptionalComponents,
        match=re.escape(
            "some necessary libraries are not installed (hint: pip install jwt)"
        ),
    ):
        base_client.decode_id_token(full_tokens.id_token)


@pytest.mark.skipif(not utils.can_use("jwt"), reason="jwt is not available")
def test_base_client_decode_id_token(
    base_client: Client, full_tokens: Tokens, public_jwks, id_token_payload
):
    with mock.patch.object(
        CustomBaseClient, "_request", return_value=MockResponse(public_jwks, 200)
    ):
        assert base_client.decode_id_token(full_tokens.id_token) == id_token_payload


@pytest.mark.skipif(not utils.can_use("jwt"), reason="jwt is not available")
def test_base_client_decode_id_token(
    base_client: Client, full_tokens: Tokens, public_jwks, id_token_payload, caplog
):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(
            CustomBaseClient, "_request", return_value=MockResponse(public_jwks, 200)
        ):
            assert base_client.decode_id_token(full_tokens.id_token) == id_token_payload

        assert "Fetching JWKs" in caplog.text
        assert "Attempting decode using JWK with KID '420'"


@pytest.mark.skipif(not utils.can_use("jwt"), reason="jwt is not available")
def test_base_client_decode_id_token_cant_fetch_jwks(
    base_client: Client, full_tokens: Tokens
):
    with mock.patch.object(
        CustomBaseClient, "_request", return_value=MockResponse("", 400)
    ):
        with pytest.raises(IdTokenError, match="could not fetch Google JWKs"):
            base_client.decode_id_token(full_tokens.id_token)


@pytest.mark.skipif(not utils.can_use("jwt"), reason="jwt is not available")
def test_base_client_decode_id_token_decode_error(
    base_client: Client, full_tokens: Tokens, public_jwks, caplog
):
    jwks = json.loads(public_jwks)
    jwks["keys"][0]["n"] = "rickroll"
    public_jwks = json.dumps(jwks)

    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(
            CustomBaseClient, "_request", return_value=MockResponse(public_jwks, 200)
        ):
            with pytest.raises(
                IdTokenError, match="ID token signature could not be validated"
            ):
                base_client.decode_id_token(full_tokens.id_token)

        assert "Fetching JWKs" in caplog.text
        assert "Attempting decode using JWK with KID '420'"


@pytest.mark.skipif(not utils.can_use("jwt"), reason="jwt is not available")
def test_base_client_decode_id_token_invalid_type(
    base_client: Client, full_tokens: Tokens, public_jwks, caplog
):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(
            CustomBaseClient, "_request", return_value=MockResponse(public_jwks, 200)
        ):
            with pytest.raises(
                IdTokenError, match=re.escape("invalid ID token (see above error)")
            ):
                base_client.decode_id_token(full_tokens)

        assert "Fetching JWKs" in caplog.text
        assert "Attempting decode using JWK with KID '420'"


def test_base_client_refresh_access_token_success(
    base_client: CustomBaseClient, tokens, refreshed_tokens_data, caplog
):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(
            CustomBaseClient,
            "_request",
            return_value=MockResponse(refreshed_tokens_data, 200),
        ):
            refreshed = base_client.refresh_access_token(tokens)
            assert refreshed.access_token == "5e4d3c2b1a"
            assert refreshed.refresh_token == "f6g7h8i9j0"

        assert "Access token has been refreshed successfully" in caplog.text


def test_base_client_refresh_access_token_failure(
    base_client: CustomBaseClient, tokens, caplog
):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(
            CustomBaseClient, "_request", return_value=MockResponse("", 400)
        ):
            assert not base_client.refresh_access_token(tokens)

        assert "Access token could not be refreshed" in caplog.text


def test_base_client_shard_no_scopes(base_client: CustomBaseClient, tokens):
    with base_client.shard(tokens) as shard:
        assert shard._tokens.access_token == tokens.access_token
        assert shard._scopes == Scopes.READONLY


def test_base_client_shard_with_scopes(base_client: CustomBaseClient, tokens):
    with base_client.shard(tokens, scopes=Scopes.ALL) as shard:
        assert shard._tokens.access_token == tokens.access_token
        assert shard._scopes == Scopes.ALL
