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

__all__ = ("GroupItemQuery", "GroupQuery", "ReportQuery")

import datetime as dt
import logging
import warnings
from typing import TYPE_CHECKING
from typing import Collection
from typing import Dict
from typing import Optional

from analytix.auth import Scopes
from analytix.errors import InvalidRequest
from analytix.reports import data
from analytix.reports import types as rt
from analytix.warnings import InvalidMonthFormatWarning

if TYPE_CHECKING:
    from analytix.abc import ReportType

API_BASE_URL = "https://youtubeanalytics.googleapis.com/v2"
API_REPORTS_URL = f"{API_BASE_URL}/reports"
API_GROUPS_URL = f"{API_BASE_URL}/groups"
API_GROUP_ITEMS_URL = f"{API_BASE_URL}/groupItems"

_log = logging.getLogger(__name__)


class ReportQuery:
    __slots__ = (
        "_end_date",
        "_include_historical_data",
        "_start_date",
        "currency",
        "dimensions",
        "filters",
        "max_results",
        "metrics",
        "rtype",
        "sort_options",
        "start_index",
    )

    def __init__(
        self,
        dimensions: Optional[Collection[str]] = None,
        filters: Optional[Dict[str, str]] = None,
        metrics: Optional[Collection[str]] = None,
        sort_options: Optional[Collection[str]] = None,
        max_results: int = 0,
        start_date: Optional[dt.date] = None,
        end_date: Optional[dt.date] = None,
        currency: str = "USD",
        start_index: int = 1,
        include_historical_data: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        self.dimensions = dimensions or ()
        self.filters = filters or {}
        self.metrics = metrics or ()
        self.sort_options = sort_options or ()
        self.max_results = max_results

        self._end_date = end_date or dt.date.today()
        self._start_date = start_date or (self._end_date - dt.timedelta(days=28))
        self.currency = currency
        self.start_index = start_index
        self._include_historical_data = include_historical_data

        self.rtype: Optional[ReportType] = None

    @property
    def start_date(self) -> str:
        return self._start_date.strftime("%Y-%m-%d")

    @property
    def end_date(self) -> str:
        return self._end_date.strftime("%Y-%m-%d")

    @property
    def include_historical_data(self) -> str:
        return f"{self._include_historical_data}".lower()

    @property
    def url(self) -> str:
        filters = ";".join(f"{k}=={v}" for k, v in self.filters.items())
        return API_REPORTS_URL + (
            "?ids=channel==MINE"
            f"&dimensions={','.join(self.dimensions)}"
            f"&filters={filters}"
            f"&metrics={','.join(self.metrics)}"
            f"&sort={','.join(self.sort_options)}"
            f"&maxResults={self.max_results}"
            f"&startDate={self.start_date}"
            f"&endDate={self.end_date}"
            f"&currency={self.currency}"
            f"&startIndex={self.start_index}"
            f"&includeHistoricalData={self.include_historical_data}"
        )

    def validate(self, scopes: Scopes) -> None:
        _log.debug("Validating request")

        if self.max_results < 0:
            raise InvalidRequest(
                "the max results should be non-negative (0 for unlimited results)",
            )

        if not isinstance(self._start_date, dt.date):
            raise InvalidRequest("expected start date as date object")

        if not isinstance(self._end_date, dt.date):
            raise InvalidRequest("expected end date as date object")

        if self._end_date < self._start_date:
            raise InvalidRequest("the start date should be earlier than the end date")

        if "month" in self.dimensions and (
            self._start_date.day != 1 or self._end_date.day != 1
        ):
            warnings.warn(
                "Correcting start and end dates -- if 'month' is passed as a "
                "dimension, these should always be the first day of the month",
                InvalidMonthFormatWarning,
                stacklevel=4,
            )
            self._start_date = dt.date(self._start_date.year, self._start_date.month, 1)
            self._end_date = dt.date(self._end_date.year, self._end_date.month, 1)

        _log.debug(f"Getting data between {self.start_date} and {self.end_date}")

        if self.currency not in data.CURRENCIES:
            raise InvalidRequest(
                f"expected a valid ISO 4217 currency code, got {self.currency!r}",
            )

        if self.start_index < 1:
            raise InvalidRequest("the start index should be positive")

        self.set_report_type()
        assert self.rtype is not None

        if not self.metrics:
            self.metrics = [
                m for m in data.ALL_METRICS_ORDERED if m in self.rtype.metrics.values
            ]

        if not scopes & Scopes.MONETARY_READONLY:
            self.metrics = [m for m in self.metrics if m not in data.REVENUE_METRICS]
        elif not scopes & Scopes.READONLY:
            self.metrics = [m for m in self.metrics if m in data.REVENUE_METRICS]

        _log.debug("Metrics set to: " + ", ".join(self.metrics))

        if diff := {o.strip("-") for o in self.sort_options} - set(self.metrics):
            raise InvalidRequest.non_matching_sort_options(diff)

        self.rtype.validate(
            self.dimensions,
            self.filters,
            self.metrics,
            self.sort_options,
            self.max_results,
            self.start_index,
        )

        # If it gets to this point, it's fine.
        _log.debug("Request OK!")

    def _is_playlist_report_type(self) -> bool:
        if "playlist" in self.dimensions:
            return True

        if self.filters.get("playlist"):
            return True

        return bool(
            self.filters.get("group")
            and any(m in data.ALL_PLAYLIST_METRICS for m in self.metrics),
        )

    def _determine_video_report_type(self) -> "ReportType":
        # sourcery skip: low-code-quality
        if "adType" in self.dimensions:
            return rt.AdPerformance()

        if "sharingService" in self.dimensions:
            return rt.EngagementAndContentSharing()

        if "elapsedVideoTimeRatio" in self.dimensions:
            return rt.AudienceRetention()

        if "city" in self.dimensions:
            return rt.GeographyBasedActivityByCity()

        if "insightPlaybackLocationType" in self.dimensions:
            return rt.PlaybackLocation()

        if "insightPlaybackLocationDetail" in self.dimensions:
            return rt.PlaybackLocationDetail()

        if "insightTrafficSourceType" in self.dimensions:
            return rt.TrafficSource()

        if "insightTrafficSourceDetail" in self.dimensions:
            return rt.TrafficSourceDetail()

        if "ageGroup" in self.dimensions or "gender" in self.dimensions:
            return rt.ViewerDemographics()

        if "deviceType" in self.dimensions:
            if "operatingSystem" in self.dimensions:
                return rt.DeviceTypeAndOperatingSystem()
            return rt.DeviceType()

        if "operatingSystem" in self.dimensions:
            return rt.OperatingSystem()

        if "video" in self.dimensions:
            if "province" in self.filters:
                return rt.TopVideosUS()
            if "subscribedStatus" not in self.filters:
                return rt.TopVideosRegional()
            if "province" not in self.filters and "youtubeProduct" not in self.filters:
                return rt.TopVideosSubscribed()
            if "averageViewPercentage" in self.metrics:
                return rt.TopVideosYouTubeProduct()
            return rt.TopVideosPlaybackDetail()

        if "country" in self.dimensions:
            if "liveOrOnDemand" in self.dimensions or "liveOrOnDemand" in self.filters:
                return rt.PlaybackDetailsLiveGeographyBased()
            if (
                "subscribedStatus" in self.dimensions
                or "subscribedStatus" in self.filters
                or "youtubeProduct" in self.dimensions
                or "youtubeProduct" in self.filters
            ):
                return rt.PlaybackDetailsViewPercentageGeographyBased()
            return rt.GeographyBasedActivity()

        if "province" in self.dimensions:
            if "liveOrOnDemand" in self.dimensions or "liveOrOnDemand" in self.filters:
                return rt.PlaybackDetailsLiveGeographyBasedUS()
            if (
                "subscribedStatus" in self.dimensions
                or "subscribedStatus" in self.filters
                or "youtubeProduct" in self.dimensions
                or "youtubeProduct" in self.filters
            ):
                return rt.PlaybackDetailsViewPercentageGeographyBasedUS()
            return rt.GeographyBasedActivityUS()

        if "youtubeProduct" in self.dimensions or "youtubeProduct" in self.filters:
            if "liveOrOnDemand" in self.dimensions or "liveOrOnDemand" in self.filters:
                return rt.PlaybackDetailsLiveTimeBased()
            return rt.PlaybackDetailsViewPercentageTimeBased()

        if "liveOrOnDemand" in self.dimensions or "liveOrOnDemand" in self.filters:
            return rt.PlaybackDetailsLiveTimeBased()

        if "subscribedStatus" in self.dimensions:
            if "province" in self.filters:
                return rt.PlaybackDetailsSubscribedStatusUS()
            return rt.PlaybackDetailsSubscribedStatus()

        if "day" in self.dimensions or "month" in self.dimensions:
            if "province" in self.filters:
                return rt.TimeBasedActivityUS()
            return rt.TimeBasedActivity()

        if "province" in self.filters:
            return rt.BasicUserActivityUS()

        return rt.BasicUserActivity()

    def _determine_playlist_report_type(self) -> "ReportType":
        if "playlist" in self.dimensions:
            return rt.TopPlaylists()

        if "insightPlaybackLocationType" in self.dimensions:
            return rt.PlaybackLocationPlaylist()

        if "insightPlaybackLocationDetail" in self.dimensions:
            return rt.PlaybackLocationDetailPlaylist()

        if "insightTrafficSourceType" in self.dimensions:
            return rt.TrafficSourcePlaylist()

        if "insightTrafficSourceDetail" in self.dimensions:
            return rt.TrafficSourceDetailPlaylist()

        if "ageGroup" in self.dimensions or "gender" in self.dimensions:
            return rt.ViewerDemographicsPlaylist()

        if "deviceType" in self.dimensions:
            if "operatingSystem" in self.dimensions:
                return rt.DeviceTypeAndOperatingSystemPlaylist()
            return rt.DeviceTypePlaylist()

        if "operatingSystem" in self.dimensions:
            return rt.OperatingSystemPlaylist()

        if "country" in self.dimensions:
            return rt.GeographyBasedActivityPlaylist()

        if "province" in self.dimensions:
            return rt.GeographyBasedActivityUSPlaylist()

        if "day" in self.dimensions or "month" in self.dimensions:
            return rt.TimeBasedActivityPlaylist()

        return rt.BasicUserActivityPlaylist()

    def determine_report_type(self) -> "ReportType":
        playlist = self._is_playlist_report_type()

        return (
            self._determine_playlist_report_type()
            if playlist
            else self._determine_video_report_type()
        )

    def set_report_type(self) -> None:
        self.rtype = self.determine_report_type()
        _log.debug(f"Report type determined as {self.rtype.name!r}")


class GroupQuery:
    __slots__ = ("ids", "next_page_token")

    def __init__(
        self,
        ids: Optional[Collection[str]] = None,
        next_page_token: Optional[str] = None,
    ) -> None:
        self.ids = ids or ()
        self.next_page_token = next_page_token

    @property
    def url(self) -> str:
        ids = ("id=" + ",".join(self.ids)) if self.ids else "mine=true"
        npt = f"&next_page_token={self.next_page_token}" if self.next_page_token else ""
        return f"{API_GROUPS_URL}?{ids}{npt}"


class GroupItemQuery:
    __slots__ = ("group_id",)

    def __init__(self, group_id: str) -> None:
        self.group_id = group_id

    @property
    def url(self) -> str:
        return f"{API_GROUP_ITEMS_URL}?groupId={self.group_id}"
