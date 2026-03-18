# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

import datetime as dt
import json
import logging
import time
from io import StringIO
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


def test_expires_in_set_expires_at_set(caplog) -> None:
    class Tokens:
        # These tests each need different classes to avoid conflicts
        # between _ExpiresIn descriptors.
        access_token = "access_token"
        expires_in = _ExpiresIn()

    with (
        mock.patch.object(_ExpiresIn, "_expires_at", dt.datetime.now()),
        caplog.at_level(logging.DEBUG),
    ):
        Tokens().expires_in = 3600

    assert "Setting access token expiry time is not supported" in caplog.text


def test_expires_in_set_expires_at_not_set(caplog) -> None:
    class Tokens:
        # These tests each need different classes to avoid conflicts
        # between _ExpiresIn descriptors.
        access_token = "access_token"
        expires_in = _ExpiresIn()

    with (
        mock.patch.object(_ExpiresIn, "_expires_at", None),
        caplog.at_level(logging.DEBUG),
    ):
        Tokens().expires_in = 3600

    assert "Setting access token expiry time is not supported" not in caplog.text


def test_tokens_read_json_from_file(tokens: Tokens, tokens_file: MockFile) -> None:
    with mock.patch.object(Path, "open", return_value=tokens_file):
        assert Tokens.read_json("tokens_file") == tokens


def test_tokens_read_json_from_string(tokens: Tokens, tokens_json: str) -> None:
    assert Tokens.read_json(StringIO(tokens_json)) == tokens


def test_tokens_read_json_type_error() -> None:
    with pytest.raises(TypeError) as exc_info:
        Tokens.read_json(123)

    assert exc_info.value.args[0] == "Expected str, PathLike, or TextIOBase, got int"


def test_tokens_to_json_to_file(
    tokens: Tokens,
    tokens_file: MockFile,
    tokens_json: str,
) -> None:
    with mock.patch.object(Path, "open", return_value=tokens_file):
        assert tokens.to_json("tokens_file") is None
        assert tokens_file.write_data == tokens_json


def test_tokens_to_json_to_buffer(tokens: Tokens, tokens_json: str) -> None:
    f = StringIO()
    assert tokens.to_json(f) is None
    assert f.getvalue() == tokens_json


def test_tokens_to_json_to_string(tokens: Tokens, tokens_json: str) -> None:
    assert tokens.to_json() == tokens_json


def test_tokens_to_json_type_error(tokens: Tokens) -> None:
    with pytest.raises(TypeError):
        tokens.to_json(123)


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
                    },
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
