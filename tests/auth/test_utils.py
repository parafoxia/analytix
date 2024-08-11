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

from unittest import mock

from analytix.auth.scopes import Scopes
from analytix.auth.secrets import Secrets
from analytix.auth.utils import auth_uri
from analytix.auth.utils import refresh_uri
from analytix.auth.utils import state_token
from analytix.auth.utils import token_uri


def test_state_token():
    with mock.patch("os.urandom", return_value=b"rickroll"):
        assert (
            state_token()
            == "34c5f166f6abb229ee092be1e7e92ca71434bcb1a27ba0664cd2fea834d85927"
        )


def test_auth_uri_all_readonly_scopes(secrets: Secrets, auth_params):
    with mock.patch("os.urandom", return_value=b"rickroll"):
        uri, params, headers = auth_uri(secrets, Scopes.ALL_READONLY, 8080)

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


def test_auth_uri_all_readonly_scopes_legacy_secrets(
    legacy_secrets: Secrets, auth_params
):
    with mock.patch("os.urandom", return_value=b"rickroll"):
        uri, params, headers = auth_uri(legacy_secrets, Scopes.ALL_READONLY, 8080)

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
    with mock.patch("os.urandom", return_value=b"rickroll"):
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
    with mock.patch("os.urandom", return_value=b"rickroll"):
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
    with mock.patch("os.urandom", return_value=b"rickroll"):
        uri, params, headers = auth_uri(secrets, Scopes.ALL_READONLY, 80)

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
