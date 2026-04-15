# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

import warnings
from collections.abc import Collection

from analytix.errors import ValidationError
from analytix.reports.constants import ALL_PROVINCE_METRICS
from analytix.reports.constants import ALL_VIDEO_METRICS
from analytix.reports.constants import CITY_METRICS
from analytix.reports.constants import LIVE_PLAYBACK_DETAIL_METRICS
from analytix.reports.constants import LOCATION_AND_TRAFFIC_METRICS
from analytix.reports.constants import LOCATION_AND_TRAFFIC_SORT_OPTIONS
from analytix.reports.constants import SUBSCRIPTION_METRICS
from analytix.reports.constants import TOP_VIDEOS_EXTRA_SORT_OPTIONS
from analytix.reports.constants import TOP_VIDEOS_SORT_OPTIONS
from analytix.reports.constants import VALID_FILTER_OPTIONS
from analytix.reports.constants import VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
from analytix.reports.constraints import ExactlyOne
from analytix.reports.constraints import OneOrMore
from analytix.reports.constraints import Optional
from analytix.reports.constraints import Required
from analytix.reports.constraints import ZeroOrMore
from analytix.reports.constraints import ZeroOrOne
from analytix.reports.parameters import Dimensions
from analytix.reports.parameters import Filters
from analytix.reports.parameters import Metrics
from analytix.reports.parameters import SortOptions
from analytix.warnings import CityReportWarning

from . import ReportType


class BasicUserActivity(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Basic user activity",
            metrics=Metrics(OneOrMore(*ALL_VIDEO_METRICS)),
            filters=Filters(
                ZeroOrOne("country", "continent", "subContinent"),
                ZeroOrOne("video", "group"),
            ),
        )


class BasicUserActivityUS(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Basic user activity (US)",
            metrics=Metrics(OneOrMore(*ALL_PROVINCE_METRICS)),
            filters=Filters(
                Required("province"),
                ZeroOrOne("video", "group"),
            ),
        )


class TimeBasedActivity(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Time-based activity",
            metrics=Metrics(OneOrMore(*ALL_VIDEO_METRICS)),
            dimensions=Dimensions(
                ExactlyOne("day", "month"),
                Optional("creatorContentType"),
            ),
            filters=Filters(
                ZeroOrOne("country", "continent", "subContinent"),
                ZeroOrOne("video", "group"),
            ),
        )


class TimeBasedActivityUS(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Time-based activity (US)",
            metrics=Metrics(OneOrMore(*ALL_PROVINCE_METRICS)),
            dimensions=Dimensions(
                ExactlyOne("day", "month"),
                Optional("creatorContentType"),
            ),
            filters=Filters(
                Required("province"),
                ZeroOrOne("video", "group"),
            ),
        )


class GeographyBasedActivity(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Geography-based activity",
            metrics=Metrics(OneOrMore(*ALL_VIDEO_METRICS)),
            dimensions=Dimensions(
                Required("country"),
                Optional("creatorContentType"),
            ),
            filters=Filters(
                ZeroOrOne("continent", "subContinent"),
                ZeroOrOne("video", "group"),
            ),
        )


class GeographyBasedActivityUS(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Geography-based activity (US)",
            metrics=Metrics(OneOrMore(*ALL_PROVINCE_METRICS)),
            dimensions=Dimensions(
                Required("province"),
                Optional("creatorContentType"),
            ),
            filters=Filters(
                Required("country==US"),
                ZeroOrOne("video", "group"),
            ),
        )


class GeographyBasedActivityByCity(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Geography-based activity (by city)",
            metrics=Metrics(OneOrMore(*CITY_METRICS)),
            dimensions=Dimensions(
                Required("city"),
                ZeroOrMore(
                    "creatorContentType",
                    "country",
                    "province",
                    "subscribedStatus",
                ),
                ZeroOrOne("day", "month"),
            ),
            filters=Filters(
                ZeroOrOne("country", "province", "continent", "subContinent"),
                ZeroOrOne("video", "group"),
            ),
            sort_options=SortOptions(
                OneOrMore(*LOCATION_AND_TRAFFIC_SORT_OPTIONS),
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
        if 25 < max_results <= 250:
            warnings.warn(
                "While the documentation says city reports can have a maximum of 250 "
                "results, the actual maximum the API accepts (currently) is 25",
                CityReportWarning,
                stacklevel=5,
            )

        if "province" in input_dimensions:
            self.filters = Filters(Required("country==US"), ZeroOrOne("video", "group"))

        return super().validate(
            input_dimensions=input_dimensions,
            input_filters=input_filters,
            input_metrics=input_metrics,
            input_sort_options=input_sort_options,
            max_results=max_results,
            start_index=start_index,
        )


class PlaybackDetailsSubscribedStatus(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="User activity by subscribed status",
            metrics=Metrics(OneOrMore(*SUBSCRIPTION_METRICS)),
            dimensions=Dimensions(
                ZeroOrMore("creatorContentType", "subscribedStatus"),
                ZeroOrOne("day", "month"),
            ),
            filters=Filters(
                ZeroOrOne("country", "continent", "subContinent"),
                ZeroOrOne("video", "group"),
                Optional("subscribedStatus"),
            ),
        )


class PlaybackDetailsSubscribedStatusUS(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="User activity by subscribed status (US)",
            metrics=Metrics(OneOrMore(*ALL_PROVINCE_METRICS)),
            dimensions=Dimensions(
                ZeroOrMore("creatorContentType", "subscribedStatus"),
                ZeroOrOne("day", "month"),
            ),
            filters=Filters(
                ZeroOrOne("video", "group"),
                ZeroOrMore("province", "subscribedStatus"),
            ),
        )


class PlaybackDetailsLiveTimeBased(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Time-based playback details (live)",
            metrics=Metrics(OneOrMore(*LIVE_PLAYBACK_DETAIL_METRICS)),
            dimensions=Dimensions(
                ZeroOrMore(
                    "creatorContentType",
                    "liveOrOnDemand",
                    "subscribedStatus",
                    "youtubeProduct",
                ),
                ZeroOrOne("day", "month"),
            ),
            filters=Filters(
                ZeroOrOne("country", "province", "continent", "subContinent"),
                ZeroOrOne("video", "group"),
                ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
            ),
        )


class PlaybackDetailsViewPercentageTimeBased(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Time-based playback details (view percentage)",
            metrics=Metrics(OneOrMore(*VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)),
            dimensions=Dimensions(
                ZeroOrMore("creatorContentType", "subscribedStatus", "youtubeProduct"),
                ZeroOrOne("day", "month"),
            ),
            filters=Filters(
                ZeroOrOne("country", "province", "continent", "subContinent"),
                ZeroOrOne("video", "group"),
                ZeroOrMore("subscribedStatus", "youtubeProduct"),
            ),
        )


class PlaybackDetailsLiveGeographyBased(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Geography-based playback details (live)",
            metrics=Metrics(OneOrMore(*LIVE_PLAYBACK_DETAIL_METRICS)),
            dimensions=Dimensions(
                Required("country"),
                ZeroOrMore(
                    "creatorContentType",
                    "liveOrOnDemand",
                    "subscribedStatus",
                    "youtubeProduct",
                ),
            ),
            filters=Filters(
                ZeroOrOne("continent", "subContinent"),
                ZeroOrOne("video", "group"),
                ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
            ),
        )


class PlaybackDetailsViewPercentageGeographyBased(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Geography-based playback details (view percentage)",
            metrics=Metrics(OneOrMore(*VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)),
            dimensions=Dimensions(
                Required("country"),
                ZeroOrMore("creatorContentType", "subscribedStatus", "youtubeProduct"),
            ),
            filters=Filters(
                ZeroOrOne("continent", "subContinent"),
                ZeroOrOne("video", "group"),
                ZeroOrMore("subscribedStatus", "youtubeProduct"),
            ),
        )


class PlaybackDetailsLiveGeographyBasedUS(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Geography-based playback details (live, US)",
            metrics=Metrics(OneOrMore(*LIVE_PLAYBACK_DETAIL_METRICS)),
            dimensions=Dimensions(
                Required("province"),
                ZeroOrMore(
                    "creatorContentType",
                    "liveOrOnDemand",
                    "subscribedStatus",
                    "youtubeProduct",
                ),
            ),
            filters=Filters(
                Required("country==US"),
                ZeroOrOne("video", "group"),
                ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
            ),
        )


class PlaybackDetailsViewPercentageGeographyBasedUS(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Geography-based playback details (view percentage, US)",
            metrics=Metrics(OneOrMore(*VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)),
            dimensions=Dimensions(
                Required("province"),
                ZeroOrMore("creatorContentType", "subscribedStatus", "youtubeProduct"),
            ),
            filters=Filters(
                Required("country==US"),
                ZeroOrOne("video", "group"),
                ZeroOrMore("subscribedStatus", "youtubeProduct"),
            ),
        )


class PlaybackLocation(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Playback locations",
            metrics=Metrics(OneOrMore(*LOCATION_AND_TRAFFIC_METRICS)),
            dimensions=Dimensions(
                Required("insightPlaybackLocationType"),
                ZeroOrMore(
                    "creatorContentType",
                    "day",
                    "liveOrOnDemand",
                    "subscribedStatus",
                ),
            ),
            filters=Filters(
                ZeroOrOne("country", "province", "continent", "subContinent"),
                ZeroOrOne("video", "group"),
                ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
            ),
        )


class PlaybackLocationDetail(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Playback locations (detailed)",
            metrics=Metrics(OneOrMore(*LOCATION_AND_TRAFFIC_METRICS)),
            dimensions=Dimensions(
                Required("insightPlaybackLocationDetail"),
                Optional("creatorContentType"),
            ),
            filters=Filters(
                Required("insightPlaybackLocationType==EMBEDDED"),
                ZeroOrOne("country", "province", "continent", "subContinent"),
                ZeroOrOne("video", "group"),
                ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
            ),
            sort_options=SortOptions(
                OneOrMore(*LOCATION_AND_TRAFFIC_SORT_OPTIONS),
                descending_only=True,
            ),
            max_results=25,
        )


class TrafficSource(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Traffic sources",
            metrics=Metrics(OneOrMore(*LOCATION_AND_TRAFFIC_METRICS)),
            dimensions=Dimensions(
                Required("insightTrafficSourceType"),
                ZeroOrMore(
                    "creatorContentType",
                    "day",
                    "liveOrOnDemand",
                    "subscribedStatus",
                ),
            ),
            filters=Filters(
                ZeroOrOne("country", "province", "continent", "subContinent"),
                ZeroOrOne("video", "group"),
                ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
            ),
        )


class TrafficSourceDetail(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Traffic sources (detailed)",
            metrics=Metrics(OneOrMore(*LOCATION_AND_TRAFFIC_METRICS)),
            dimensions=Dimensions(
                Required("insightTrafficSourceDetail"),
                Optional("creatorContentType"),
            ),
            filters=Filters(
                Required("insightTrafficSourceType"),
                ZeroOrOne("country", "province", "continent", "subContinent"),
                ZeroOrOne("video", "group"),
                ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
            ),
            sort_options=SortOptions(
                OneOrMore(*LOCATION_AND_TRAFFIC_SORT_OPTIONS),
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


class DeviceType(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Device types",
            metrics=Metrics(OneOrMore(*LOCATION_AND_TRAFFIC_METRICS)),
            dimensions=Dimensions(
                Required("deviceType"),
                ZeroOrMore(
                    "creatorContentType",
                    "day",
                    "liveOrOnDemand",
                    "subscribedStatus",
                    "youtubeProduct",
                ),
            ),
            filters=Filters(
                ZeroOrOne("country", "province", "continent", "subContinent"),
                ZeroOrOne("video", "group"),
                ZeroOrMore(
                    "operatingSystem",
                    "liveOrOnDemand",
                    "subscribedStatus",
                    "youtubeProduct",
                ),
            ),
        )


class OperatingSystem(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Operating systems",
            metrics=Metrics(OneOrMore(*LOCATION_AND_TRAFFIC_METRICS)),
            dimensions=Dimensions(
                Required("operatingSystem"),
                ZeroOrMore(
                    "creatorContentType",
                    "day",
                    "liveOrOnDemand",
                    "subscribedStatus",
                    "youtubeProduct",
                ),
            ),
            filters=Filters(
                ZeroOrOne("country", "province", "continent", "subContinent"),
                ZeroOrOne("video", "group"),
                ZeroOrMore(
                    "deviceType",
                    "liveOrOnDemand",
                    "subscribedStatus",
                    "youtubeProduct",
                ),
            ),
        )


class DeviceTypeAndOperatingSystem(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Device types and operating systems",
            metrics=Metrics(OneOrMore(*LOCATION_AND_TRAFFIC_METRICS)),
            dimensions=Dimensions(
                Required("deviceType", "operatingSystem"),
                ZeroOrMore(
                    "creatorContentType",
                    "day",
                    "liveOrOnDemand",
                    "subscribedStatus",
                    "youtubeProduct",
                ),
            ),
            filters=Filters(
                ZeroOrOne("country", "province", "continent", "subContinent"),
                ZeroOrOne("video", "group"),
                ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
            ),
        )


class ViewerDemographics(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Viewer demographics",
            metrics=Metrics(OneOrMore("viewerPercentage")),
            dimensions=Dimensions(
                OneOrMore("ageGroup", "gender"),
                ZeroOrMore("creatorContentType", "liveOrOnDemand", "subscribedStatus"),
            ),
            filters=Filters(
                ZeroOrOne("country", "province", "continent", "subContinent"),
                ZeroOrOne("video", "group"),
                ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
            ),
        )


class EngagementAndContentSharing(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Engagement and content sharing",
            metrics=Metrics(OneOrMore("shares")),
            dimensions=Dimensions(
                Required("sharingService"),
                ZeroOrMore("creatorContentType", "subscribedStatus"),
            ),
            filters=Filters(
                ZeroOrOne("country", "continent", "subContinent"),
                ZeroOrOne("video", "group"),
                Optional("subscribedStatus"),
            ),
        )


class AudienceRetention(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Audience retention",
            metrics=Metrics(
                OneOrMore("audienceWatchRatio", "relativeRetentionPerformance"),
            ),
            dimensions=Dimensions(
                Required("elapsedVideoTimeRatio"),
                Optional("creatorContentType"),
            ),
            filters=Filters(
                Required("video"),
                ZeroOrMore("audienceType", "subscribedStatus", "youtubeProduct"),
            ),
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
        )

        v = input_filters.get("video", "")
        if v and "," in v:
            errors.append(
                ValidationError(
                    "only one video ID can be provided when 'elapsedVideoTimeRatio' "
                    "is a dimension",
                ),
            )

        return errors


class TopVideosRegional(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Top videos by region",
            metrics=Metrics(OneOrMore(*ALL_VIDEO_METRICS)),
            dimensions=Dimensions(Required("video"), Optional("creatorContentType")),
            filters=Filters(ZeroOrOne("country", "continent", "subContinent")),
            sort_options=SortOptions(
                OneOrMore(*TOP_VIDEOS_EXTRA_SORT_OPTIONS),
                descending_only=True,
            ),
            max_results=200,
        )


class TopVideosUS(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Top videos by state",
            metrics=Metrics(OneOrMore(*ALL_PROVINCE_METRICS)),
            dimensions=Dimensions(Required("video"), Optional("creatorContentType")),
            filters=Filters(Required("province"), Optional("subscribedStatus")),
            sort_options=SortOptions(
                OneOrMore(*TOP_VIDEOS_SORT_OPTIONS),
                descending_only=True,
            ),
            max_results=200,
        )


class TopVideosSubscribed(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Top videos by subscription status",
            metrics=Metrics(OneOrMore(*SUBSCRIPTION_METRICS)),
            dimensions=Dimensions(Required("video"), Optional("creatorContentType")),
            filters=Filters(
                Optional("subscribedStatus"),
                ZeroOrOne("country", "continent", "subContinent"),
            ),
            sort_options=SortOptions(
                OneOrMore(*TOP_VIDEOS_SORT_OPTIONS),
                descending_only=True,
            ),
            max_results=200,
        )


class TopVideosYouTubeProduct(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Top videos by YouTube product",
            metrics=Metrics(OneOrMore(*VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)),
            dimensions=Dimensions(Required("video"), Optional("creatorContentType")),
            filters=Filters(
                ZeroOrOne("country", "province", "continent", "subContinent"),
                ZeroOrMore("subscribedStatus", "youtubeProduct"),
            ),
            sort_options=SortOptions(
                OneOrMore(*TOP_VIDEOS_SORT_OPTIONS),
                descending_only=True,
            ),
            max_results=200,
        )


class TopVideosPlaybackDetail(ReportType):
    def __init__(self) -> None:
        super().__init__(
            name="Top videos by playback detail",
            metrics=Metrics(OneOrMore(*VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)),
            dimensions=Dimensions(Required("video"), Optional("creatorContentType")),
            filters=Filters(
                ZeroOrOne("country", "province", "continent", "subContinent"),
                ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
            ),
            sort_options=SortOptions(
                OneOrMore(*TOP_VIDEOS_SORT_OPTIONS),
                descending_only=True,
            ),
            max_results=200,
        )
