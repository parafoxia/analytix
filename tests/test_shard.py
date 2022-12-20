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

import datetime as dt
import json
import sys

import pytest
import pytz
from aiohttp import ClientSession

from analytix.errors import APIError, RefreshTokenExpired
from analytix.groups import Group, GroupItem, GroupItemList, GroupList
from analytix.reports import AnalyticsReport
from analytix.reports.types import TimeBasedActivity
from analytix.shard import Shard
from tests import (
    MockResponse,
    create_group_item_data,
    create_group_item_list_data,
    create_group_list_data,
    create_request_data,
    create_secrets,
    create_tokens,
    create_tokens_file,
)

if sys.version_info >= (3, 8):
    from unittest import mock
else:
    import mock

ERROR_DATA = r"""{"error": {"code": 403, "message": "You ain't allowed, son."}}"""


@pytest.fixture()
async def shard():
    return Shard(
        _session=ClientSession(), _secrets=create_secrets(), _tokens=create_tokens()
    )


def test_shard_str(shard):
    assert str(shard) == "rickroll"
    assert f"{shard}" == "rickroll"


def test_shard_repr(shard):
    assert repr(shard) == "Shard(project_id='rickroll')"
    assert f"{shard!r}" == "Shard(project_id='rickroll')"


@mock.patch.object(
    ClientSession, "get", return_value=MockResponse(create_request_data())
)
async def test_shard_request(_, shard: Shard, caplog):
    assert await shard._request("https://rickroll.com") == json.loads(
        create_request_data()
    )
    assert "Response data" in caplog.text


@mock.patch.object(
    ClientSession, "get", return_value=MockResponse(create_request_data(), ok=False)
)
async def test_shard_request_api_error(_, shard: Shard):
    with pytest.raises(APIError, match="API returned 400: Too bad sucker!"):
        await shard._request("https://rickroll.com")


@mock.patch.object(ClientSession, "get", return_value=MockResponse(ERROR_DATA))
async def test_shard_request_request_error(_, shard: Shard):
    with pytest.raises(APIError, match="API returned 403: You ain't allowed, son."):
        await shard._request("https://rickroll.com")


@mock.patch.object(ClientSession, "get", return_value=MockResponse(""))
async def test_shard_token_refreshed_not_required(_, shard: Shard, caplog):
    assert not await shard.token_refresh_required()
    assert "Access token does not need refreshing" in caplog.text


@mock.patch.object(ClientSession, "get", return_value=MockResponse("", ok=False))
async def test_shard_token_refreshed_is_required(_, shard: Shard):
    assert await shard.token_refresh_required()
    assert "Access token needs refreshing"


@mock.patch.object(
    ClientSession, "post", return_value=MockResponse(create_tokens_file())
)
async def test_shard_refresh_access_token(_, shard: Shard, caplog):
    tokens = await shard.refresh_access_token()
    assert tokens == shard._tokens == create_tokens()
    assert "Refreshing access token" in caplog.text
    assert "Refreshed tokens" in caplog.text
    assert "Refresh complete!" in caplog.text


@mock.patch.object(Shard, "token_refresh_required", return_value=False)
async def test_shard_refresh_access_token_check_and_not_necessary(_, shard: Shard):
    assert not await shard.refresh_access_token(check=True)


@mock.patch.object(
    ClientSession, "post", return_value=MockResponse(create_tokens_file(), ok=False)
)
async def test_shard_refresh_access_token_expired(_, shard: Shard, caplog):
    with pytest.raises(RefreshTokenExpired, match="your refresh token has expired"):
        await shard.refresh_access_token()

    assert "Refreshing access token" in caplog.text
    assert "Refreshed tokens" in caplog.text


@mock.patch.object(
    ClientSession, "get", return_value=MockResponse(create_request_data())
)
async def test_shard_retrieve_report(_, shard: Shard, caplog):
    assert await shard.retrieve_report(
        dimensions=("day",),
        metrics=("views", "likes", "comments", "grossRevenue"),
        start_date=dt.date(2022, 6, 20),
        end_date=dt.date(2022, 6, 26),
    ) == AnalyticsReport(json.loads(create_request_data()), TimeBasedActivity())
    assert "Created report of shape (7, 5)!" in caplog.text


@mock.patch.object(
    ClientSession, "get", return_value=MockResponse(create_group_list_data())
)
async def test_shard_fetch_groups(_, shard: Shard):
    assert await shard.fetch_groups() == GroupList(
        kind="youtube#groupListResponse",
        etag="f6g7h8i9j0",
        items=[
            Group(
                kind="youtube#group",
                etag="f6g7h8i9j0",
                id="a1b2c3d4e5",
                published_at=dt.datetime(
                    2022, 11, 30, 12, 34, 56, 789000, tzinfo=pytz.utc
                ),
                title="Barney the Dinosaur",
                item_count=69,
                item_type="youtube#video",
            )
        ],
        next_page_token="a1b2c3d4e5",
    )


@mock.patch.object(
    ClientSession, "get", return_value=MockResponse(create_group_item_list_data())
)
async def test_shard_fetch_group_items(_, shard: Shard):
    assert await shard.fetch_group_items("a1b2c3d4e5") == GroupItemList(
        kind="youtube#groupItemListResponse",
        etag="a1b2c3d4e5",
        items=[GroupItem.from_json(json.loads(create_group_item_data()))],
    )
