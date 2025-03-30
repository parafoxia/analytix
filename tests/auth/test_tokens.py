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
import time
from pathlib import Path
from unittest import mock

import pytest
from jwt import JWT
from jwt.exceptions import JWSDecodeError

from analytix import utils
from analytix.auth.scopes import Scopes
from analytix.auth.secrets import Secrets
from analytix.auth.tokens import Tokens
from analytix.auth.tokens import _ExpiresIn
from analytix.errors import IdTokenError
from analytix.errors import MissingOptionalComponents
from tests import MockFile
from tests import MockResponse


@pytest.mark.parametrize("expires_in", [(3600, 3599), (0, 0), (-3600, 0)])
def test_expires_in_get(expires_in: tuple[int, int]) -> None:
    class Tokens:
        # These tests each need different classes to avoid conflicts
        # between _ExpiresIn descriptors.
        access_token = "access_token"
        expires_in = _ExpiresIn()

    with mock.patch.object(
        _ExpiresIn,
        "_request",
        return_value=MockResponse(
            json.dumps({"exp": time.time() + expires_in[0]}),
            200,
        ),
    ):
        assert int(Tokens().expires_in) == expires_in[1]


def test_tokens_load_from(tokens: Tokens, tokens_file: MockFile) -> None:
    tokens._path = Path("tokens_file")
    assert Tokens.load_from("tokens_file") == tokens


def test_tokens_from_json(tokens: Tokens, tokens_json: str) -> None:
    assert Tokens.from_json(tokens_json) == tokens


def test_tokens_save_to(
    tokens: Tokens,
    tokens_file: MockFile,
    tokens_json: str,
) -> None:
    tokens.save_to("tokens_file")
    assert tokens_file.write_data == tokens_json


def test_tokens_refresh(tokens: Tokens, secrets: Secrets, caplog) -> None:
    with (
        caplog.at_level(logging.DEBUG),
        mock.patch.object(
            Tokens,
            "_request",
            return_value=MockResponse(
                json.dumps(
                    {
                        "access_token": "new_access_token",
                        "expires_in": 3600,
                        "scope": "scope",
                        "token_type": "token_type",
                    }
                ),
                200,
            ),
        ),
    ):
        assert tokens.refresh(secrets)
        assert tokens.access_token == "new_access_token"
        assert tokens.scope == "scope"
        assert tokens.token_type == "token_type"
        assert "Access token has been refreshed successfully" in caplog.text


def test_tokens_refresh_failure(tokens: Tokens, secrets: Secrets, caplog) -> None:
    with (
        caplog.at_level(logging.DEBUG),
        mock.patch.object(
            Tokens,
            "_request",
            return_value=MockResponse("{}", 400),
        ),
    ):
        assert not tokens.refresh(secrets)
        assert "Access token could not be refreshed" in caplog.text


def test_tokens_expired(tokens: Tokens) -> None:
    with mock.patch.object(_ExpiresIn, "__get__", return_value=0):
        assert tokens.expired


def test_tokens_not_expired(tokens: Tokens) -> None:
    with mock.patch.object(_ExpiresIn, "__get__", return_value=3599):
        assert not tokens.expired


def test_tokens_are_scoped_for_readonly(tokens: Tokens, caplog) -> None:
    tokens.scope = "https://www.googleapis.com/auth/yt-analytics.readonly"

    with caplog.at_level(logging.DEBUG):
        assert tokens.are_scoped_for(Scopes.READONLY)
        assert "Stored scopes are sufficient" in caplog.text

    with caplog.at_level(logging.DEBUG):
        assert not tokens.are_scoped_for(Scopes.MONETARY_READONLY)
        assert "Stored scopes are insufficient" in caplog.text

    with caplog.at_level(logging.DEBUG):
        assert not tokens.are_scoped_for(Scopes.ALL_READONLY)
        assert "Stored scopes are insufficient" in caplog.text


def test_tokens_are_scoped_for_monetary_readonly(tokens: Tokens, caplog):
    tokens.scope = "https://www.googleapis.com/auth/yt-analytics-monetary.readonly"

    with caplog.at_level(logging.DEBUG):
        assert not tokens.are_scoped_for(Scopes.READONLY)
        assert "Stored scopes are insufficient" in caplog.text

    with caplog.at_level(logging.DEBUG):
        assert tokens.are_scoped_for(Scopes.MONETARY_READONLY)
        assert "Stored scopes are sufficient" in caplog.text

    with caplog.at_level(logging.DEBUG):
        assert not tokens.are_scoped_for(Scopes.ALL_READONLY)
        assert "Stored scopes are insufficient" in caplog.text


def test_tokens_are_scoped_for_all_readonly(tokens: Tokens, caplog):
    tokens.scope = "https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly"

    with caplog.at_level(logging.DEBUG):
        assert tokens.are_scoped_for(Scopes.READONLY)
        assert "Stored scopes are sufficient" in caplog.text

    with caplog.at_level(logging.DEBUG):
        assert tokens.are_scoped_for(Scopes.MONETARY_READONLY)
        assert "Stored scopes are sufficient" in caplog.text

    with caplog.at_level(logging.DEBUG):
        assert tokens.are_scoped_for(Scopes.ALL_READONLY)
        assert "Stored scopes are sufficient" in caplog.text


def test_tokens_decoded_id_token_no_id_token(tokens: Tokens) -> None:
    tokens.id_token = None
    assert tokens.decoded_id_token == None


def test_tokens_decoded_id_token_no_jwt(tokens: Tokens) -> None:
    with (
        mock.patch.object(utils, "can_use", return_value=False),
        pytest.raises(MissingOptionalComponents) as exc_info,
    ):
        tokens.decoded_id_token

    assert (
        str(exc_info.value)
        == "some necessary libraries are not installed (hint: pip install jwt)"
    )


def test_tokens_decoded_id_token(
    tokens: Tokens,
    public_jwks: str,
    id_token: str,
    id_token_payload: dict,
    caplog,
) -> None:
    tokens.id_token = id_token
    with (
        caplog.at_level(logging.DEBUG),
        mock.patch.object(
            Tokens,
            "_request",
            return_value=MockResponse(public_jwks, 200),
        ),
    ):
        assert tokens.decoded_id_token == id_token_payload

    assert "Fetching JWKs" in caplog.text
    assert "Attempting decode using JWK with KID '420'"


def test_tokens_decoded_id_token_cant_fetch_jwks(tokens: Tokens) -> None:
    with (
        mock.patch.object(Tokens, "_request", return_value=MockResponse("", 400)),
        pytest.raises(IdTokenError) as exc_info,
    ):
        tokens.decoded_id_token

    assert str(exc_info.value) == "could not fetch Google JWKs"


def test_tokens_decoded_id_token_jws_decode_error(
    tokens: Tokens,
    public_jwks: str,
    caplog,
) -> None:
    jwks = json.loads(public_jwks)
    jwks["keys"][0]["n"] = "rickroll"
    public_jwks = json.dumps(jwks)

    with (
        caplog.at_level(logging.DEBUG),
        mock.patch.object(
            Tokens,
            "_request",
            return_value=MockResponse(public_jwks, 200),
        ),
        mock.patch.object(JWT, "decode", side_effect=JWSDecodeError),
        pytest.raises(IdTokenError) as exc_info,
    ):
        tokens.decoded_id_token

    assert str(exc_info.value) == "invalid ID token (see above error)"
    assert "Fetching JWKs" in caplog.text


def test_tokens_decoded_id_token_decode_error(
    tokens: Tokens,
    public_jwks: str,
    caplog,
) -> None:
    jwks = json.loads(public_jwks)
    jwks["keys"][0]["n"] = "rickroll"
    public_jwks = json.dumps(jwks)

    with (
        caplog.at_level(logging.DEBUG),
        mock.patch.object(
            Tokens,
            "_request",
            return_value=MockResponse(public_jwks, 200),
        ),
        pytest.raises(IdTokenError) as exc_info,
    ):
        tokens.decoded_id_token

    assert str(exc_info.value) == "ID token signature could not be validated"
    assert "Fetching JWKs" in caplog.text
