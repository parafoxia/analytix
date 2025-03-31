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
import secrets as secrets_mod
import time
import webbrowser
from multiprocessing.pool import ThreadPool
from pathlib import Path
from unittest import mock
from urllib.request import urlopen

import pytest

from analytix.auth.secrets import AuthContext
from analytix.auth.secrets import Scopes
from analytix.auth.secrets import Secrets
from analytix.auth.tokens import Tokens
from analytix.errors import AuthorisationError
from tests import MockFile
from tests import MockResponse


def test_auth_content_open_webbrowser_success(
    auth_context: AuthContext,
    caplog,
) -> None:
    with (
        mock.patch.object(webbrowser, "open", return_value=True) as mock_open_browser,
        caplog.at_level(logging.DEBUG),
    ):
        auth_context.open_browser()
        assert "Opening web browser" in caplog.text
        assert "Failed to open web browser" not in caplog.text

    mock_open_browser.assert_called_once_with(auth_context.auth_uri, 0, autoraise=True)


def test_auth_content_open_webbrowser_failure(
    auth_context: AuthContext,
    caplog,
) -> None:
    with (
        mock.patch.object(webbrowser, "open", return_value=False) as mock_open_browser,
        caplog.at_level(logging.DEBUG),
    ):
        auth_context.open_browser()
        assert "Opening web browser" in caplog.text
        assert "Failed to open web browser" in caplog.text

    mock_open_browser.assert_called_once_with(auth_context.auth_uri, 0, autoraise=True)


def _run_server(
    pool: ThreadPool,
    auth_context: AuthContext,
    *,
    state: str | None = None,
) -> list[str]:
    def make_request() -> str:
        time.sleep(0.1)
        return urlopen(
            f"http://localhost:8080?state={state or auth_context.state}&code=authorisationcode",
        )

    return pool.map(lambda f: f(), [auth_context.fetch_code, make_request])


def test_auth_context_fetch_code(auth_context: AuthContext, caplog) -> None:
    with caplog.at_level(logging.DEBUG):
        pool = ThreadPool(processes=2)
        res = _run_server(pool, auth_context)
        pool.close()
        pool.join()

        assert res[0] == "authorisationcode"
        assert "Received request (200)" in caplog.text
        assert "Received code: auth...code" in caplog.text


def test_auth_context_fetch_code_invalid_redirect_uri() -> None:
    auth_context = AuthContext(
        client_id="client_id",
        client_secret="client_secret",
        redirect_uri="barney-the-dinosaur",
        auth_uri="https://accounts.google.com/o/oauth2/auth",
        token_uri="https://oauth2.googleapis.com/token",
        state="token",
    )

    pool = ThreadPool(processes=2)
    with pytest.raises(AuthorisationError) as exc_info:
        _run_server(pool, auth_context)
    pool.close()
    pool.join()

    assert str(exc_info.value) == ("invalid redirect URI")


def test_auth_context_fetch_code_invalid_state(auth_context: AuthContext) -> None:
    pool = ThreadPool(processes=2)
    with pytest.raises(AuthorisationError, match="invalid state"):
        _run_server(pool, auth_context, state="invalid")
    pool.close()
    pool.join()


def test_auth_context_fetch_tokens(
    auth_context: AuthContext,
    tokens: Tokens,
    tokens_json: str,
) -> None:
    with (
        mock.patch.object(
            AuthContext,
            "_request",
            return_value=MockResponse(tokens_json, 200),
        ),
        mock.patch.object(AuthContext, "fetch_code", return_value="authorisationcode"),
    ):
        assert auth_context.fetch_tokens() == tokens


def test_auth_context_fetch_tokens_error(auth_context: AuthContext) -> None:
    with (
        mock.patch.object(
            AuthContext,
            "_request",
            return_value=MockResponse(
                json.dumps(
                    {
                        "error": "error",
                        "error_description": "error_description",
                    },
                ),
                400,
            ),
        ),
        mock.patch.object(AuthContext, "fetch_code", return_value="authorisationcode"),
        pytest.raises(AuthorisationError) as exc_info,
    ):
        auth_context.fetch_tokens()

    assert str(exc_info.value) == "could not authorise: error_description (error)"


def test_secrets_load_from(secrets: Secrets, client_secrets_file: MockFile) -> None:
    with mock.patch.object(Path, "open", return_value=client_secrets_file):
        assert Secrets.load_from("client_secrets_file", Scopes.READONLY) == secrets


def test_secrets_auth_context(secrets: Secrets, auth_context: AuthContext) -> None:
    with mock.patch.object(secrets_mod, "token_urlsafe", return_value="token"):
        with secrets.auth_context() as ctx:
            assert ctx == auth_context
