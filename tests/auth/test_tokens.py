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
import logging
import re
import time
from pathlib import Path
from unittest import mock

import pytest

from analytix import utils
from analytix.auth.scopes import Scopes
from analytix.auth.tokens import Tokens
from analytix.auth.tokens import _ExpiresIn
from analytix.errors import APIError
from analytix.errors import IdTokenError
from analytix.errors import MissingOptionalComponents
from tests import MockFile
from tests import MockResponse


def test_expires_in_init():
    exp = _ExpiresIn(default=3599)
    assert exp._default == 3599
    assert exp._expires_at is None


def test_expires_in_get():
    class Test:
        access_token = "a1b2c3d4e5"
        expires_in = _ExpiresIn()

    with mock.patch.object(
        _ExpiresIn,
        "_request",
        return_value=MockResponse(json.dumps({"exp": time.time() + 3600}), 200),
    ):
        assert Test().expires_in == 3599


def test_expires_in_get_invalid():
    class Test:
        access_token = "a1b2c3d4e5"
        expires_in = _ExpiresIn()

    with mock.patch.object(
        _ExpiresIn,
        "_request",
        return_value=MockResponse(json.dumps({"exp": time.time() - 3600}), 200),
    ):
        assert Test().expires_in == 0


def test_expires_in_set(caplog):
    class Test:
        access_token = "a1b2c3d4e5"
        expires_in = _ExpiresIn()

    with caplog.at_level(logging.WARNING):
        Test().expires_in = 0

    assert "Setting access token expiry time is not supported" in caplog.text


def test_expires_in_set_no_warning_default(caplog):
    class Test:
        access_token = "a1b2c3d4e5"
        expires_in = _ExpiresIn()

    with caplog.at_level(logging.WARNING):
        Test().expires_in = 3599

    assert "Setting access token expiry time is not supported" not in caplog.text


def test_tokens_str(tokens: Tokens):
    with mock.patch.object(_ExpiresIn, "__get__", return_value=3599):
        assert (
            str(tokens)
            == "Tokens(access_token='a1b2c3d4e5', scope='https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly', token_type='Bearer', refresh_token='f6g7h8i9j0', expires_in=3599, id_token=None)"
        )


def test_tokens_repr(tokens: Tokens):
    with mock.patch.object(_ExpiresIn, "__get__", return_value=3599):
        assert repr(tokens) == str(tokens)


def test_tokens_from_json(tokens: Tokens, tokens_data: str):
    with mock.patch.object(_ExpiresIn, "__get__", return_value=3599):
        assert tokens == Tokens.from_json(tokens_data)


def test_tokens_load_from(saved_tokens: Tokens, tokens_data: str, caplog):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(_ExpiresIn, "__get__", return_value=3599):
            f = MockFile(tokens_data)
            with mock.patch.object(Path, "open", return_value=f):
                assert saved_tokens == Tokens.load_from("tokens.json")

            assert "Loading tokens from" in caplog.text


def test_tokens_save_to(tokens: Tokens, tokens_data: str, caplog):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(_ExpiresIn, "__get__", return_value=3599):
            f = MockFile()
            with mock.patch.object(Path, "open", return_value=f):
                tokens.save_to("tokens.json")
                assert f.write_data == tokens_data

            assert "Saving tokens to" in caplog.text


def test_tokens_are_value_true(tokens: Tokens, caplog):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(_ExpiresIn, "__get__", return_value=3599):
            assert tokens.are_valid


def test_tokens_token_is_valid_false(tokens: Tokens, caplog):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(_ExpiresIn, "__get__", return_value=0):
            assert not tokens.are_valid


def test_tokens_are_scoped_for_readonly(tokens: Tokens, caplog):
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


@mock.patch.object(utils, "can_use", return_value=False)
def test_tokens_decoded_id_token_no_jwt(mock_can_use, full_tokens: Tokens):
    with pytest.raises(
        MissingOptionalComponents,
        match=re.escape(
            "some necessary libraries are not installed (hint: pip install jwt)"
        ),
    ):
        full_tokens.decoded_id_token


@pytest.mark.skipif(not utils.can_use("jwt"), reason="jwt is not available")
def test_tokens_decode_id_token_no_token(
    tokens: Tokens, public_jwks, id_token_payload, caplog
):
    assert tokens.decoded_id_token is None


@pytest.mark.skipif(not utils.can_use("jwt"), reason="jwt is not available")
def test_tokens_decode_id_token(
    full_tokens: Tokens, public_jwks, id_token_payload, caplog
):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(
            Tokens, "_request", return_value=MockResponse(public_jwks, 200)
        ):
            assert full_tokens.decoded_id_token == id_token_payload

        assert "Fetching JWKs" in caplog.text
        assert "Attempting decode using JWK with KID '420'"


@pytest.mark.skipif(not utils.can_use("jwt"), reason="jwt is not available")
def test_base_client_decode_id_token_cant_fetch_jwks(full_tokens: Tokens):
    with mock.patch.object(Tokens, "_request", return_value=MockResponse("", 400)):
        with pytest.raises(IdTokenError, match="could not fetch Google JWKs"):
            full_tokens.decoded_id_token


@pytest.mark.skipif(not utils.can_use("jwt"), reason="jwt is not available")
def test_base_client_decode_id_token_jws_decode_error(
    full_tokens: Tokens, public_jwks, caplog
):
    from jwt import JWT
    from jwt.exceptions import JWSDecodeError

    jwks = json.loads(public_jwks)
    jwks["keys"][0]["n"] = "rickroll"
    public_jwks = json.dumps(jwks)

    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(
            Tokens, "_request", return_value=MockResponse(public_jwks, 200)
        ):
            with mock.patch.object(JWT, "decode", side_effect=JWSDecodeError):
                with pytest.raises(
                    IdTokenError, match=re.escape("invalid ID token (see above error)")
                ):
                    full_tokens.decoded_id_token

        assert "Fetching JWKs" in caplog.text


@pytest.mark.skipif(not utils.can_use("jwt"), reason="jwt is not available")
def test_base_client_decode_id_token_decode_error(
    full_tokens: Tokens, public_jwks, caplog
):
    jwks = json.loads(public_jwks)
    jwks["keys"][0]["n"] = "rickroll"
    public_jwks = json.dumps(jwks)

    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(
            Tokens, "_request", return_value=MockResponse(public_jwks, 200)
        ):
            with pytest.raises(
                IdTokenError, match="ID token signature could not be validated"
            ):
                full_tokens.decoded_id_token

        assert "Fetching JWKs" in caplog.text
        assert "Fetching JWKs" in caplog.text
