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

import asyncio
import pytest

from analytix import AsyncAnalytics
from analytix.secrets import Secrets
from analytix.tokens import Tokens
from tests.test_secrets import SECRETS_PATH, secrets, secrets_dict
from tests.test_tokens import TOKENS_PATH, tokens, tokens_dict


def test_load_from_secrets_file(secrets_dict):
    client = asyncio.run(AsyncAnalytics.with_secrets(SECRETS_PATH))
    assert isinstance(client.secrets, Secrets)

    assert client.secrets.client_id == secrets_dict["client_id"]
    assert client.secrets.project_id == secrets_dict["project_id"]
    assert client.secrets.auth_uri == secrets_dict["auth_uri"]
    assert client.secrets.token_uri == secrets_dict["token_uri"]
    assert (
        client.secrets.auth_provider_x509_cert_url
        == secrets_dict["auth_provider_x509_cert_url"]
    )
    assert client.secrets.client_secret == secrets_dict["client_secret"]
    assert client.secrets.redirect_uris == secrets_dict["redirect_uris"]


def test_load_from_non_existent_secrets_file():
    with pytest.raises(FileNotFoundError) as exc:
        asyncio.run(AsyncAnalytics.with_secrets(SECRETS_PATH.parent / "does-not.exist"))
    assert f"{exc.value}" == "you must provided a valid path to a secrets file"


@pytest.fixture()
def client() -> AsyncAnalytics:
    return asyncio.run(AsyncAnalytics.with_secrets(SECRETS_PATH))


def test_str_output(client):
    output = "test-secrets"

    assert str(client) == output
    assert f"{client}" == output


def test_authorised_property_no_tokens(client):
    assert not client.authorised


def test_authorised_property_with_tokens(client):
    client._tokens = {"access_token": "whatever"}
    assert client.authorised


def test_session_close(client):
    asyncio.run(client.close_session())
    assert client._session.is_closed


def test_load_existing_tokens(client, tokens_dict):
    tokens = asyncio.run(client._try_load_tokens(TOKENS_PATH))
    assert isinstance(tokens, Tokens)
    assert tokens.access_token == tokens_dict["access_token"]
    assert tokens.expires_in == tokens_dict["expires_in"]
    assert tokens.refresh_token == tokens_dict["refresh_token"]
    assert tokens.scope == tokens_dict["scope"]
    assert tokens.token_type == tokens_dict["token_type"]


def test_load_non_existent_tokens(client):
    tokens = asyncio.run(client._try_load_tokens(TOKENS_PATH.parent / "does-not.exist"))
    assert tokens is None
