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

import datetime
import logging
import typing as t
from dataclasses import dataclass

from aiohttp import ClientSession

from analytix import OAUTH_CHECK_URL, oidc
from analytix.errors import APIError, RefreshTokenExpired
from analytix.groups import GroupItemList, GroupList
from analytix.queries import GroupItemQuery, GroupQuery, ReportQuery
from analytix.reports import AnalyticsReport

_log = logging.getLogger(__name__)


@dataclass()
class Shard:
    __slots__ = ("_session", "_secrets", "_tokens")

    _session: ClientSession
    _secrets: oidc.Secrets
    _tokens: oidc.Tokens

    def __str__(self) -> str:
        return self._secrets.project_id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(project_id={self._secrets.project_id})"

    async def _request(self, url: str) -> dict[str, t.Any]:
        headers = {"Authorization": f"Bearer {self._tokens.access_token}"}
        async with self._session.get(url, headers=headers) as resp:
            if not resp.ok:
                raise APIError(resp.status, str(resp.reason))

            data: dict[str, t.Any] = await resp.json()
            _log.debug(f"Response data: {data}")

        if next(iter(data)) == "error":
            error = data["error"]
            raise APIError(error["code"], error["message"])

        return data

    async def token_refresh_required(self) -> bool:
        async with self._session.get(
            OAUTH_CHECK_URL + self._tokens.access_token
        ) as resp:
            if resp.ok:
                _log.info("Access token does not need refreshing")
                return False

        _log.info("Access token needs refreshing")
        return True

    async def refresh_access_token(
        self, *, check_need: bool = False
    ) -> oidc.Tokens | None:
        if check_need and (not await self.token_refresh_required()):
            return None

        _log.info("Refreshing access token")
        refresh_uri, data, headers = oidc.refresh_uri(
            self._secrets, self._tokens.refresh_token
        )

        async with self._session.post(refresh_uri, data=data, headers=headers) as resp:
            resp_data = await resp.json()
            _log.debug(f"Refreshed tokens: {resp_data}")

            if not resp.ok:
                raise RefreshTokenExpired("your refresh token has expired")

            self._tokens.update(resp_data)

        _log.info("Refresh complete!")
        return self._tokens

    async def retrieve_report(
        self,
        *,
        dimensions: t.Collection[str] | None = None,
        filters: dict[str, str] | None = None,
        metrics: t.Collection[str] | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
        sort_options: t.Collection[str] | None = None,
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

        query.validate()
        data = await self._request(query.url)

        if not query.rtype:
            query.set_report_type()

        assert query.rtype is not None
        report = AnalyticsReport(data, query.rtype)
        _log.info(f"Created report of shape {report.shape}!")
        return report

    async def fetch_groups(
        self,
        *,
        ids: t.Collection[str] | None = None,
        next_page_token: str | None = None,
    ) -> GroupList:
        query = GroupQuery(ids, next_page_token)
        return GroupList.from_json(await self._request(query.url))

    async def fetch_group_items(self, group_id: str) -> GroupItemList:
        query = GroupItemQuery(group_id)
        return GroupItemList.from_json(await self._request(query.url))