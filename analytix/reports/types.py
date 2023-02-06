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

__all__ = (
    "BasicUserActivity",
    "BasicUserActivityUS",
    "TimeBasedActivity",
    "TimeBasedActivityUS",
    "GeographyBasedActivity",
    "GeographyBasedActivityUS",
    "GeographyBasedActivityByCity",
    "PlaybackDetailsSubscribedStatus",
    "PlaybackDetailsSubscribedStatusUS",
    "PlaybackDetailsLiveTimeBased",
    "PlaybackDetailsViewPercentageTimeBased",
    "PlaybackDetailsLiveGeographyBased",
    "PlaybackDetailsViewPercentageGeographyBased",
    "PlaybackDetailsLiveGeographyBasedUS",
    "PlaybackDetailsViewPercentageGeographyBasedUS",
    "PlaybackLocation",
    "PlaybackLocationDetail",
    "TrafficSource",
    "TrafficSourceDetail",
    "DeviceType",
    "OperatingSystem",
    "DeviceTypeAndOperatingSystem",
    "ViewerDemographics",
    "EngagementAndContentSharing",
    "AudienceRetention",
    "TopVideosRegional",
    "TopVideosUS",
    "TopVideosSubscribed",
    "TopVideosYouTubeProduct",
    "TopVideosPlaybackDetail",
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
    "AdPerformance",
)

import logging
import typing as t

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

_log = logging.getLogger(__name__)


class BasicUserActivity(ReportType):
    def __init__(self) -> None:
        self.name = "Basic user activity"
        self.dimensions = Dimensions()
        self.filters = Filters(
            ZeroOrOne("country", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
        )
        self.metrics = Metrics(*data.ALL_VIDEO_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class BasicUserActivityUS(ReportType):
    def __init__(self) -> None:
        self.name = "Basic user activity (US)"
        self.dimensions = Dimensions()
        self.filters = Filters(
            Required("province"),
            ZeroOrOne("video", "group"),
        )
        self.metrics = Metrics(*data.ALL_PROVINCE_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class TimeBasedActivity(ReportType):
    def __init__(self) -> None:
        self.name = "Time-based activity"
        self.dimensions = Dimensions(
            ExactlyOne("day", "month"), Optional("creatorContentType")
        )
        self.filters = Filters(
            ZeroOrOne("country", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
        )
        self.metrics = Metrics(*data.ALL_VIDEO_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class TimeBasedActivityUS(ReportType):
    def __init__(self) -> None:
        self.name = "Time-based activity (US)"
        self.dimensions = Dimensions(
            ExactlyOne("day", "month"), Optional("creatorContentType")
        )
        self.filters = Filters(
            Required("province"),
            ZeroOrOne("video", "group"),
        )
        self.metrics = Metrics(*data.ALL_PROVINCE_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class GeographyBasedActivity(ReportType):
    def __init__(self) -> None:
        self.name = "Geography-based activity"
        self.dimensions = Dimensions(
            Required("country"), Optional("creatorContentType")
        )
        self.filters = Filters(
            ZeroOrOne("continent", "subContinent"),
            ZeroOrOne("video", "group"),
        )
        self.metrics = Metrics(*data.ALL_VIDEO_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class GeographyBasedActivityUS(ReportType):
    def __init__(self) -> None:
        self.name = "Geography-based activity (US)"
        self.dimensions = Dimensions(
            Required("province"), Optional("creatorContentType")
        )
        self.filters = Filters(
            Required("country==US"),
            ZeroOrOne("video", "group"),
        )
        self.metrics = Metrics(*data.ALL_PROVINCE_METRICS)
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
            *data.LOCATION_AND_TRAFFIC_SORT_OPTIONS, descending_only=True
        )
        self.max_results = 25

    def validate(
        self,
        dimensions: t.Collection[str],
        filters: dict[str, str],
        metrics: t.Collection[str],
        sort_options: t.Collection[str],
        max_results: int = 0,
        start_index: int = 1,
    ) -> None:
        if 25 < max_results <= 250:
            _log.warning(
                "While the documentation says city reports can have a maximum of 250 "
                "results, the actual maximum the API accepts (currently) is 25"
            )

        if "province" in dimensions:
            # Change the filters on the fly to confirm with special
            # rules for this report type.
            self.filters = Filters(Required("country==US"), ZeroOrOne("video", "group"))

        super().validate(
            dimensions, filters, metrics, sort_options, max_results, start_index
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
        self.metrics = Metrics(*data.SUBSCRIPTION_METRICS)
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
        self.metrics = Metrics(*data.LESSER_SUBSCRIPTION_METRICS)
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
        self.metrics = Metrics(*data.LIVE_PLAYBACK_DETAIL_METRICS)
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
        self.metrics = Metrics(*data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)
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
        self.metrics = Metrics(*data.LIVE_PLAYBACK_DETAIL_METRICS)
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
        self.metrics = Metrics(*data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)
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
        self.metrics = Metrics(*data.LIVE_PLAYBACK_DETAIL_METRICS)
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
        self.metrics = Metrics(*data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackLocation(ReportType):
    def __init__(self) -> None:
        self.name = "Playback locations"
        self.dimensions = Dimensions(
            Required("insightPlaybackLocationType"),
            ZeroOrMore(
                "creatorContentType", "day", "liveOrOnDemand", "subscribedStatus"
            ),
        )
        self.filters = Filters(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackLocationDetail(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Playback locations (detailed)"
        self.dimensions = Dimensions(
            Required("insightPlaybackLocationDetail"), Optional("creatorContentType")
        )
        self.filters = Filters(
            Required("insightPlaybackLocationType==EMBEDDED"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_METRICS)
        self.sort_options = SortOptions(
            *data.LOCATION_AND_TRAFFIC_SORT_OPTIONS, descending_only=True
        )
        self.max_results = 25


class TrafficSource(ReportType):
    def __init__(self) -> None:
        self.name = "Traffic sources"
        self.dimensions = Dimensions(
            Required("insightTrafficSourceType"),
            ZeroOrMore(
                "creatorContentType", "day", "liveOrOnDemand", "subscribedStatus"
            ),
        )
        self.filters = Filters(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class TrafficSourceDetail(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Traffic sources (detailed)"
        self.dimensions = Dimensions(
            Required("insightTrafficSourceDetail"), Optional("creatorContentType")
        )
        self.filters = Filters(
            Required("insightTrafficSourceType"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_METRICS)
        self.sort_options = SortOptions(
            *data.LOCATION_AND_TRAFFIC_SORT_OPTIONS, descending_only=True
        )
        self.max_results = 25

    def validate(
        self,
        dimensions: t.Collection[str],
        filters: dict[str, str],
        metrics: t.Collection[str],
        sort_options: t.Collection[str],
        max_results: int = 0,
        start_index: int = 1,
    ) -> None:
        super().validate(
            dimensions, filters, metrics, sort_options, max_results, start_index
        )

        itst = filters["insightTrafficSourceType"]
        if itst not in data.VALID_FILTER_OPTIONS["insightTrafficSourceDetail"]:
            raise InvalidRequest(
                "dimensions and filters are incompatible with value "
                f"{itst!r} for filter 'insightTrafficSourceType'"
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
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_METRICS)
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
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_METRICS)
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
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_METRICS)
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
            Required("elapsedVideoTimeRatio"), Optional("creatorContentType")
        )
        self.filters = Filters(
            Required("video"),
            ZeroOrMore("audienceType", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics("audienceWatchRatio", "relativeRetentionPerformance")
        self.sort_options = SortOptions(*self.metrics.values)

    def validate(
        self,
        dimensions: t.Collection[str],
        filters: dict[str, str],
        metrics: t.Collection[str],
        sort_options: t.Collection[str],
        max_results: int = 0,
        start_index: int = 1,
    ) -> None:
        super().validate(dimensions, filters, metrics, sort_options)

        v = filters["video"]
        if "," in v:
            raise InvalidRequest(
                "only one video ID can be provided when 'elapsedVideoTimeRatio' "
                "is a dimension"
            )


class TopVideosRegional(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Top videos by region"
        self.dimensions = Dimensions(Required("video"), Optional("creatorContentType"))
        self.filters = Filters(ZeroOrOne("country", "continent", "subContinent"))
        self.metrics = Metrics(*data.ALL_VIDEO_METRICS)
        self.sort_options = SortOptions(
            *data.TOP_VIDEOS_EXTRA_SORT_OPTIONS, descending_only=True
        )
        self.max_results = 200


class TopVideosUS(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Top videos by state"
        self.dimensions = Dimensions(Required("video"), Optional("creatorContentType"))
        self.filters = Filters(Required("province"), Optional("subscribedStatus"))
        self.metrics = Metrics(*data.ALL_PROVINCE_METRICS)
        self.sort_options = SortOptions(
            *data.TOP_VIDEOS_SORT_OPTIONS, descending_only=True
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
        self.metrics = Metrics(*data.SUBSCRIPTION_METRICS)
        self.sort_options = SortOptions(
            *data.TOP_VIDEOS_SORT_OPTIONS, descending_only=True
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
        self.metrics = Metrics(*data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)
        self.sort_options = SortOptions(
            *data.TOP_VIDEOS_SORT_OPTIONS, descending_only=True
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
        self.metrics = Metrics(*data.VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)
        self.sort_options = SortOptions(
            *data.TOP_VIDEOS_SORT_OPTIONS, descending_only=True
        )
        self.max_results = 200


class BasicUserActivityPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Basic user activity for playlists"
        self.dimensions = Dimensions()
        self.filters = Filters(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*data.ALL_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class TimeBasedActivityPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Time-based activity for playlists"
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
        self.metrics = Metrics(*data.ALL_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class GeographyBasedActivityPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Geography-based activity for playlists"
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
        self.metrics = Metrics(*data.ALL_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class GeographyBasedActivityUSPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Geography-based activity for playlists (US)"
        self.dimensions = Dimensions(
            Required("province"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.filters = Filters(
            Required("isCurated==1", "country==US"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*data.ALL_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackLocationPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Playback locations for playlists"
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
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class PlaybackLocationDetailPlaylist(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Playback locations for playlists (detailed)"
        self.dimensions = Dimensions(
            Required("insightPlaybackLocationDetail"),
        )
        self.filters = Filters(
            Required("isCurated==1", "insightPlaybackLocationType==EMBEDDED"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            Optional("subscribedStatus"),
        )
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS)
        self.sort_options = SortOptions(
            *data.LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS, descending_only=True
        )
        self.max_results = 25


class TrafficSourcePlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Traffic sources for playlists"
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
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class TrafficSourceDetailPlaylist(DetailedReportType):
    def __init__(self) -> None:
        self.name = "Traffic sources for playlists (detailed)"
        self.dimensions = Dimensions(
            Required("insightTrafficSourceDetail"),
        )
        self.filters = Filters(
            Required("isCurated==1", "insightTrafficSourceType"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            Optional("subscribedStatus"),
        )
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS)
        self.sort_options = SortOptions(
            *data.LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS, descending_only=True
        )
        self.max_results = 25

    def validate(
        self,
        dimensions: t.Collection[str],
        filters: dict[str, str],
        metrics: t.Collection[str],
        sort_options: t.Collection[str],
        max_results: int = 0,
        start_index: int = 1,
    ) -> None:
        super().validate(
            dimensions, filters, metrics, sort_options, max_results, start_index
        )

        itst = filters["insightTrafficSourceType"]
        if itst not in data.VALID_FILTER_OPTIONS["insightTrafficSourceDetail"]:
            raise InvalidRequest(
                "dimensions and filters are incompatible with value "
                f"{itst!r} for filter 'insightTrafficSourceType'"
            )


class DeviceTypePlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Device types for playlists"
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
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class OperatingSystemPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Operating systems for playlists"
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
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class DeviceTypeAndOperatingSystemPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Device types and operating systems for playlists"
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
        self.metrics = Metrics(*data.LOCATION_AND_TRAFFIC_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*self.metrics.values)


class ViewerDemographicsPlaylist(ReportType):
    def __init__(self) -> None:
        self.name = "Viewer demographics for playlists"
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
        self.name = "Top playlists"
        self.dimensions = Dimensions(Required("playlist"))
        self.filters = Filters(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrMore("playlist", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = Metrics(*data.ALL_PLAYLIST_METRICS)
        self.sort_options = SortOptions(*data.TOP_VIDEOS_SORT_OPTIONS)
        self.max_results = 200


class AdPerformance(ReportType):
    def __init__(self) -> None:
        self.name = "Ad performance"
        self.dimensions = Dimensions(Required("adType"), Optional("day"))
        self.filters = Filters(
            ZeroOrOne("video", "group"),
            ZeroOrOne("country", "continent", "subContinent"),
        )
        self.metrics = Metrics("grossRevenue", "adImpressions", "cpm")
        self.sort_options = SortOptions(*self.metrics.values)
