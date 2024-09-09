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
import secrets
import time
from functools import partial
from multiprocessing.pool import ThreadPool
from pathlib import Path
from unittest import mock
from urllib.request import urlopen

import pytest

from analytix.auth import Scopes
from analytix.auth import Secrets
from analytix.auth import Tokens
from analytix.auth import auth_uri
from analytix.auth import refresh_uri
from analytix.auth import run_flow
from analytix.auth import state_token
from analytix.auth import token_uri
from analytix.errors import AuthorisationError
from tests import MockFile


def test_scopes_formatting_readonly():
    assert (
        Scopes.READONLY.formatted
        == "https://www.googleapis.com/auth/yt-analytics.readonly"
    )


def test_scopes_formatting_monetary_readonly():
    assert (
        Scopes.MONETARY_READONLY.formatted
        == "https://www.googleapis.com/auth/yt-analytics-monetary.readonly"
    )


def test_scopes_formatting_all():
    assert (
        Scopes.ALL.formatted
        == "https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly"
    )


def test_scopes_formatting_openid():
    assert Scopes.OPENID.formatted == "openid"


def test_scopes_formatting_profile():
    assert (
        Scopes.PROFILE.formatted == "https://www.googleapis.com/auth/userinfo.profile"
    )


def test_scopes_formatting_email():
    assert Scopes.EMAIL.formatted == "https://www.googleapis.com/auth/userinfo.email"


def test_scopes_formatting_all_jwt():
    assert (
        Scopes.ALL_JWT.formatted
        == "openid https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email"
    )


def test_scopes_validate_valid():
    Scopes.READONLY.validate()
    Scopes.MONETARY_READONLY.validate()
    Scopes.ALL.validate()
    (Scopes.READONLY | Scopes.OPENID).validate()


def test_scopes_validate_invalid():
    with pytest.raises(
        AuthorisationError,
        match="the READONLY or MONETARY_READONLY scope must be provided",
    ):
        Scopes.OPENID.validate()

    with pytest.raises(
        AuthorisationError,
        match="the READONLY or MONETARY_READONLY scope must be provided",
    ):
        Scopes.PROFILE.validate()

    with pytest.raises(
        AuthorisationError,
        match="the READONLY or MONETARY_READONLY scope must be provided",
    ):
        Scopes.EMAIL.validate()

    with pytest.raises(
        AuthorisationError,
        match="the READONLY or MONETARY_READONLY scope must be provided",
    ):
        Scopes.ALL_JWT.validate()


def test_secrets_str(secrets: Secrets):
    assert (
        str(secrets)
        == "Secrets(type='installed', client_id='a1b2c3d4e5', project_id='rickroll', auth_uri='https://accounts.google.com/o/oauth2/auth', token_uri='https://oauth2.googleapis.com/token', auth_provider_x509_cert_url='https://www.googleapis.com/oauth2/v1/certs', client_secret='f6g7h8i9j0', redirect_uris=['http://localhost'])"
    )


def test_secrets_repr(secrets: Secrets):
    assert repr(secrets) == str(secrets)


def test_secrets_load_from(secrets: Secrets, secrets_data: str, caplog):
    with caplog.at_level(logging.DEBUG):
        f = MockFile(secrets_data)
        with mock.patch.object(Path, "open", return_value=f):
            assert secrets == Secrets.load_from("secrets.json")

        assert "Loading secrets from" in caplog.text


def test_tokens_str(tokens: Tokens):
    assert (
        str(tokens)
        == "Tokens(access_token='a1b2c3d4e5', expires_in=3599, scope='https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly', token_type='Bearer', refresh_token='f6g7h8i9j0', id_token=None)"
    )


def test_tokens_repr(tokens: Tokens):
    assert repr(tokens) == str(tokens)


def test_tokens_from_json(tokens: Tokens, tokens_data: str):
    assert tokens == Tokens.from_json(tokens_data)


def test_tokens_load_from(tokens: Tokens, tokens_data: str, caplog):
    with caplog.at_level(logging.DEBUG):
        f = MockFile(tokens_data)
        with mock.patch.object(Path, "open", return_value=f):
            assert tokens == Tokens.load_from("tokens.json")

        assert "Loading tokens from" in caplog.text


def test_tokens_save_to(tokens: Tokens, tokens_data: str, caplog):
    with caplog.at_level(logging.DEBUG):
        f = MockFile()
        with mock.patch.object(Path, "open", return_value=f):
            tokens.save_to("tokens.json")
            assert f.write_data == tokens_data

        assert "Saving tokens to" in caplog.text


def test_tokens_refresh(tokens: Tokens):
    tokens.refresh(json.dumps({"access_token": "f6g7h8i9j0"}))
    assert tokens.access_token == "f6g7h8i9j0"


def test_state_token():
    with mock.patch(
        "secrets.token_hex",
        return_value="34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927",
    ):
        assert (
            state_token()
            == "34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927"
        )


def test_auth_uri_all_scopes(secrets: Secrets, auth_params):
    with mock.patch(
        "secrets.token_hex",
        return_value="34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927",
    ):
        uri, params, headers = auth_uri(secrets, Scopes.ALL, 8080)

    assert uri == (
        "https://accounts.google.com/o/oauth2/auth"
        "?client_id=a1b2c3d4e5"
        "&nonce=34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927"
        "&response_type=code"
        "&redirect_uri=http%3A%2F%2Flocalhost%3A8080"
        "&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyt-analytics.readonly+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyt-analytics-monetary.readonly"
        "&state=34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927"
        "&access_type=offline"
    )
    assert params == auth_params
    assert headers == {}


def test_auth_uri_all_scopes_legacy_secrets(legacy_secrets: Secrets, auth_params):
    with mock.patch(
        "secrets.token_hex",
        return_value="34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927",
    ):
        uri, params, headers = auth_uri(legacy_secrets, Scopes.ALL, 8080)

    assert uri == (
        "https://accounts.google.com/o/oauth2/auth"
        "?client_id=a1b2c3d4e5"
        "&nonce=34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927"
        "&response_type=code"
        "&redirect_uri=http%3A%2F%2Flocalhost%3A8080"
        "&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyt-analytics.readonly+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyt-analytics-monetary.readonly"
        "&state=34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927"
        "&access_type=offline"
    )
    assert params == auth_params
    assert headers == {}


def test_auth_uri_readonly_scope(secrets: Secrets, auth_params_readonly):
    with mock.patch(
        "secrets.token_hex",
        return_value="34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927",
    ):
        uri, params, headers = auth_uri(secrets, Scopes.READONLY, 8080)

    assert uri == (
        "https://accounts.google.com/o/oauth2/auth"
        "?client_id=a1b2c3d4e5"
        "&nonce=34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927"
        "&response_type=code"
        "&redirect_uri=http%3A%2F%2Flocalhost%3A8080"
        "&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyt-analytics.readonly"
        "&state=34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927"
        "&access_type=offline"
    )
    assert params == auth_params_readonly
    assert headers == {}


def test_auth_uri_monetary_scopes(secrets: Secrets, auth_params_monetary_readonly):
    with mock.patch(
        "secrets.token_hex",
        return_value="34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927",
    ):
        uri, params, headers = auth_uri(secrets, Scopes.MONETARY_READONLY, 8080)

    assert uri == (
        "https://accounts.google.com/o/oauth2/auth"
        "?client_id=a1b2c3d4e5"
        "&nonce=34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927"
        "&response_type=code"
        "&redirect_uri=http%3A%2F%2Flocalhost%3A8080"
        "&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyt-analytics-monetary.readonly"
        "&state=34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927"
        "&access_type=offline"
    )
    assert params == auth_params_monetary_readonly
    assert headers == {}


def test_auth_uri_port_80(secrets: Secrets, auth_params_port_80):
    with mock.patch(
        "secrets.token_hex",
        return_value="34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927",
    ):
        uri, params, headers = auth_uri(secrets, Scopes.ALL, 80)

    assert uri == (
        "https://accounts.google.com/o/oauth2/auth"
        "?client_id=a1b2c3d4e5"
        "&nonce=34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927"
        "&response_type=code"
        "&redirect_uri=http%3A%2F%2Flocalhost"
        "&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyt-analytics.readonly+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyt-analytics-monetary.readonly"
        "&state=34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927"
        "&access_type=offline"
    )
    assert params == auth_params_port_80
    assert headers == {}


def test_token_uri(secrets: Secrets, auth_params):
    uri, data, headers = token_uri(secrets, "rickroll", auth_params["redirect_uri"])
    assert uri == "https://oauth2.googleapis.com/token"
    assert data == {
        "code": "rickroll",
        "client_id": "a1b2c3d4e5",
        "client_secret": "f6g7h8i9j0",
        "redirect_uri": "http://localhost:8080",
        "grant_type": "authorization_code",
    }
    assert headers == {"Content-Type": "application/x-www-form-urlencoded"}


def test_refresh_uri(secrets: Secrets):
    uri, data, headers = refresh_uri(secrets, "f6g7h8i9j0")
    assert uri == "https://oauth2.googleapis.com/token"
    assert data == {
        "client_id": "a1b2c3d4e5",
        "client_secret": "f6g7h8i9j0",
        "refresh_token": "f6g7h8i9j0",
        "grant_type": "refresh_token",
    }
    assert headers == {"Content-Type": "application/x-www-form-urlencoded"}


def test_run_flow(auth_params, caplog):
    auth_params["redirect_uri"] = f"http://localhost:8081"

    def req():
        # Sleeping for a tick makes sure the server is set up before a
        # request is made to it.
        time.sleep(0.1)
        url = f"http://localhost:8081?state=34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927&code=a1b2c3d4e5"
        urlopen(url)

    with caplog.at_level(logging.DEBUG):
        pool = ThreadPool(processes=2)
        res = pool.map(lambda f: f(), [partial(run_flow, auth_params), req])
        pool.close()
        pool.join()

        assert res[0] == "a1b2c3d4e5"
        assert "Received request (200)" in caplog.text


def test_run_flow_invalid_url(auth_params, caplog):
    auth_params["redirect_uri"] = "barney_the_dinosaur"

    def req():
        # Sleeping for a tick makes sure the server is set up before a
        # request is made to it.
        time.sleep(0.1)
        url = "http://localhost:8082?state=34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927&code=a1b2c3d4e5"
        urlopen(url)

    with caplog.at_level(logging.DEBUG):
        pool = ThreadPool(processes=2)
        with pytest.raises(AuthorisationError, match="invalid redirect URI"):
            pool.map(lambda f: f(), [partial(run_flow, auth_params), req])
        pool.close()
        pool.join()


def test_run_flow_invalid_state(auth_params, caplog):
    auth_params["redirect_uri"] = f"http://localhost:8083"

    def req():
        # Sleeping for a tick makes sure the server is set up before a
        # request is made to it.
        time.sleep(0.1)
        url = "http://localhost:8083?state=rickroll&code=a1b2c3d4e5"
        urlopen(url)

    with caplog.at_level(logging.DEBUG):
        pool = ThreadPool(processes=2)
        with pytest.raises(AuthorisationError, match="invalid state"):
            pool.map(lambda f: f(), [partial(run_flow, auth_params), req])
        pool.close()
        pool.join()
