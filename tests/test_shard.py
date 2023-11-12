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

import datetime as dt
import logging
from unittest import mock

from analytix.auth import Scopes
from analytix.mixins import RequestMixin
from analytix.reports import Report
from analytix.shard import Shard


def test_shard_init(shard: Shard, tokens):
    assert shard._scopes == Scopes.ALL
    assert shard._tokens == tokens


def test_shard_fetch_report(shard: Shard, report: Report, response, caplog):
    with caplog.at_level(logging.INFO):
        with mock.patch.object(RequestMixin, "_request", return_value=response):
            new_report = shard.fetch_report(
                dimensions=("day",),
                metrics=("views", "likes", "comments", "grossRevenue"),
                start_date=dt.date(2022, 6, 20),
                end_date=dt.date(2022, 6, 26),
            )
            assert isinstance(new_report, Report)
            assert new_report.columns == report.columns
        assert "Created 'Time-based activity' report of shape (7, 2)" in caplog.text


def test_shard_fetch_groups(shard: Shard, group_list, group_list_response):
    with mock.patch.object(RequestMixin, "_request", return_value=group_list_response):
        assert group_list == shard.fetch_groups()


def test_shard_fetch_group_items(
    shard: Shard, group_item_list, group_item_list_response
):
    with mock.patch.object(
        RequestMixin, "_request", return_value=group_item_list_response
    ):
        assert group_item_list == shard.fetch_group_items("a1b2c3d4e5")
