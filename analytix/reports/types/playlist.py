# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

from collections.abc import Collection

from analytix.errors import ValidationError
from analytix.reports.constants import ALL_PLAYLIST_METRICS
from analytix.reports.constants import GEOGRAPHICAL_PLAYLIST_METRICS
from analytix.reports.constants import LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS
from analytix.reports.constants import LOCATION_PLAYLIST_METRICS
from analytix.reports.constants import TOP_PLAYLIST_METRICS
from analytix.reports.constants import VALID_FILTER_OPTIONS
from analytix.reports.constraints import ExactlyOne
from analytix.reports.constraints import OneOrMore
from analytix.reports.constraints import Required
from analytix.reports.constraints import ZeroOrOne
from analytix.reports.parameters import Dimensions
from analytix.reports.parameters import Filters
from analytix.reports.parameters import Metrics
from analytix.reports.parameters import SortOptions

from . import ReportType


class BasicUserActivityPlaylist(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Basic user activity for playlists",
            metrics=Metrics(OneOrMore(*ALL_PLAYLIST_METRICS)),
            filters=Filters(ExactlyOne("playlist", "group")),
        )


class TimeBasedActivityPlaylist(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Time-based activity for playlists",
            metrics=Metrics(OneOrMore(*ALL_PLAYLIST_METRICS)),
            dimensions=Dimensions(ExactlyOne("day", "month")),
            filters=Filters(ExactlyOne("playlist", "group")),
        )


class GeographyBasedActivityPlaylist(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Geography-based activity for playlists",
            metrics=Metrics(OneOrMore(*GEOGRAPHICAL_PLAYLIST_METRICS)),
            dimensions=Dimensions(Required("country")),
            filters=Filters(
                ExactlyOne("playlist", "group"),
                ZeroOrOne("continent", "subContinent"),
            ),
        )


class GeographyBasedActivityUSPlaylist(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Geography-based activity for playlists (US)",
            metrics=Metrics(OneOrMore(*GEOGRAPHICAL_PLAYLIST_METRICS)),
            dimensions=Dimensions(Required("province")),
            filters=Filters(
                Required("country==US"),
                ExactlyOne("playlist", "group"),
            ),
        )


class PlaybackLocationPlaylist(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Playback locations for playlists",
            metrics=Metrics(OneOrMore(*LOCATION_PLAYLIST_METRICS)),
            dimensions=Dimensions(Required("insightPlaybackLocationType")),
            filters=Filters(ExactlyOne("playlist", "group")),
        )


class PlaybackLocationDetailPlaylist(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Playback locations for playlists (detailed)",
            metrics=Metrics(OneOrMore(*LOCATION_PLAYLIST_METRICS)),
            dimensions=Dimensions(Required("insightPlaybackLocationDetail")),
            filters=Filters(
                Required("insightPlaybackLocationType==EMBEDDED"),
                ExactlyOne("playlist", "group"),
            ),
            sort_options=SortOptions(
                OneOrMore(*LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS),
                descending_only=True,
            ),
            max_results=25,
        )


class TrafficSourcePlaylist(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Traffic sources for playlists",
            metrics=Metrics(OneOrMore(*ALL_PLAYLIST_METRICS)),
            dimensions=Dimensions(Required("insightTrafficSourceType")),
            filters=Filters(ExactlyOne("playlist", "group")),
        )


class TrafficSourceDetailPlaylist(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Traffic sources for playlists (detailed)",
            metrics=Metrics(OneOrMore(*ALL_PLAYLIST_METRICS)),
            dimensions=Dimensions(Required("insightTrafficSourceDetail")),
            filters=Filters(
                Required("insightTrafficSourceType"),
                ExactlyOne("playlist", "group"),
            ),
            sort_options=SortOptions(
                OneOrMore(*LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS),
                descending_only=True,
            ),
            max_results=25,
        )

    def validate(
        self,
        *,
        input_dimensions: Collection[str],
        input_filters: dict[str, str],
        input_metrics: Collection[str],
        input_sort_options: Collection[str],
        max_results: int = 0,
        start_index: int = 1,
    ) -> list[ValidationError]:
        errors = super().validate(
            input_dimensions=input_dimensions,
            input_filters=input_filters,
            input_metrics=input_metrics,
            input_sort_options=input_sort_options,
            max_results=max_results,
            start_index=start_index,
        )

        src_type = input_filters.get("insightTrafficSourceType", "")
        if (
            src_type
            and src_type not in VALID_FILTER_OPTIONS["insightTrafficSourceDetail"]
        ):
            errors.append(
                ValidationError.format(
                    "invalid value {value!r} for filter 'insightTrafficSourceType'",
                    value=src_type,
                ),
            )

        return errors


class DeviceTypePlaylist(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Device types for playlists",
            metrics=Metrics(OneOrMore(*LOCATION_PLAYLIST_METRICS)),
            dimensions=Dimensions(Required("deviceType")),
            filters=Filters(ExactlyOne("playlist", "group")),
        )


class OperatingSystemPlaylist(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Operating systems for playlists",
            metrics=Metrics(OneOrMore(*LOCATION_PLAYLIST_METRICS)),
            dimensions=Dimensions(Required("operatingSystem")),
            filters=Filters(ExactlyOne("playlist", "group")),
        )


class DeviceTypeAndOperatingSystemPlaylist(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Device types and operating systems for playlists",
            metrics=Metrics(OneOrMore(*LOCATION_PLAYLIST_METRICS)),
            dimensions=Dimensions(Required("deviceType", "operatingSystem")),
            filters=Filters(ExactlyOne("playlist", "group")),
        )


class ViewerDemographicsPlaylist(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Viewer demographics for playlists",
            metrics=Metrics(OneOrMore("viewerPercentage")),
            dimensions=Dimensions(OneOrMore("ageGroup", "gender")),
            filters=Filters(ExactlyOne("playlist", "group")),
        )


class TopPlaylists(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Top playlists",
            metrics=Metrics(OneOrMore(*TOP_PLAYLIST_METRICS)),
            dimensions=Dimensions(Required("playlist")),
            sort_options=SortOptions(
                OneOrMore(*LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS),
                descending_only=True,
            ),
            max_results=200,
        )
