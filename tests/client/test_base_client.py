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

import logging
from pathlib import Path
from unittest import mock

from analytix.auth import Scopes
from analytix.errors import APIError
from tests import CustomBaseClient, MockResponse


def test_base_client_init(base_client: CustomBaseClient, secrets):
    assert base_client._secrets == secrets
    assert base_client._scopes == Scopes.READONLY


def test_base_client_context_manager(base_client: CustomBaseClient, secrets_data):
    with mock.patch.object(Path, "read_text", return_value=secrets_data):
        with CustomBaseClient("secrets.json") as client:
            assert client._scopes == base_client._scopes


def test_base_client_token_is_valid_true(base_client: CustomBaseClient, caplog):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(
            CustomBaseClient, "_request", return_value=MockResponse("", 200)
        ):
            assert base_client.token_is_valid("rickroll")

        assert "Access token does not need refreshing" in caplog.text


def test_base_client_token_is_valid_false(base_client: CustomBaseClient, caplog):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(
            CustomBaseClient, "_request", side_effect=APIError(400, "token is dead son")
        ):
            assert not base_client.token_is_valid("rickroll")

        assert "Access token needs refreshing" in caplog.text


def test_base_client_refresh_access_token_success(
    base_client: CustomBaseClient, tokens, refreshed_tokens_data, caplog
):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(
            CustomBaseClient,
            "_request",
            return_value=MockResponse(refreshed_tokens_data, 200),
        ):
            refreshed = base_client.refresh_access_token(tokens)
            assert refreshed.access_token == "5e4d3c2b1a"
            assert refreshed.refresh_token == "f6g7h8i9j0"

        assert "Access token has been refreshed successfully" in caplog.text


def test_base_client_refresh_access_token_failure(
    base_client: CustomBaseClient, tokens, caplog
):
    with caplog.at_level(logging.DEBUG):
        with mock.patch.object(
            CustomBaseClient, "_request", return_value=MockResponse("", 400)
        ):
            assert not base_client.refresh_access_token(tokens)

        assert "Access token could not be refreshed" in caplog.text


def test_base_client_shard_no_scopes(base_client: CustomBaseClient, tokens):
    with base_client.shard(tokens) as shard:
        assert shard._tokens.access_token == tokens.access_token
        assert shard._scopes == Scopes.READONLY


def test_base_client_shard_with_scopes(base_client: CustomBaseClient, tokens):
    with base_client.shard(tokens, scopes=Scopes.ALL) as shard:
        assert shard._tokens.access_token == tokens.access_token
        assert shard._scopes == Scopes.ALL
