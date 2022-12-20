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

from __future__ import annotations

import asyncio
import json
import sys
from asyncio import AbstractEventLoop
from os import _Environ

import pytest
from aiohttp import ClientSession

from analytix import AsyncBaseClient
from tests import (
    MockResponse,
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
@mock.patch("builtins.open", mock.mock_open(read_data=create_secrets_file()))
async def client():
    return AsyncBaseClient("secrets.json")


def test_client_init(client: AsyncBaseClient):
    assert isinstance(client._loop, AbstractEventLoop)
    assert client._secrets == create_secrets()
    assert isinstance(client._session, ClientSession)


async def test_client_str(client: AsyncBaseClient):
    assert str(client) == "rickroll"
    assert f"{client}" == "rickroll"


async def test_client_repr(client: AsyncBaseClient):
    assert repr(client) == "AsyncBaseClient(project_id='rickroll')"
    assert f"{client!r}" == "AsyncBaseClient(project_id='rickroll')"


@pytest.mark.dependency()
async def test_client_eq(client: AsyncBaseClient):
    with mock.patch("builtins.open", mock.mock_open(read_data=create_secrets_file())):
        assert client == AsyncBaseClient("secrets.json")

    with mock.patch(
        "builtins.open", mock.mock_open(read_data=create_secrets_file(other=True))
    ):
        assert not client == AsyncBaseClient("secrets.json")

    assert not client == create_secrets()


@pytest.mark.dependency()
async def test_client_ne(client: AsyncBaseClient):
    with mock.patch("builtins.open", mock.mock_open(read_data=create_secrets_file())):
        assert not client != AsyncBaseClient("secrets.json")

    with mock.patch(
        "builtins.open", mock.mock_open(read_data=create_secrets_file(other=True))
    ):
        assert client != AsyncBaseClient("secrets.json")

    assert client != create_secrets()


@pytest.mark.dependency(depends=["test_client_eq"])
@mock.patch("asyncio.get_running_loop", side_effect=RuntimeError())
@mock.patch("builtins.open", mock.mock_open(read_data=create_secrets_file()))
async def test_client_loop_runtime_error_handling(_, client: AsyncBaseClient):
    # Only the running_loop mock actually gets passed in for some
    # reason, but I spose it doesn't matter here.
    assert client == AsyncBaseClient("secrets.json")


@pytest.mark.dependency()
async def test_client_teardown(client: AsyncBaseClient):
    assert not client._session.closed
    await client.teardown()
    assert client._session.closed


@pytest.mark.dependency(depends=["test_client_teardown"])
@mock.patch("builtins.open", mock.mock_open(read_data=create_secrets_file()))
async def test_client_context_manager(client: AsyncBaseClient):
    async with AsyncBaseClient("secrets.json") as other:
        assert client == other
        assert not other._session.closed

    assert other._session.closed


@pytest.mark.dependency()
@mock.patch.object(
    ClientSession,
    "get",
    return_value=MockResponse('{"info": {"version": "0.69.420"}}'),
)
async def test_client_check_for_updates(_, client: AsyncBaseClient, caplog):
    await client._check_for_updates()
    assert (
        "You do not have the latest stable version of analytix (v0.69.420)"
        in caplog.text
    )


@pytest.mark.dependency(depends=["test_client_check_for_updates"])
@mock.patch.object(_Environ, "get", return_value=False)
@mock.patch.object(
    ClientSession,
    "get",
    return_value=MockResponse('{"info": {"version": "0.69.420"}}'),
)
@mock.patch("builtins.open", mock.mock_open(read_data=create_secrets_file()))
async def test_client_check_for_updates_on_init(_, __, caplog):
    AsyncBaseClient("secrets.json")
    await asyncio.sleep(0.1)
    assert (
        "You do not have the latest stable version of analytix (v0.69.420)"
        in caplog.text
    )


@mock.patch.object(
    ClientSession,
    "get",
    return_value=MockResponse('{"info": {"version": "0.69.420"}}', ok=False),
)
async def test_client_check_for_updates_failed(_, client: AsyncBaseClient, caplog):
    await client._check_for_updates()
    assert "Failed to get version information" in caplog.text


async def test_client_shard_with_tokens(client: AsyncBaseClient):
    with client.shard(create_tokens()) as shard:
        assert shard._session == client._session
        assert shard._secrets == client._secrets
        assert shard._tokens == create_tokens()


async def test_client_shard_with_json(client: AsyncBaseClient):
    with client.shard(json.loads(create_tokens_file())) as shard:
        assert shard._session == client._session
        assert shard._secrets == client._secrets
        assert shard._tokens == create_tokens()
