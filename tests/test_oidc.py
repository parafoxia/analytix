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
import sys
import time
from functools import partial
from multiprocessing.pool import ThreadPool
from urllib import request

import pytest

from analytix import oidc
from analytix.errors import AuthorisationError
from tests import (
    MockAsyncFile,
    create_auth_params,
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
def secrets_file():
    return create_secrets_file()


@pytest.fixture()
def secrets():
    return create_secrets()


def test_secrets_str(secrets: oidc.Secrets):
    assert str(secrets) == secrets.project_id
    assert str(secrets) == "rickroll"


def test_secrets_repr(secrets: oidc.Secrets):
    assert (
        repr(secrets)
        == "Secrets(type='installed', client_id='a1b2c3d4e5', project_id='rickroll', auth_uri='https://accounts.google.com/o/oauth2/auth', token_uri='https://oauth2.googleapis.com/token', auth_provider_x509_cert_url='https://www.googleapis.com/oauth2/v1/certs', client_secret='f6g7h8i9j0', redirect_uris=['http://localhost'])"
    )


def test_secrets_getitem(secrets: oidc.Secrets):
    assert secrets.type == secrets["type"]
    assert secrets.client_id == secrets["client_id"]
    assert secrets.project_id == secrets["project_id"]
    assert secrets.auth_uri == secrets["auth_uri"]
    assert secrets.token_uri == secrets["token_uri"]
    assert secrets.auth_provider_x509_cert_url == secrets["auth_provider_x509_cert_url"]
    assert secrets.client_secret == secrets["client_secret"]
    assert secrets.redirect_uris == secrets["redirect_uris"]


@mock.patch("builtins.open", mock.mock_open(read_data=create_secrets_file()))
def test_secrets_from_file(secrets: oidc.Secrets):
    assert secrets == oidc.Secrets.from_file("secrets.json")


def test_secrets_to_dict(secrets: oidc.Secrets, secrets_file):
    assert secrets.to_dict() == json.loads(secrets_file)


@pytest.fixture()
def tokens_file():
    return create_tokens_file()


@pytest.fixture()
def tokens():
    return create_tokens()


def test_tokens_repr(tokens: oidc.Tokens):
    assert (
        repr(tokens)
        == "Tokens(access_token='a1b2c3d4e5', expires_in=3599, scope='https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly', token_type='Bearer', refresh_token='f6g7h8i9j0')"
    )


def test_tokens_getitem(tokens: oidc.Tokens):
    assert tokens.access_token == tokens["access_token"]
    assert tokens.expires_in == tokens["expires_in"]
    assert tokens.scope == tokens["scope"]
    assert tokens.token_type == tokens["token_type"]
    assert tokens.refresh_token == tokens["refresh_token"]


def test_tokens_from_dict(tokens: oidc.Tokens, tokens_file):
    assert tokens.from_dict(json.loads(tokens_file))


@mock.patch("aiofiles.open")
async def test_tokens_from_file(mock_open, tokens: oidc.Tokens, tokens_file):
    mock_open.return_value = MockAsyncFile(tokens_file)
    assert tokens == await oidc.Tokens.from_file("tokens.json")


def test_tokens_to_dict(tokens: oidc.Tokens, tokens_file):
    assert tokens.to_dict() == json.loads(tokens_file)


def test_tokens_update(tokens: oidc.Tokens):
    tokens.update({"expires_in": 1000})
    assert tokens.expires_in == 1000


@mock.patch("aiofiles.open")
async def test_tokens_write(mock_open, tokens: oidc.Tokens, tokens_file):
    f = MockAsyncFile(tokens_file)
    mock_open.return_value = f
    await tokens.write("tokens.json")
    assert f.write_data == tokens_file


@pytest.fixture()
def auth_params():
    return create_auth_params()


@pytest.mark.dependency()
@mock.patch("os.urandom", return_value=b"rickroll")
def test_state_token(mock_urand):
    assert (
        oidc.state_token()
        == "34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927"
    )


@pytest.mark.dependency(depends=["test_state_token"])
@mock.patch("os.urandom", return_value=b"rickroll")
def test_auth_uri(mock_urand, secrets, auth_params):
    uri, params = oidc.auth_uri(secrets, 8080)
    # We don't need to test Python's URL encoder.
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


def test_token_uri(secrets, auth_params):
    uri, data, headers = oidc.token_uri(secrets, "rickroll", auth_params)
    assert uri == "https://oauth2.googleapis.com/token"
    assert data == {
        "code": "rickroll",
        "client_id": "a1b2c3d4e5",
        "client_secret": "f6g7h8i9j0",
        "redirect_uri": "http://localhost:8080",
        "grant_type": "authorization_code",
    }
    assert headers == {"Content-Type": "application/x-www-form-urlencoded"}


def test_refresh_uri(secrets):
    uri, data, headers = oidc.refresh_uri(secrets, "f6g7h8i9j0")
    assert uri == "https://oauth2.googleapis.com/token"
    assert data == {
        "client_id": "a1b2c3d4e5",
        "client_secret": "f6g7h8i9j0",
        "refresh_token": "f6g7h8i9j0",
        "grant_type": "refresh_token",
    }
    assert headers == {"Content-Type": "application/x-www-form-urlencoded"}


def test_authentication(auth_params, caplog):
    def req():
        # Sleeping for a tick makes sure the server is set up before a
        # request is made to it.
        time.sleep(0.1)
        url = "http://localhost:8080?state=34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927&code=a1b2c3d4e5"
        request.urlopen(url)

    pool = ThreadPool(processes=2)
    res = pool.map(lambda f: f(), [partial(oidc.authenticate, auth_params), req])
    pool.close()
    pool.join()

    assert res[0] == "a1b2c3d4e5"
    assert "Received request (200)" in caplog.text


def test_authentication_invalid_uri(auth_params):
    auth_params["redirect_uri"] = "barney_the_dinosaur"

    def req():
        time.sleep(0.1)
        url = "http://localhost:8080?state=34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927&code=a1b2c3d4e5"
        request.urlopen(url)

    pool = ThreadPool(processes=2)
    with pytest.raises(AuthorisationError, match="invalid redirect URI"):
        pool.map(lambda f: f(), [partial(oidc.authenticate, auth_params), req])
    pool.close()
    pool.join()


def test_authentication_invalid_state(auth_params):
    def req():
        time.sleep(0.1)
        url = "http://localhost:8080?state=f6g7h8i9j0&code=a1b2c3d4e5"
        request.urlopen(url)

    pool = ThreadPool(processes=2)
    with pytest.raises(AuthorisationError, match="invalid state"):
        pool.map(lambda f: f(), [partial(oidc.authenticate, auth_params), req])
    pool.close()
    pool.join()
