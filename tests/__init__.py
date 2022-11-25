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

from analytix import oidc


class MockFile:
    def __init__(self, data):
        self.read_data = data
        self.write_data = ""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        ...

    def read(self):
        return self.read_data

    def write(self, data):
        self.write_data = data


class MockAsyncFile:
    def __init__(self, data):
        self.read_data = data
        self.write_data = ""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        ...

    async def read(self):
        return self.read_data

    async def write(self, data):
        self.write_data = data


class MockVersionResponse:
    def __init__(self, version, ok=True):
        self.version = version
        self.ok = ok

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        ...

    async def json(self):
        return {"info": {"version": self.version}}


def create_secrets_file(other=False):
    return json.dumps(
        {
            "installed": {
                "client_id": "a1b2c3d4e5",
                "project_id": "rickroll" if not other else "barney",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "f6g7h8i9j0",
                "redirect_uris": ["http://localhost"],
            }
        }
    )


def create_secrets():
    return oidc.Secrets(
        type="installed",
        client_id="a1b2c3d4e5",
        project_id="rickroll",
        auth_uri="https://accounts.google.com/o/oauth2/auth",
        token_uri="https://oauth2.googleapis.com/token",
        auth_provider_x509_cert_url="https://www.googleapis.com/oauth2/v1/certs",
        client_secret="f6g7h8i9j0",
        redirect_uris=["http://localhost"],
    )


def create_tokens_file():
    return json.dumps(
        {
            "access_token": "a1b2c3d4e5",
            "expires_in": 3599,
            "scope": "https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
            "token_type": "Bearer",
            "refresh_token": "f6g7h8i9j0",
        }
    )


def create_tokens():
    return oidc.Tokens(
        access_token="a1b2c3d4e5",
        expires_in=3599,
        scope="https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
        token_type="Bearer",
        refresh_token="f6g7h8i9j0",
    )
