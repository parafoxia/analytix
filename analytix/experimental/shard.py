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

__all__ = ("Shard",)

import datetime as dt
import json
import logging
from typing import TYPE_CHECKING, Collection, Dict, Optional

from analytix.experimental.mixins import RequestMixin
from analytix.groups import GroupItemList, GroupList
from analytix.queries import GroupItemQuery, GroupQuery, ReportQuery
from analytix.reports import AnalyticsReport

if TYPE_CHECKING:
    from analytix.experimental.auth import Tokens
    from analytix.oidc import Scopes


_log = logging.getLogger(__name__)


class Shard(RequestMixin):
    __slots__ = ("_scopes", "_tokens")

    def __init__(self, scopes: "Scopes", tokens: "Tokens") -> None:
        self._scopes = scopes
        self._tokens = tokens

    def revive(self, tokens: "Tokens") -> "Shard":
        self._tokens = tokens
        return self

    def fetch_report(
        self,
        *,
        dimensions: Optional[Collection[str]] = None,
        filters: Optional[Dict[str, str]] = None,
        metrics: Optional[Collection[str]] = None,
        start_date: Optional[dt.date] = None,
        end_date: Optional[dt.date] = None,
        sort_options: Optional[Collection[str]] = None,
        max_results: int = 0,
        currency: str = "USD",
        start_index: int = 1,
        include_historical_data: bool = False,
    ) -> AnalyticsReport:
        query = ReportQuery(
            dimensions,
            filters,
            metrics,
            sort_options,
            max_results,
            start_date,
            end_date,
            currency,
            start_index,
            include_historical_data,
        )
        query.validate(self._scopes)

        with self._request(query.url, token=self._tokens.access_token) as resp:
            data = json.loads(resp.data)

        assert query.rtype
        report = AnalyticsReport(data, query.rtype)
        _log.info("Created '%s' report of shape %s", query.rtype, report.shape)
        return report

    def fetch_groups(
        self,
        *,
        ids: Optional[Collection[str]] = None,
        next_page_token: Optional[str] = None,
    ) -> GroupList:
        query = GroupQuery(ids, next_page_token)
        with self._request(query.url, token=self._tokens.access_token) as resp:
            return GroupList.from_json(json.loads(resp.data))

    def fetch_group_items(self, group_id: str) -> GroupItemList:
        query = GroupItemQuery(group_id)
        with self._request(query.url, token=self._tokens.access_token) as resp:
            return GroupItemList.from_json(json.loads(resp.data))
