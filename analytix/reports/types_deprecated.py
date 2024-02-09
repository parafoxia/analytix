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

__all__ = (
    "BasicUserActivityPlaylist",
    "TimeBasedActivityPlaylist",
    "GeographyBasedActivityPlaylist",
    "GeographyBasedActivityUSPlaylist",
    "PlaybackLocationPlaylist",
    "PlaybackLocationDetailPlaylist",
    "TrafficSourcePlaylist",
    "TrafficSourceDetailPlaylist",
    "DeviceTypePlaylist",
    "OperatingSystemPlaylist",
    "DeviceTypeAndOperatingSystemPlaylist",
    "ViewerDemographicsPlaylist",
    "TopPlaylists",
)

from typing import Collection, Dict

from analytix.abc import DetailedReportType, ReportType
from analytix.errors import InvalidRequest
from analytix.reports import data
from analytix.reports.features import (
    Dimensions,
    ExactlyOne,
    Filters,
    Metrics,
    OneOrMore,
    Optional,
    Required,
    SortOptions,
    ZeroOrMore,
    ZeroOrOne,
)


class BasicUserActivityPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Basic user activity for playlists (deprecated)"
        self.dimensions = Dimensions()
        self.filters = Filters(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*data.ALL_PLAYLIST_METRICS_DEPRECATED)
        self.sort_options = SortOptions(*self.metrics.values)


class TimeBasedActivityPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Time-based activity for playlists (deprecated)"
        self.dimensions = Dimensions(
            ExactlyOne("day", "month"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.filters = Filters(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*data.ALL_PLAYLIST_METRICS_DEPRECATED)
        self.sort_options = SortOptions(*self.metrics.values)


class GeographyBasedActivityPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Geography-based activity for playlists (deprecated)"
        self.dimensions = Dimensions(
            Required("country"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.filters = Filters(
            Required("isCurated==1"),
            ZeroOrOne("continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*data.ALL_PLAYLIST_METRICS_DEPRECATED)
        self.sort_options = SortOptions(*self.metrics.values)


class GeographyBasedActivityUSPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Geography-based activity for playlists (US) (deprecated)"
        self.dimensions = Dimensions(
            Required("province"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.filters = Filters(
            Required("isCurated==1", "country==US"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*data.ALL_PLAYLIST_METRICS_DEPRECATED)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackLocationPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Playback locations for playlists (deprecated)"
        self.dimensions = Dimensions(
            Required("insightPlaybackLocationType"),
            ZeroOrMore("day", "subscribedStatus"),
        )
        self.filters = Filters(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            Optional("subscribedStatus"),
        )
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS_DEPRECATED)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackLocationDetailPlaylist(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Playback locations for playlists (detailed) (deprecated)"
        self.dimensions = Dimensions(
            Required("insightPlaybackLocationDetail"),
        )
        self.filters = Filters(
            Required("isCurated==1", "insightPlaybackLocationType==EMBEDDED"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            Optional("subscribedStatus"),
        )
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS_DEPRECATED)
        self.sort_options = SortOptions(
            *data.LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS_DEPRECATED,
            descending_only=True,
        )
        self.max_results = 25


class TrafficSourcePlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Traffic sources for playlists (deprecated)"
        self.dimensions = Dimensions(
            Required("insightTrafficSourceType"),
            ZeroOrMore("day", "subscribedStatus"),
        )
        self.filters = Filters(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            Optional("subscribedStatus"),
        )
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS_DEPRECATED)
        self.sort_options = SortOptions(*self.metrics.values)


class TrafficSourceDetailPlaylist(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Traffic sources for playlists (detailed) (deprecated)"
        self.dimensions = Dimensions(
            Required("insightTrafficSourceDetail"),
        )
        self.filters = Filters(
            Required("isCurated==1", "insightTrafficSourceType"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            Optional("subscribedStatus"),
        )
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS_DEPRECATED)
        self.sort_options = SortOptions(
            *data.LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS_DEPRECATED,
            descending_only=True,
        )
        self.max_results = 25

    def validate(
        self,
        dimensions: Collection[str],
        filters: Dict[str, str],
        metrics: Collection[str],
        sort_options: Collection[str],
        max_results: int = 0,
        start_index: int = 1,
    ) -> None:
        super().validate(
            dimensions, filters, metrics, sort_options, max_results, start_index
        )

        itst = filters["insightTrafficSourceType"]
        if itst not in data.VALID_FILTER_OPTIONS["insightTrafficSourceDetail"]:
            raise InvalidRequest.incompatible_filter_value(
                "insightTrafficSourceType", itst
            )


class DeviceTypePlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Device types for playlists (deprecated)"
        self.dimensions = Dimensions(
            Required("deviceType"),
            ZeroOrMore("day", "subscribedStatus", "youtubeProduct"),
        )
        self.filters = Filters(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("operatingSystem", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS_DEPRECATED)
        self.sort_options = SortOptions(*self.metrics.values)


class OperatingSystemPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Operating systems for playlists (deprecated)"
        self.dimensions = Dimensions(
            Required("operatingSystem"),
            ZeroOrMore("day", "subscribedStatus", "youtubeProduct"),
        )
        self.filters = Filters(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("deviceType", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS_DEPRECATED)
        self.sort_options = SortOptions(*self.metrics.values)


class DeviceTypeAndOperatingSystemPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Device types and operating systems for playlists (deprecated)"
        self.dimensions = Dimensions(
            Required("deviceType", "operatingSystem"),
            ZeroOrMore("day", "subscribedStatus", "youtubeProduct"),
        )
        self.filters = Filters(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS_DEPRECATED)
        self.sort_options = SortOptions(*self.metrics.values)


class ViewerDemographicsPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Viewer demographics for playlists (deprecated)"
        self.dimensions = Dimensions(
            OneOrMore("ageGroup", "gender"),
            Optional("subscribedStatus"),
        )
        self.filters = Filters(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("subscribedStatus"),
        )
        self.metrics = Metrics("viewerPercentage")
        self.sort_options = SortOptions(*self.metrics.values)


class TopPlaylists(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Top playlists (deprecated)"
        self.dimensions = Dimensions(Required("playlist"))
        self.filters = Filters(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrMore("playlist", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*data.ALL_PLAYLIST_METRICS_DEPRECATED)
        self.sort_options = SortOptions(
            *data.TOP_VIDEOS_SORT_OPTIONS,
            descending_only=True,
        )
        self.max_results = 200
