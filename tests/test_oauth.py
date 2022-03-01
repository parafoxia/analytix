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

import re

from analytix import oauth
from tests.test_secrets import secrets  # noqa

STATE_PATTERN = re.compile("[0-9a-f]{64}")


def test_create_state():
    assert STATE_PATTERN.match(oauth.create_state())


def test_auth_url_and_state(secrets):
    url, state = oauth.auth_url_and_state(secrets)

    assert url == (
        "https://accounts.google.com/o/oauth2/auth"
        "?response_type=code"
        "&client_id=fn497gnwebg9wn98ghw8gh9"
        "&redirect_uri=urn:ietf:wg:oauth:2.0:oob"
        "&scope=https://www.googleapis.com/auth/yt-analytics.readonly+https://www.googleapis.com/auth/yt-analytics-monetary.readonly"
        f"&state={state}"
    )
    assert STATE_PATTERN.match(state)


def test_access_data_and_headers(secrets):
    code = "4ng0843ng89n340gn4028ng084n"
    data, headers = oauth.access_data_and_headers(code, secrets)

    assert data == {
        "client_id": "fn497gnwebg9wn98ghw8gh9",
        "client_secret": "gnfre09gnng094h309gn30bg98",
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
    }
    assert headers == {"Content-Type": "application/x-www-form-urlencoded"}


def test_refresh_data_and_headers(secrets):
    token = "gnu54ngp943bpg984npgbn480gb9483bg84b9g8b498pb"
    data, headers = oauth.refresh_data_and_headers(token, secrets)

    assert data == {
        "client_id": "fn497gnwebg9wn98ghw8gh9",
        "client_secret": "gnfre09gnng094h309gn30bg98",
        "grant_type": "refresh_token",
        "refresh_token": token,
    }
    assert headers == {"Content-Type": "application/x-www-form-urlencoded"}
