# Copyright (c) 2021, Ethan Henderson
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

from analytix.errors import InvalidRequest

from .constants import (
    YOUTUBE_ANALYTICS_ALL_PLAYLIST_METRICS,
    YOUTUBE_ANALYTICS_ALL_PROVINCE_METRICS,
    YOUTUBE_ANALYTICS_ALL_SORT_OPTIONS,
    YOUTUBE_ANALYTICS_ALL_VIDEO_METRICS,
    YOUTUBE_ANALYTICS_LIVE_PLAYBACK_DETAIL_METRICS,
    YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_METRICS,
    YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_PLAYLIST_METRICS,
    YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS,
    YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_SORT_OPTIONS,
    YOUTUBE_ANALYTICS_SUBSCRIPTION_METRICS,
    YOUTUBE_ANALYTICS_TOP_VIDEOS_SORT_OPTIONS,
    YOUTUBE_ANALYTICS_VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS,
)
from .features import (
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

_D = Dimensions
_F = Filters
_M = Metrics
_S = SortOptions


class ReportType:
    _friendly_name = "Generic"

    def __init__(self):
        self.dimensions = _D()
        self.metrics = _M()
        self.filters = _F()
        self.sort_options = _S()

    def __str__(self):
        return self._friendly_name

    def verify(self, dimensions, metrics, filters, sort_options, *args):
        self.dimensions.verify(dimensions)
        self.metrics.verify(metrics)
        self.filters.verify(filters)
        self.sort_options.verify(sort_options)


class DetailedReportType(ReportType):
    def __init__(self):
        super().__init__()
        self.max_results = 0

    def verify(self, dimensions, metrics, filters, sort_options, max_results):
        super().verify(dimensions, metrics, filters, sort_options)

        if not max_results or max_results > self.max_results:
            raise InvalidRequest(
                "the 'max_results' parameter must be provided and no larger "
                f"than {self.max_results} for the selected report type"
            )

        if not sort_options:
            raise InvalidRequest(
                "you must provide at least 1 sort parameter for the "
                "selected report type"
            )

        if any(not s[0] == "-" for s in sort_options):
            raise InvalidRequest(
                (
                    "you can only sort in descending order for this report "
                    "type; you can do this by prefixing the sort options with "
                    "a hyphen (-)"
                )
            )


class BasicUserActivity(ReportType):
    _friendly_name = "Basic user activity"

    def __init__(self):
        self.dimensions = _D()
        self.metrics = _M(*YOUTUBE_ANALYTICS_ALL_VIDEO_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
        )
        self.sort_options = _S(*YOUTUBE_ANALYTICS_ALL_VIDEO_METRICS)


class BasicUserActivityUS(ReportType):
    _friendly_name = "Basic user activity (US)"

    def __init__(self):
        self.dimensions = _D()
        self.metrics = _M(*YOUTUBE_ANALYTICS_ALL_PROVINCE_METRICS)
        self.filters = _F(
            Required("province"),
            ZeroOrOne("video", "group"),
        )
        self.sort_options = _S(*self.metrics.values)


class TimeBasedActivity(ReportType):
    _friendly_name = "Time-based activity"

    def __init__(self):
        self.dimensions = _D(ExactlyOne("day", "month"))
        self.metrics = _M(*YOUTUBE_ANALYTICS_ALL_VIDEO_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
        )
        self.sort_options = _S(*self.metrics.values)


class TimeBasedActivityUS(ReportType):
    _friendly_name = "Time-based activity (US)"

    def __init__(self):
        self.dimensions = _D(ExactlyOne("day", "month"))
        self.metrics = _M(*YOUTUBE_ANALYTICS_ALL_PROVINCE_METRICS)
        self.filters = _F(
            Required("province"),
            ZeroOrOne("video", "group"),
        )
        self.sort_options = _S(*self.metrics.values)


class GeographyBasedActivity(ReportType):
    _friendly_name = "Geography-based activity"

    def __init__(self):
        self.dimensions = _D(Required("country"))
        self.metrics = _M(*YOUTUBE_ANALYTICS_ALL_VIDEO_METRICS)
        self.filters = _F(
            ZeroOrOne("continent", "subContinent"),
            ZeroOrOne("video", "group"),
        )
        self.sort_options = _S(*self.metrics.values)


class GeographyBasedActivityUS(ReportType):
    _friendly_name = "Geography-based activity (US)"

    def __init__(self):
        self.dimensions = _D(Required("province"))
        self.metrics = _M(*YOUTUBE_ANALYTICS_ALL_PROVINCE_METRICS)
        self.filters = _F(
            Required("country==US"),
            ZeroOrOne("video", "group"),
        )
        self.sort_options = _S(*self.metrics.values)


class PlaybackDetailsSubscribedStatus(ReportType):
    _friendly_name = "User activity by subscribed status"

    def __init__(self):
        self.dimensions = _D(
            Optional("subscribedStatus"),
            ZeroOrOne("day", "month"),
        )
        self.metrics = _M(*YOUTUBE_ANALYTICS_SUBSCRIPTION_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            Optional("subscribedStatus"),
        )
        self.sort_options = _S(*self.metrics.values)


class PlaybackDetailsSubscribedStatusUS(ReportType):
    _friendly_name = "User activity by subscribed status (US)"

    def __init__(self):
        self.dimensions = _D(
            Optional("subscribedStatus"),
            ZeroOrOne("day", "month"),
        )
        self.metrics = _M(
            "views",
            "redViews",
            "estimatedMinutesWatched",
            "estimatedRedMinutesWatched",
            "averageViewDuration",
            "averageViewPercentage",
            "annotationClickThroughRate",
            "annotationCloseRate",
            "annotationImpressions",
            "annotationClickableImpressions",
            "annotationClosableImpressions",
            "annotationClicks",
            "annotationCloses",
            "cardClickRate",
            "cardTeaserClickRate",
            "cardImpressions",
            "cardTeaserImpressions",
            "cardClicks",
            "cardTeaserClicks",
        )
        self.filters = _F(
            ZeroOrOne("video", "group"),
            ZeroOrMore("province", "subscribedStatus"),
        )
        self.sort_options = _S(*self.metrics.values)


class PlaybackDetailsLiveTimeBased(ReportType):
    _friendly_name = "Time-based playback details (live)"

    def __init__(self):
        self.dimensions = _D(
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
            ZeroOrOne("day", "month"),
        )
        self.metrics = _M(*YOUTUBE_ANALYTICS_LIVE_PLAYBACK_DETAIL_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(*self.metrics.values)


class PlaybackDetailsViewPercentageTimeBased(ReportType):
    _friendly_name = "Time-based playback details (view percentage)"

    def __init__(self):
        self.dimensions = _D(
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
            ZeroOrOne("day", "month"),
        )
        self.metrics = _M(*YOUTUBE_ANALYTICS_LIVE_PLAYBACK_DETAIL_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(*self.metrics.values)


class PlaybackDetailsLiveGeographyBased(ReportType):
    _friendly_name = "Geography-based playback details (live)"

    def __init__(self):
        self.dimensions = _D(
            Required("country"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = _M(*YOUTUBE_ANALYTICS_LIVE_PLAYBACK_DETAIL_METRICS)
        self.filters = _F(
            ZeroOrOne("continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(*self.metrics.values)


class PlaybackDetailsViewPercentageGeographyBased(ReportType):
    _friendly_name = "Geography-based playback details (view percentage)"

    def __init__(self):
        self.dimensions = _D(
            Required("country"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = _M(
            *YOUTUBE_ANALYTICS_VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
        )
        self.filters = _F(
            ZeroOrOne("continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(*self.metrics.values)


class PlaybackDetailsLiveGeographyBasedUS(ReportType):
    _friendly_name = "Geography-based playback details (live, US)"

    def __init__(self):
        self.dimensions = _D(
            Required("province"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = _M(*YOUTUBE_ANALYTICS_LIVE_PLAYBACK_DETAIL_METRICS)
        self.filters = _F(
            Required("country==US"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(*self.metrics.values)


class PlaybackDetailsViewPercentageGeographyBasedUS(ReportType):
    _friendly_name = "Geography-based playback details (view percentage, US)"

    def __init__(self):
        self.dimensions = _D(
            Required("province"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = _M(
            *YOUTUBE_ANALYTICS_VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
        )
        self.filters = _F(
            Required("country==US"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(*self.metrics.values)


class PlaybackLocation(ReportType):
    _friendly_name = "Playback locations"

    def __init__(self):
        self.dimensions = _D(
            Required("insightPlaybackLocationType"),
            ZeroOrMore("day", "liveOrOnDemand", "subscribedStatus"),
        )
        self.metrics = _M(*YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )
        self.sort_options = _S(*self.metrics.values)


class PlaybackLocationDetail(DetailedReportType):
    _friendly_name = "Playback locations (detailed)"

    def __init__(self):
        self.dimensions = _D(Required("insightPlaybackLocationDetail"))
        self.metrics = _M(*YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_METRICS)
        self.filters = _F(
            Required("insightPlaybackLocationType==EMBEDDED"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )
        self.sort_options = _S(
            *YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_SORT_OPTIONS
        )
        self.max_results = 25


class TrafficSource(ReportType):
    _friendly_name = "Traffic sources"

    def __init__(self):
        self.dimensions = _D(
            Required("insightTrafficSourceType"),
            ZeroOrMore("day", "liveOrOnDemand", "subscribedStatus"),
        )
        self.metrics = _M(*YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )
        self.sort_options = _S(*self.metrics.values)


class TrafficSourceDetail(DetailedReportType):
    _friendly_name = "Traffic sources (detailed)"

    def __init__(self):
        self.dimensions = _D(Required("insightTrafficSourceDetail"))
        self.metrics = _M(*YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_METRICS)
        self.filters = _F(
            Required("insightTrafficSourceType"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )
        self.sort_options = _S(
            *YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_SORT_OPTIONS
        )
        self.max_results = 25


class DeviceType(ReportType):
    _friendly_name = "Device types"

    def __init__(self):
        self.dimensions = _D(
            Required("deviceType"),
            ZeroOrMore(
                "day", "liveOrOnDemand", "subscribedStatus", "youtubeProduct"
            ),
        )
        self.metrics = _M(*YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore(
                "operatingSystem",
                "liveOrOnDemand",
                "subscribedStatus",
                "youtubeProduct",
            ),
        )
        self.sort_options = _S(*self.metrics.values)


class OperatingSystem(ReportType):
    _friendly_name = "Operating systems"

    def __init__(self):
        self.dimensions = _D(
            Required("operatingSystem"),
            ZeroOrMore(
                "day", "liveOrOnDemand", "subscribedStatus", "youtubeProduct"
            ),
        )
        self.metrics = _M(*YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore(
                "deviceType",
                "liveOrOnDemand",
                "subscribedStatus",
                "youtubeProduct",
            ),
        )
        self.sort_options = _S(*self.metrics.values)


class DeviceTypeAndOperatingSystem(ReportType):
    _friendly_name = "Device types and operating systems"

    def __init__(self):
        self.dimensions = _D(
            Required("deviceType", "operatingSystem"),
            ZeroOrMore(
                "day", "liveOrOnDemand", "subscribedStatus", "youtubeProduct"
            ),
        )
        self.metrics = _M(*YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(*self.metrics.values)


class ViewerDemographics(ReportType):
    _friendly_name = "Viewer demographics"

    def __init__(self):
        self.dimensions = _D(
            OneOrMore("ageGroup", "gender"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )
        self.metrics = _M("viewerPercentage")
        self.filters = _F(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore(
                "deviceType",
                "liveOrOnDemand",
                "subscribedStatus",
                "youtubeProduct",
            ),
        )
        self.sort_options = _S(*self.metrics.values)


class EngagementAndContentSharing(ReportType):
    _friendly_name = "Engagement and content sharing"

    def __init__(self):
        self.dimensions = _D(
            Required("sharingService"),
            Optional("subscribedStatus"),
        )
        self.metrics = _M("shares")
        self.filters = _F(
            ZeroOrOne("country", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("subscribedStatus"),
        )
        self.sort_options = _S(*self.metrics.values)


class AudienceRetention(ReportType):
    _friendly_name = "Audience retention"

    def __init__(self):
        self.dimensions = _D(Required("elapsedVideoTimeRatio"))
        self.metrics = _M("audienceWatchRatio", "relativeRetentionPerformance")
        self.filters = _F(
            Required("video"),
            ZeroOrMore("audienceType", "subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(*self.metrics.values)

    def verify(self, dimensions, metrics, filters, sort_options, *args):
        super().verify(dimensions, metrics, filters, sort_options)

        if "," in filters["video"]:
            raise InvalidRequest(
                "you can only supply one video for the selected report type"
            )


class TopVideosRegional(DetailedReportType):
    _friendly_name = "Top videos by region"

    def __init__(self):
        self.dimensions = _D(Required("video"))
        self.metrics = _M(*YOUTUBE_ANALYTICS_ALL_VIDEO_METRICS)
        self.filters = _F(ZeroOrOne("country", "continent", "subContinent"))
        self.sort_options = _S(*YOUTUBE_ANALYTICS_ALL_SORT_OPTIONS)
        self.max_results = 200


class TopVideosUS(DetailedReportType):
    _friendly_name = "Top videos by state"

    def __init__(self):
        self.dimensions = _D(Required("video"))
        self.metrics = _M(*YOUTUBE_ANALYTICS_ALL_PROVINCE_METRICS)
        self.filters = _F(
            Required("province"),
            Optional("subscribedStatus"),
        )
        self.sort_options = _S(*YOUTUBE_ANALYTICS_TOP_VIDEOS_SORT_OPTIONS)
        self.max_results = 200


class TopVideosSubscribed(DetailedReportType):
    _friendly_name = "Top videos by subscription status"

    def __init__(self):
        self.dimensions = _D(Required("video"))
        self.metrics = _M(*YOUTUBE_ANALYTICS_SUBSCRIPTION_METRICS)
        self.filters = _F(
            Optional("subscribedStatus"),
            ZeroOrOne("country", "continent", "subContinent"),
        )
        self.sort_options = _S(*YOUTUBE_ANALYTICS_TOP_VIDEOS_SORT_OPTIONS)
        self.max_results = 200


class TopVideosYouTubeProduct(DetailedReportType):
    _friendly_name = "Top videos by YouTube product"

    def __init__(self):
        self.dimensions = _D(Required("video"))
        self.metrics = _M(
            *YOUTUBE_ANALYTICS_VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
        )
        self.filters = _F(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(*YOUTUBE_ANALYTICS_TOP_VIDEOS_SORT_OPTIONS)
        self.max_results = 200


class TopVideosPlaybackDetail(DetailedReportType):
    _friendly_name = "Top videos by playback detail"

    def __init__(self):
        self.dimensions = _D(Required("video"))
        self.metrics = _M(*YOUTUBE_ANALYTICS_LIVE_PLAYBACK_DETAIL_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(*YOUTUBE_ANALYTICS_TOP_VIDEOS_SORT_OPTIONS)
        self.max_results = 200


class BasicUserActivityPlaylist(ReportType):
    _friendly_name = "Basic user activity for playlists"

    def __init__(self):
        self.dimensions = _D()
        self.metrics = _M(*YOUTUBE_ANALYTICS_ALL_PLAYLIST_METRICS)
        self.filters = _F(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(*self.metrics.values)


class TimeBasedActivityPlaylist(ReportType):
    _friendly_name = "Time-based activity for playlists"

    def __init__(self):
        self.dimensions = _D(
            ExactlyOne("day", "month"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = _M(*YOUTUBE_ANALYTICS_ALL_PLAYLIST_METRICS)
        self.filters = _F(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(*self.metrics.values)


class GeographyBasedActivityPlaylist(ReportType):
    _friendly_name = "Geography-based activity for playlists"

    def __init__(self):
        self.dimensions = _D(
            ExactlyOne("country"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = _M(*YOUTUBE_ANALYTICS_ALL_PLAYLIST_METRICS)
        self.filters = _F(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(*self.metrics.values)


class GeographyBasedActivityUSPlaylist(ReportType):
    _friendly_name = "Geography-based activity for playlists (US)"

    def __init__(self):
        self.dimensions = _D(
            Required("province"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = _M(*YOUTUBE_ANALYTICS_ALL_PLAYLIST_METRICS)
        self.filters = _F(
            Required("isCurated==1", "country==US"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(*self.metrics.values)


class PlaybackLocationPlaylist(ReportType):
    _friendly_name = "Playback locations for playlists"

    def __init__(self):
        self.dimensions = _D(
            Required("insightPlaybackLocationType"),
            ZeroOrMore("day", "subscribedStatus"),
        )
        self.metrics = _M(
            *YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
        )
        self.filters = _F(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            Optional("subscribedStatus"),
        )
        self.sort_options = _S(*self.metrics.values)


class PlaybackLocationDetailPlaylist(DetailedReportType):
    _friendly_name = "Playback locations for playlists (detailed)"

    def __init__(self):
        self.dimensions = _D(
            Required("insightPlaybackLocationDetail"),
        )
        self.metrics = _M(
            *YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
        )
        self.filters = _F(
            Required("isCurated==1", "insightPlaybackLocationType==EMBEDDED"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            Optional("subscribedStatus"),
        )
        self.sort_options = _S(
            *YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS
        )
        self.max_results = 25


class TrafficSourcePlaylist(ReportType):
    _friendly_name = "Traffic sources for playlists"

    def __init__(self):
        self.dimensions = _D(
            Required("insightTrafficSourceType"),
            ZeroOrMore("day", "subscribedStatus"),
        )
        self.metrics = _M(
            *YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
        )
        self.filters = _F(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            Optional("subscribedStatus"),
        )
        self.sort_options = _S(*self.metrics.values)


class TrafficSourceDetailPlaylist(DetailedReportType):
    _friendly_name = "Traffic sources for playlists (detailed)"

    def __init__(self):
        self.dimensions = _D(
            Required("insightTrafficSourceDetail"),
        )
        self.metrics = _M(
            *YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
        )
        self.filters = _F(
            Required("isCurated==1", "insightTrafficSourceType"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            Optional("subscribedStatus"),
        )
        self.sort_options = _S(
            *YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS
        )
        self.max_results = 25


class DeviceTypePlaylist(ReportType):
    _friendly_name = "Device types for playlists"

    def __init__(self):
        self.dimensions = _D(
            Required("deviceType"),
            ZeroOrMore("day", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = _M(
            *YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
        )
        self.filters = _F(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore(
                "operatingSystem", "subscribedStatus", "youtubeProduct"
            ),
        )
        self.sort_options = _S(*self.metrics.values)


class OperatingSystemPlaylist(ReportType):
    _friendly_name = "Operating systems for playlists"

    def __init__(self):
        self.dimensions = _D(
            Required("operatingSystem"),
            ZeroOrMore("day", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = _M(
            *YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
        )
        self.filters = _F(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("deviceType", "subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(*self.metrics.values)


class DeviceTypeAndOperatingSystemPlaylist(ReportType):
    _friendly_name = "Device types and operating systems for playlists"

    def __init__(self):
        self.dimensions = _D(
            Required("deviceType", "operatingSystem"),
            ZeroOrMore("day", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = _M(
            *YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_PLAYLIST_METRICS
        )
        self.filters = _F(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(*self.metrics.values)


class ViewerDemographicsPlaylist(ReportType):
    _friendly_name = "Viewer demographics for playlists"

    def __init__(self):
        self.dimensions = _D(
            OneOrMore("ageGroup", "gender"),
            Optional("subscribedStatus"),
        )
        self.metrics = _M("viewerPercentage")
        self.filters = _F(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("playlist", "group"),
            ZeroOrMore("subscribedStatus"),
        )
        self.sort_options = _S(*self.metrics.values)


class TopPlaylists(DetailedReportType):
    _friendly_name = "Top playlists"

    def __init__(self):
        self.dimensions = _D(Required("playlist"))
        self.metrics = _M(*YOUTUBE_ANALYTICS_ALL_PLAYLIST_METRICS)
        self.filters = _F(
            Required("isCurated==1"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrMore("playlist", "subscribedStatus", "youtubeProduct"),
        )
        self.sort_options = _S(
            "views",
            "redViews",
            "estimatedMinutesWatched",
            "estimatedRedMinutesWatched",
        )
        self.max_results = 200


class AdPerformance(ReportType):
    _friendly_name = "Ad performance"

    def __init__(self):
        self.dimensions = _D(Required("adType"), Optional("day"))
        self.metrics = _M("grossRevenue", "adImpressions", "cpm")
        self.filters = _F(
            ZeroOrOne("video", "group"),
            ZeroOrOne("country", "continent", "subContinent"),
        )
        self.sort_options = _S(*self.metrics.values)


def determine(dimensions, metrics, filters):
    curated = filters.get("isCurated", "0") == "1"

    if "adType" in dimensions:
        return AdPerformance

    if "sharingService" in dimensions:
        return EngagementAndContentSharing

    if "elapsedVideoTimeRatio" in dimensions:
        return AudienceRetention

    if "playlist" in dimensions:
        return TopPlaylists

    if "insightPlaybackLocationType" in dimensions:
        if curated:
            return PlaybackLocationPlaylist
        return PlaybackLocation

    if "insightPlaybackLocationDetail" in dimensions:
        if curated:
            return PlaybackLocationDetailPlaylist
        return PlaybackLocationDetail

    if "insightTrafficSourceType" in dimensions:
        if curated:
            return TrafficSourcePlaylist
        return TrafficSource

    if "insightTrafficSourceDetail" in dimensions:
        if curated:
            return TrafficSourceDetailPlaylist
        return TrafficSourceDetail

    if "ageGroup" in dimensions or "gender" in dimensions:
        if curated:
            return ViewerDemographicsPlaylist
        return ViewerDemographics

    if "deviceType" in dimensions:
        if "operatingSystem" in dimensions:
            if curated:
                return DeviceTypeAndOperatingSystemPlaylist
            return DeviceTypeAndOperatingSystem
        if curated:
            return DeviceTypePlaylist
        return DeviceType

    if "operatingSystem" in dimensions:
        if curated:
            return OperatingSystemPlaylist
        return OperatingSystem

    # TODO: Re-do this section
    if "video" in dimensions:
        if "province" in filters:
            return TopVideosUS
        if "subscribedStatus" not in filters:
            return TopVideosRegional
        if "province" not in filters and "youtubeProduct" not in filters:
            return TopVideosSubscribed
        if "averageViewPercentage" in metrics:
            return TopVideosYouTubeProduct
        return TopVideosPlaybackDetail

    if "country" in dimensions:
        if "liveOrOnDemand" in dimensions or "liveOrOnDemand" in filters:
            return PlaybackDetailsLiveGeographyBased
        if curated:
            return GeographyBasedActivityPlaylist
        if (
            "subscribedStatus" in dimensions
            or "subscribedStatus" in filters
            or "youtubeProduct" in dimensions
            or "youtubeProduct" in filters
        ):
            return PlaybackDetailsViewPercentageGeographyBased
        return GeographyBasedActivity

    if "province" in dimensions:
        if "liveOrOnDemand" in dimensions or "liveOrOnDemand" in filters:
            return PlaybackDetailsLiveGeographyBasedUS
        if curated:
            return GeographyBasedActivityUSPlaylist
        if (
            "subscribedStatus" in dimensions
            or "subscribedStatus" in filters
            or "youtubeProduct" in dimensions
            or "youtubeProduct" in filters
        ):
            return PlaybackDetailsViewPercentageGeographyBasedUS
        return GeographyBasedActivityUS

    if "youtubeProduct" in dimensions or "youtubeProduct" in filters:
        if "liveOrOnDemand" in dimensions or "liveOrOnDemand" in filters:
            return PlaybackDetailsLiveTimeBased
        return PlaybackDetailsViewPercentageTimeBased

    if "liveOrOnDemand" in dimensions or "liveOrOnDemand" in filters:
        return PlaybackDetailsLiveTimeBased

    if "subscribedStatus" in dimensions:
        if "province" in filters:
            return PlaybackDetailsSubscribedStatusUS
        return PlaybackDetailsSubscribedStatus

    if "day" in dimensions or "month" in dimensions:
        if curated:
            return TimeBasedActivityPlaylist
        if "province" in filters:
            return TimeBasedActivityUS
        return TimeBasedActivity

    if curated:
        return BasicUserActivityPlaylist
    if "province" in filters:
        return BasicUserActivityUS
    return BasicUserActivity
