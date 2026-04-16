# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

__all__ = (
    "AudienceRetention",
    "BasicUserActivity",
    "BasicUserActivityUS",
    "DeviceType",
    "DeviceTypeAndOperatingSystem",
    "EngagementAndContentSharing",
    "GeographyBasedActivity",
    "GeographyBasedActivityByCity",
    "GeographyBasedActivityUS",
    "OperatingSystem",
    "PlaybackDetailsLiveGeographyBased",
    "PlaybackDetailsLiveGeographyBasedUS",
    "PlaybackDetailsLiveTimeBased",
    "PlaybackDetailsSubscribedStatus",
    "PlaybackDetailsSubscribedStatusUS",
    "PlaybackDetailsViewPercentageGeographyBased",
    "PlaybackDetailsViewPercentageGeographyBasedUS",
    "PlaybackDetailsViewPercentageTimeBased",
    "PlaybackLocation",
    "PlaybackLocationDetail",
    "TimeBasedActivity",
    "TimeBasedActivityUS",
    "TopVideosPlaybackDetail",
    "TopVideosRegional",
    "TopVideosSubscribed",
    "TopVideosUS",
    "TopVideosYouTubeProduct",
    "TrafficSource",
    "TrafficSourceDetail",
    "ViewerDemographics",
)

import warnings
from collections.abc import Collection

from analytix.abc import DetailedReportType
from analytix.abc import ReportType
from analytix.errors import InvalidRequest
from analytix.reports.constants import ALL_PROVINCE_METRICS
from analytix.reports.constants import ALL_VIDEO_METRICS
from analytix.reports.constants import LIVE_PLAYBACK_DETAIL_METRICS
from analytix.reports.constants import LOCATION_AND_TRAFFIC_METRICS
from analytix.reports.constants import LOCATION_AND_TRAFFIC_SORT_OPTIONS
from analytix.reports.constants import SUBSCRIPTION_METRICS
from analytix.reports.constants import TOP_VIDEOS_EXTRA_SORT_OPTIONS
from analytix.reports.constants import TOP_VIDEOS_SORT_OPTIONS
from analytix.reports.constants import VALID_FILTER_OPTIONS
from analytix.reports.constants import VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
from analytix.reports.features import Dimensions
from analytix.reports.features import ExactlyOne
from analytix.reports.features import Filters
from analytix.reports.features import Metrics
from analytix.reports.features import OneOrMore
from analytix.reports.features import Optional
from analytix.reports.features import Required
from analytix.reports.features import SortOptions
from analytix.reports.features import ZeroOrMore
from analytix.reports.features import ZeroOrOne
from analytix.warnings import CityReportWarning


class BasicUserActivity(ReportType):
    def __init__(self) -> None:
        self.name = "Basic user activity"
        self.dimensions = Dimensions()
        self.filters = Filters(
            ZeroOrOne("country", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
        )
        self.metrics = Metrics(*ALL_VIDEO_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class BasicUserActivityUS(ReportType):
    def __init__(self) -> None:
        self.name = "Basic user activity (US)"
        self.dimensions = Dimensions()
        self.filters = Filters(
            Required("province"),
            ZeroOrOne("video", "group"),
        )
        self.metrics = Metrics(*ALL_PROVINCE_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class TimeBasedActivity(ReportType):
    def __init__(self) -> None:
        self.name = "Time-based activity"
        self.dimensions = Dimensions(
            ExactlyOne("day", "month"),
            Optional("creatorContentType"),
        )
        self.filters = Filters(
            ZeroOrOne("country", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
        )
        self.metrics = Metrics(*ALL_VIDEO_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class TimeBasedActivityUS(ReportType):
    def __init__(self) -> None:
        self.name = "Time-based activity (US)"
        self.dimensions = Dimensions(
            ExactlyOne("day", "month"),
            Optional("creatorContentType"),
        )
        self.filters = Filters(
            Required("province"),
            ZeroOrOne("video", "group"),
        )
        self.metrics = Metrics(*ALL_PROVINCE_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class GeographyBasedActivity(ReportType):
    def __init__(self) -> None:
        self.name = "Geography-based activity"
        self.dimensions = Dimensions(
            Required("country"),
            Optional("creatorContentType"),
        )
        self.filters = Filters(
            ZeroOrOne("continent", "subContinent"),
            ZeroOrOne("video", "group"),
        )
        self.metrics = Metrics(*ALL_VIDEO_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class GeographyBasedActivityUS(ReportType):
    def __init__(self) -> None:
        self.name = "Geography-based activity (US)"
        self.dimensions = Dimensions(
            Required("province"),
            Optional("creatorContentType"),
        )
        self.filters = Filters(
            Required("country==US"),
            ZeroOrOne("video", "group"),
        )
        self.metrics = Metrics(*ALL_PROVINCE_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class GeographyBasedActivityByCity(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Geography-based activity (by city)"
        self.dimensions = Dimensions(
            Required("city"),
            ZeroOrMore("creatorContentType", "country", "province", "subscribedStatus"),
            ZeroOrOne("day", "month"),
        )
        self.filters = Filters(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
        )
        self.metrics = Metrics(
            "views",
            "estimatedMinutesWatched",
            "averageViewDuration",
            "averageViewPercentage",
        )
        self.sort_options = SortOptions(
            *LOCATION_AND_TRAFFIC_SORT_OPTIONS,
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
        if 25 < max_results <= 250:
            warnings.warn(
                "While the documentation says city reports can have a maximum of 250 "
                "results, the actual maximum the API accepts (currently) is 25",
                CityReportWarning,
                stacklevel=5,
            )

        if "province" in dimensions:
            # Change the filters on the fly to confirm with special
            # rules for this report type.
            self.filters = Filters(Required("country==US"), ZeroOrOne("video", "group"))

        super().validate(
            dimensions,
            filters,
            metrics,
            sort_options,
            max_results,
            start_index,
        )


class PlaybackDetailsSubscribedStatus(ReportType):
    def __init__(self) -> None:
        self.name = "User activity by subscribed status"
        self.dimensions = Dimensions(
            ZeroOrMore("creatorContentType", "subscribedStatus"),
            ZeroOrOne("day", "month"),
        )
        self.filters = Filters(
            ZeroOrOne("country", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            Optional("subscribedStatus"),
        )
        self.metrics = Metrics(*SUBSCRIPTION_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackDetailsSubscribedStatusUS(ReportType):
    def __init__(self) -> None:
        self.name = "User activity by subscribed status (US)"
        self.dimensions = Dimensions(
            ZeroOrMore("creatorContentType", "subscribedStatus"),
            ZeroOrOne("day", "month"),
        )
        self.filters = Filters(
            ZeroOrOne("video", "group"),
            ZeroOrMore("province", "subscribedStatus"),
        )
        self.metrics = Metrics(*ALL_PROVINCE_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackDetailsLiveTimeBased(ReportType):
    def __init__(self) -> None:
        self.name = "Time-based playback details (live)"
        self.dimensions = Dimensions(
            ZeroOrMore(
                "creatorContentType",
                "liveOrOnDemand",
                "subscribedStatus",
                "youtubeProduct",
            ),
            ZeroOrOne("day", "month"),
        )
        self.filters = Filters(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*LIVE_PLAYBACK_DETAIL_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackDetailsViewPercentageTimeBased(ReportType):
    def __init__(self) -> None:
        self.name = "Time-based playback details (view percentage)"
        self.dimensions = Dimensions(
            ZeroOrMore("creatorContentType", "subscribedStatus", "youtubeProduct"),
            ZeroOrOne("day", "month"),
        )
        self.filters = Filters(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackDetailsLiveGeographyBased(ReportType):
    def __init__(self) -> None:
        self.name = "Geography-based playback details (live)"
        self.dimensions = Dimensions(
            Required("country"),
            ZeroOrMore(
                "creatorContentType",
                "liveOrOnDemand",
                "subscribedStatus",
                "youtubeProduct",
            ),
        )
        self.filters = Filters(
            ZeroOrOne("continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*LIVE_PLAYBACK_DETAIL_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackDetailsViewPercentageGeographyBased(ReportType):
    def __init__(self) -> None:
        self.name = "Geography-based playback details (view percentage)"
        self.dimensions = Dimensions(
            Required("country"),
            ZeroOrMore("creatorContentType", "subscribedStatus", "youtubeProduct"),
        )
        self.filters = Filters(
            ZeroOrOne("continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackDetailsLiveGeographyBasedUS(ReportType):
    def __init__(self) -> None:
        self.name = "Geography-based playback details (live, US)"
        self.dimensions = Dimensions(
            Required("province"),
            ZeroOrMore(
                "creatorContentType",
                "liveOrOnDemand",
                "subscribedStatus",
                "youtubeProduct",
            ),
        )
        self.filters = Filters(
            Required("country==US"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*LIVE_PLAYBACK_DETAIL_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackDetailsViewPercentageGeographyBasedUS(ReportType):
    def __init__(self) -> None:
        self.name = "Geography-based playback details (view percentage, US)"
        self.dimensions = Dimensions(
            Required("province"),
            ZeroOrMore("creatorContentType", "subscribedStatus", "youtubeProduct"),
        )
        self.filters = Filters(
            Required("country==US"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackLocation(ReportType):
    def __init__(self) -> None:
        self.name = "Playback locations"
        self.dimensions = Dimensions(
            Required("insightPlaybackLocationType"),
            ZeroOrMore(
                "creatorContentType",
                "day",
                "liveOrOnDemand",
                "subscribedStatus",
            ),
        )
        self.filters = Filters(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )
        self.metrics = Metrics(*LOCATION_AND_TRAFFIC_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackLocationDetail(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Playback locations (detailed)"
        self.dimensions = Dimensions(
            Required("insightPlaybackLocationDetail"),
            Optional("creatorContentType"),
        )
        self.filters = Filters(
            Required("insightPlaybackLocationType==EMBEDDED"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )
        self.metrics = Metrics(*LOCATION_AND_TRAFFIC_METRICS)
        self.sort_options = SortOptions(
            *LOCATION_AND_TRAFFIC_SORT_OPTIONS,
            descending_only=True,
        )
        self.max_results = 25


class TrafficSource(ReportType):
    def __init__(self) -> None:
        self.name = "Traffic sources"
        self.dimensions = Dimensions(
            Required("insightTrafficSourceType"),
            ZeroOrMore(
                "creatorContentType",
                "day",
                "liveOrOnDemand",
                "subscribedStatus",
            ),
        )
        self.filters = Filters(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )
        self.metrics = Metrics(*LOCATION_AND_TRAFFIC_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class TrafficSourceDetail(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Traffic sources (detailed)"
        self.dimensions = Dimensions(
            Required("insightTrafficSourceDetail"),
            Optional("creatorContentType"),
        )
        self.filters = Filters(
            Required("insightTrafficSourceType"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )
        self.metrics = Metrics(*LOCATION_AND_TRAFFIC_METRICS)
        self.sort_options = SortOptions(
            *LOCATION_AND_TRAFFIC_SORT_OPTIONS,
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

        itst = filters["insightTrafficSourceType"]
        if itst not in VALID_FILTER_OPTIONS["insightTrafficSourceDetail"]:
            raise InvalidRequest.incompatible_filter_value(
                "insightTrafficSourceType",
                itst,
            )


class DeviceType(ReportType):
    def __init__(self) -> None:
        self.name = "Device types"
        self.dimensions = Dimensions(
            Required("deviceType"),
            ZeroOrMore(
                "creatorContentType",
                "day",
                "liveOrOnDemand",
                "subscribedStatus",
                "youtubeProduct",
            ),
        )
        self.filters = Filters(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore(
                "operatingSystem",
                "liveOrOnDemand",
                "subscribedStatus",
                "youtubeProduct",
            ),
        )
        self.metrics = Metrics(*LOCATION_AND_TRAFFIC_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class OperatingSystem(ReportType):
    def __init__(self) -> None:
        self.name = "Operating systems"
        self.dimensions = Dimensions(
            Required("operatingSystem"),
            ZeroOrMore(
                "creatorContentType",
                "day",
                "liveOrOnDemand",
                "subscribedStatus",
                "youtubeProduct",
            ),
        )
        self.filters = Filters(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore(
                "deviceType",
                "liveOrOnDemand",
                "subscribedStatus",
                "youtubeProduct",
            ),
        )
        self.metrics = Metrics(*LOCATION_AND_TRAFFIC_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class DeviceTypeAndOperatingSystem(ReportType):
    def __init__(self) -> None:
        self.name = "Device types and operating systems"
        self.dimensions = Dimensions(
            Required("deviceType", "operatingSystem"),
            ZeroOrMore(
                "creatorContentType",
                "day",
                "liveOrOnDemand",
                "subscribedStatus",
                "youtubeProduct",
            ),
        )
        self.filters = Filters(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*LOCATION_AND_TRAFFIC_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class ViewerDemographics(ReportType):
    def __init__(self) -> None:
        self.name = "Viewer demographics"
        self.dimensions = Dimensions(
            OneOrMore("ageGroup", "gender"),
            ZeroOrMore("creatorContentType", "liveOrOnDemand", "subscribedStatus"),
        )
        self.filters = Filters(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )
        self.metrics = Metrics("viewerPercentage")
        self.sort_options = SortOptions(*self.metrics.values)


class EngagementAndContentSharing(ReportType):
    def __init__(self) -> None:
        self.name = "Engagement and content sharing"
        self.dimensions = Dimensions(
            Required("sharingService"),
            ZeroOrMore("creatorContentType", "subscribedStatus"),
        )
        self.filters = Filters(
            ZeroOrOne("country", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            Optional("subscribedStatus"),
        )
        self.metrics = Metrics("shares")
        self.sort_options = SortOptions(*self.metrics.values)


class AudienceRetention(ReportType):
    def __init__(self) -> None:
        self.name = "Audience retention"
        self.dimensions = Dimensions(
            Required("elapsedVideoTimeRatio"),
            Optional("creatorContentType"),
        )
        self.filters = Filters(
            Required("video"),
            ZeroOrMore("audienceType", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics("audienceWatchRatio", "relativeRetentionPerformance")
        self.sort_options = SortOptions(*self.metrics.values)

    def validate(
        self,
        dimensions: Collection[str],
        filters: dict[str, str],
        metrics: Collection[str],
        sort_options: Collection[str],
        max_results: int = 0,
        start_index: int = 1,
    ) -> None:
        super().validate(dimensions, filters, metrics, sort_options)

        v = filters["video"]
        if "," in v:
            raise InvalidRequest(
                "only one video ID can be provided when 'elapsedVideoTimeRatio' "
                "is a dimension",
            )


class TopVideosRegional(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Top videos by region"
        self.dimensions = Dimensions(Required("video"), Optional("creatorContentType"))
        self.filters = Filters(ZeroOrOne("country", "continent", "subContinent"))
        self.metrics = Metrics(*ALL_VIDEO_METRICS)
        self.sort_options = SortOptions(
            *TOP_VIDEOS_EXTRA_SORT_OPTIONS,
            descending_only=True,
        )
        self.max_results = 200


class TopVideosUS(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Top videos by state"
        self.dimensions = Dimensions(Required("video"), Optional("creatorContentType"))
        self.filters = Filters(Required("province"), Optional("subscribedStatus"))
        self.metrics = Metrics(*ALL_PROVINCE_METRICS)
        self.sort_options = SortOptions(
            *TOP_VIDEOS_SORT_OPTIONS,
            descending_only=True,
        )
        self.max_results = 200


class TopVideosSubscribed(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Top videos by subscription status"
        self.dimensions = Dimensions(Required("video"), Optional("creatorContentType"))
        self.filters = Filters(
            Optional("subscribedStatus"),
            ZeroOrOne("country", "continent", "subContinent"),
        )
        self.metrics = Metrics(*SUBSCRIPTION_METRICS)
        self.sort_options = SortOptions(
            *TOP_VIDEOS_SORT_OPTIONS,
            descending_only=True,
        )
        self.max_results = 200


class TopVideosYouTubeProduct(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Top videos by YouTube product"
        self.dimensions = Dimensions(Required("video"), Optional("creatorContentType"))
        self.filters = Filters(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)
        self.sort_options = SortOptions(
            *TOP_VIDEOS_SORT_OPTIONS,
            descending_only=True,
        )
        self.max_results = 200


class TopVideosPlaybackDetail(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Top videos by playback detail"
        self.dimensions = Dimensions(Required("video"), Optional("creatorContentType"))
        self.filters = Filters(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)
        self.sort_options = SortOptions(
            *TOP_VIDEOS_SORT_OPTIONS,
            descending_only=True,
        )
        self.max_results = 200
