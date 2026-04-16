# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

__all__ = (
    "BasicUserActivityPlaylist",
    "DeviceTypeAndOperatingSystemPlaylist",
    "DeviceTypePlaylist",
    "GeographyBasedActivityPlaylist",
    "GeographyBasedActivityUSPlaylist",
    "OperatingSystemPlaylist",
    "PlaybackLocationDetailPlaylist",
    "PlaybackLocationPlaylist",
    "TimeBasedActivityPlaylist",
    "TopPlaylists",
    "TrafficSourceDetailPlaylist",
    "TrafficSourcePlaylist",
    "ViewerDemographicsPlaylist",
)

from collections.abc import Collection

from analytix.abc import DetailedReportType
from analytix.abc import ReportType
from analytix.errors import InvalidRequest
from analytix.reports.constants import ALL_PLAYLIST_METRICS
from analytix.reports.constants import GEOGRAPHICAL_PLAYLIST_METRICS
from analytix.reports.constants import LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS
from analytix.reports.constants import LOCATION_PLAYLIST_METRICS
from analytix.reports.constants import TOP_PLAYLIST_METRICS
from analytix.reports.constants import VALID_FILTER_OPTIONS
from analytix.reports.features import Dimensions
from analytix.reports.features import ExactlyOne
from analytix.reports.features import Filters
from analytix.reports.features import Metrics
from analytix.reports.features import OneOrMore
from analytix.reports.features import Required
from analytix.reports.features import SortOptions
from analytix.reports.features import ZeroOrOne


class BasicUserActivityPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Basic user activity for playlists"
        self.dimensions = Dimensions()
        self.filters = Filters(ExactlyOne("playlist", "group"))
        self.metrics = Metrics(*ALL_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class TimeBasedActivityPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Time-based activity for playlists"
        self.dimensions = Dimensions(ExactlyOne("day", "month"))
        self.filters = Filters(ExactlyOne("playlist", "group"))
        self.metrics = Metrics(*ALL_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class GeographyBasedActivityPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Geography-based activity for playlists"
        self.dimensions = Dimensions(Required("country"))
        self.filters = Filters(
            ExactlyOne("playlist", "group"),
            ZeroOrOne("continent", "subContinent"),
        )
        self.metrics = Metrics(*GEOGRAPHICAL_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class GeographyBasedActivityUSPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Geography-based activity for playlists (US)"
        self.dimensions = Dimensions(Required("province"))
        self.filters = Filters(Required("country==US"), ExactlyOne("playlist", "group"))
        self.metrics = Metrics(*GEOGRAPHICAL_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackLocationPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Playback locations for playlists"
        self.dimensions = Dimensions(Required("insightPlaybackLocationType"))
        self.filters = Filters(ExactlyOne("playlist", "group"))
        self.metrics = Metrics(*LOCATION_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackLocationDetailPlaylist(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Playback locations for playlists (detailed)"
        self.dimensions = Dimensions(Required("insightPlaybackLocationDetail"))
        self.filters = Filters(
            Required("insightPlaybackLocationType==EMBEDDED"),
            ExactlyOne("playlist", "group"),
        )
        self.metrics = Metrics(*LOCATION_PLAYLIST_METRICS)
        self.sort_options = SortOptions(
            *LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS,
            descending_only=True,
        )
        self.max_results = 25


class TrafficSourcePlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Traffic sources for playlists"
        self.dimensions = Dimensions(Required("insightTrafficSourceType"))
        self.filters = Filters(ExactlyOne("playlist", "group"))
        self.metrics = Metrics(*ALL_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class TrafficSourceDetailPlaylist(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Traffic sources for playlists (detailed)"
        self.dimensions = Dimensions(Required("insightTrafficSourceDetail"))
        self.filters = Filters(
            Required("insightTrafficSourceType"),
            ExactlyOne("playlist", "group"),
        )
        self.metrics = Metrics(*ALL_PLAYLIST_METRICS)
        self.sort_options = SortOptions(
            *LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS,
            descending_only=True,
        )
        self.max_results = 25

    def validate(
        self,
        dimensions: Collection[str],
        filters: dict[str, str],
        metrics: Collection[str],
        sort_options: Collection[str],
        max_results: int = 0,
        start_index: int = 1,
    ) -> None:
        super().validate(
            dimensions,
            filters,
            metrics,
            sort_options,
            max_results,
            start_index,
        )

        src_type = filters["insightTrafficSourceType"]
        if src_type not in VALID_FILTER_OPTIONS["insightTrafficSourceDetail"]:
            raise InvalidRequest.incompatible_filter_value(
                "insightTrafficSourceType",
                src_type,
            )


class DeviceTypePlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Device types for playlists"
        self.dimensions = Dimensions(Required("deviceType"))
        self.filters = Filters(ExactlyOne("playlist", "group"))
        self.metrics = Metrics(*LOCATION_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class OperatingSystemPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Operating systems for playlists"
        self.dimensions = Dimensions(Required("operatingSystem"))
        self.filters = Filters(ExactlyOne("playlist", "group"))
        self.metrics = Metrics(*LOCATION_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class DeviceTypeAndOperatingSystemPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Device types and operating systems for playlists"
        self.dimensions = Dimensions(Required("deviceType", "operatingSystem"))
        self.filters = Filters(ExactlyOne("playlist", "group"))
        self.metrics = Metrics(*LOCATION_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class ViewerDemographicsPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Viewer demographics for playlists"
        self.dimensions = Dimensions(OneOrMore("ageGroup", "gender"))
        self.filters = Filters(ExactlyOne("playlist", "group"))
        self.metrics = Metrics("viewerPercentage")
        self.sort_options = SortOptions(*self.metrics.values)


class TopPlaylists(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Top playlists"
        self.dimensions = Dimensions(Required("playlist"))
        self.filters = Filters()
        self.metrics = Metrics(*TOP_PLAYLIST_METRICS)
        self.sort_options = SortOptions(
            *LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS,
            descending_only=True,
        )
        self.max_results = 200
