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

from analytix.groups import GroupItemList, GroupList
from analytix.mixins import RequestMixin
from analytix.queries import GroupItemQuery, GroupQuery, ReportQuery
from analytix.reports import AnalyticsReport

if TYPE_CHECKING:
    from analytix.auth import Scopes, Tokens


_log = logging.getLogger(__name__)


class Shard(RequestMixin):
    """A "mini-client" used to handle requests to the YouTube Analytics
    API.

    Shards should only be created using the `BaseClient.shard` or
    `Client.shard` context managers.

    Parameters
    ----------
    scopes : Scopes
        The scopes to allow in requests. This is used to control whether
        or not to allow access to monetary data.
    tokens : Tokens
        Your tokens.

    !!! warning
        If your channel is not partnered, attempting to access monetary
        data will result in a `Forbidden` error.
    """

    __slots__ = ("_scopes", "_tokens")

    def __init__(self, scopes: "Scopes", tokens: "Tokens") -> None:
        self._scopes = scopes
        self._tokens = tokens

    def fetch_report(
        self,
        *,
        dimensions: Optional[Collection[str]] = None,
        filters: Optional[Dict[str, str]] = None,
        metrics: Optional[Collection[str]] = None,
        sort_options: Optional[Collection[str]] = None,
        start_date: Optional[dt.date] = None,
        end_date: Optional[dt.date] = None,
        max_results: int = 0,
        currency: str = "USD",
        start_index: int = 1,
        include_historical_data: bool = False,
    ) -> AnalyticsReport:
        """Fetch an analytics report.

        Parameters
        ----------
        dimensions : Collection[str] or None, optional
            The dimensions to use within the request.
        filters : Dict[str, str] or None, optional
            The filters to use within the request.
        metrics : Collection[str] or None, optional
            The metrics to use within the request. If none are provided,
            all supported metrics are used.
        sort_options : Collection[str] or None, optional
            The sort options to use within the request.

        Returns
        -------
        AnalyticsReport
            The generated report.

        Other Parameters
        ----------------
        start_date : datetime.date or None, optional
            The date in which data should be pulled from. If this is
            not provided, this is set to 28 days before `end_date`.
        end_date : datetime.date or None, optional
            The date in which data should be pulled to. If this is not
            provided, this is set to the current date.
        max_results : int, optional
            The maximum number of results the report should include. If
            this is `0`, no upper limit is applied.
        currency : str, optional
            The currency revenue data should be represented using. This
            should be an ISO 4217 currency code.
        start_index : int, optional
            The first row in the report to include. This is one-indexed.
            If this is 1, all rows are included.
        include_historical_data : bool, optional
            Whether to include data from before the current channel
            owner assumed control of the channel. You only need to worry
            about this is the current channel owner did not create the
            channel.

        Raises
        ------
        InvalidRequest
            Your request was invalid.
        BadRequest
            Your request was invalid, but it was not caught by
            analytix's verification systems.
        Unauthorised
            Your access token is invalid.
        Forbidden
            You tried to access data you're not allowed to access. If
            your channel is not partnered, this is raised when you try
            to access monetary data.

        !!! info "See also"
            You can learn more about dimensions, filters, metrics, and
            sort options by reading the [detailed guides](../../guides/
            dimensions).

        !!! important
            To get playlist reports, you must set the `"isCurated"`
            filter to `"1"`. View the playlist example to see how this
            is done.

        !!! example "Fetching daily analytics data for 2022"
            ```py
            from datetime import datetime

            shard.fetch_report(
                dimensions=("day",),
                start_date=datetime.date(2022, 1, 1),
                end_date=datetime.date(2022, 12, 31),
            )
            ```

        !!! example "Fetching 10 most watched videos over last 28 days"
            ```py
            shard.fetch_report(
                dimensions=("video",),
                metrics=("estimatedMinutesWatched", "views"),
                sort_options=("-estimatedMinutesWatched"),
                max_results=10,
            )
            ```

        !!! example "Fetching playlist analytics"
            ```py
            shard.fetch_report(filters={"isCurated": "1"})
            ```
        """
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
        """Fetch a list of analytics groups.

        Parameters
        ----------
        ids : Collection[str] or None, optional
            The IDs of groups you want to fetch. If none are provided,
            all your groups will be fetched.
        next_page_token : str or None, optional
            If you need to make multiple requests, you can pass this to
            load a specific page. To check if you've arrived back at the
            first page, check the next page token from the request and
            compare it to the next page token from the first page.

        Returns
        -------
        GroupList
            An object containing the list of your groups and the next
            page token.

        Raises
        ------
        BadRequest
            Your request was invalid.
        Unauthorised
            Your access token is invalid.
        Forbidden
            You tried to access data you're not allowed to access. If
            your channel is not partnered, this is raised when you try
            to access monetary data.
        """
        query = GroupQuery(ids, next_page_token)
        with self._request(query.url, token=self._tokens.access_token) as resp:
            return GroupList.from_json(json.loads(resp.data))

    def fetch_group_items(self, group_id: str) -> GroupItemList:
        """Fetch a list of all items within a group.

        Parameters
        ----------
        group_id : str
            The ID of the group to fetch items for.

        Returns
        -------
        GroupItemList
            An object containing the list of group items and the next
            page token.

        Raises
        ------
        BadRequest
            Your request was invalid.
        Unauthorised
            Your access token is invalid.
        Forbidden
            You tried to access data you're not allowed to access. If
            your channel is not partnered, this is raised when you try
            to access monetary data.
        """
        query = GroupItemQuery(group_id)
        with self._request(query.url, token=self._tokens.access_token) as resp:
            return GroupItemList.from_json(json.loads(resp.data))
