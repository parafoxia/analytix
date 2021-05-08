from .types import (
    Dimensions,
    ExactlyOne,
    Filters,
    Metrics,
    OneOrMore,
    Optional,
    Required,
    ZeroOrMore,
    ZeroOrOne,
)
from .valid import *

_D = Dimensions
_F = Filters
_M = Metrics


class ReportType:
    _friendly_name = "Generic"

    def __init__(self):
        self.dimensions = _D()
        self.metrics = _M()
        self.filters = _F()

    def __str__(self):
        return self.__class__()._friendly_name

    def verify(self, dim, met, fil):
        self.dimensions.verify(dim)
        self.metrics.verify(met)
        self.filters.verify(fil)


class DetailedReportType(ReportType):
    def __init__(self):
        super().__init__()
        self.max_results = 0

    def verify(self, dim, met, fil, max, srt):
        super().verify(dim, met, fil)

        if not max or max >= self.max_results:
            raise InvalidRequest(
                f"the 'max_results' parameter must be no larger than {self.max_results} "
                "for the selected report type"
            )

        if not srt:
            raise InvalidRequest(
                f"you must provide at least 1 sort parameter for the selected report type"
            )

        if any(s not in met for s in srt):
            raise InvalidRequest(f"the sort parameter must be a valid metric")


class BasicUserActivity(ReportType):
    _friendly_name = "Basic user activity"

    def __init__(self):
        self.dimensions = _D()
        self.metrics = _M(*ALL_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
        )


class BasicUserActivityUS(ReportType):
    _friendly_name = "Basic user activity (US)"

    def __init__(self):
        self.dimensions = _D()
        self.metrics = _M(*ALL_PROVINCE_METRICS)
        self.filters = _F(
            Required("province"),
            ZeroOrOne("video", "group"),
        )


class TimeBasedActivity(ReportType):
    _friendly_name = "Time-based activity"

    def __init__(self):
        self.dimensions = _D(ExactlyOne("day", "month"))
        self.metrics = _M(*ALL_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
        )


class TimeBasedActivityUS(ReportType):
    _friendly_name = "Time-based activity (US)"

    def __init__(self):
        self.dimensions = _D(ExactlyOne("day", "month"))
        self.metrics = _M(*ALL_PROVINCE_METRICS)
        self.filters = _F(
            Required("province"),
            ZeroOrOne("video", "group"),
        )


class GeographyBasedActivity(ReportType):
    _friendly_name = "Geography-based activity"

    def __init__(self):
        self.dimensions = _D(Required("country"))
        self.metrics = _M(*ALL_METRICS)
        self.filters = _F(
            ZeroOrOne("continent", "subContinent"),
            ZeroOrOne("video", "group"),
        )


class GeographyBasedActivityUS(ReportType):
    _friendly_name = "Geography-based activity (US)"

    def __init__(self):
        self.dimensions = _D(Required("province"))
        self.metrics = _M(*ALL_PROVINCE_METRICS)
        self.filters = _F(
            Required("country==US"),
            ZeroOrOne("video", "group"),
        )


class PlaybackDetailsSubscribedStatus(ReportType):
    _friendly_name = "User activity by subscribed status"

    def __init__(self):
        self.dimensions = _D(
            Optional("subscribedStatus"),
            ZeroOrOne("day", "month"),
        )
        self.metrics = _M(*SUBSCRIPTION_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            Optional("subscribedStatus"),
        )


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


class PlaybackDetailsLiveTimeBased(ReportType):
    _friendly_name = "Time-based playback details (live)"

    def __init__(self):
        self.dimensions = _D(
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
            ZeroOrOne("day", "month"),
        )
        self.metrics = _M(*LIVE_PLAYBACK_DETAIL_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )


class PlaybackDetailsViewPercentageTimeBased(ReportType):
    _friendly_name = "Time-based playback details (view percentage)"

    def __init__(self):
        self.dimensions = _D(
            Required("country"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = _M(*LIVE_PLAYBACK_DETAIL_METRICS)
        self.filters = _F(
            ZeroOrOne("continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )


class PlaybackDetailsLiveGeographyBased(ReportType):
    _friendly_name = "Geography-based playback details (live)"

    def __init__(self):
        self.dimensions = _D(
            Required("country"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = _M(*LIVE_PLAYBACK_DETAIL_METRICS)
        self.filters = _F(
            ZeroOrOne("continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )


class PlaybackDetailsViewPercentageGeographyBased(ReportType):
    _friendly_name = "Geography-based playback details (view percentage)"

    def __init__(self):
        self.dimensions = _D(
            Required("country"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = _M(*VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)
        self.filters = _F(
            ZeroOrOne("continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )


class PlaybackDetailsLiveGeographyBasedUS(ReportType):
    _friendly_name = "Geography-based playback details (live, US)"

    def __init__(self):
        self.dimensions = _D(
            Required("province"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )
        self.metrics = _M(*LIVE_PLAYBACK_DETAIL_METRICS)
        self.filters = _F(
            Required("country==US"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )


class PlaybackDetailsViewPercentageGeographyBasedUS(ReportType):
    _friendly_name = "Geography-based playback details (view percentage, US)"

    def __init__(self):
        self.dimensions = _D(
            Required("province"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.metrics = _M(*VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)
        self.filters = _F(
            Required("country==US"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )


class PlaybackLocation(ReportType):
    _friendly_name = "Playback locations"

    def __init__(self):
        self.dimensions = _D(
            Required("insightPlaybackLocationType"),
            ZeroOrMore("day", "liveOrOnDemand", "subscribedStatus"),
        )
        self.metrics = _M(*LOCATION_AND_TRAFFIC_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )


class PlaybackLocationDetail(DetailedReportType):
    _friendly_name = "Playback locations (detailed)"

    def __init__(self):
        self.dimensions = _D(Required("insightPlaybackLocationDetail"))
        self.metrics = _M(*LOCATION_AND_TRAFFIC_METRICS)
        self.filters = _F(
            Required("insightPlaybackLocationType==EMBEDDED"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )
        self.max_results = 25


class TrafficSource(ReportType):
    _friendly_name = "Traffic sources"

    def __init__(self):
        self.dimensions = _D(
            Required("insightTrafficSourceType"),
            ZeroOrMore("day", "liveOrOnDemand", "subscribedStatus"),
        )
        self.metrics = _M(*LOCATION_AND_TRAFFIC_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )


class TrafficSourceDetail(DetailedReportType):
    _friendly_name = "Traffic sources (detailed)"

    def __init__(self):
        self.dimensions = _D(Required("insightTrafficSourceDetail"))
        self.metrics = _M(*LOCATION_AND_TRAFFIC_METRICS)
        self.filters = _F(
            Required("insightTrafficSourceType"),
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus"),
        )
        self.max_results = 25

        # TODO: Need a custom verifier here


class DeviceType(ReportType):
    _friendly_name = "Device types"

    def __init__(self):
        self.dimensions = _D(
            Required("deviceType"),
            ZeroOrMore(
                "day", "liveOrOnDemand", "subscribedStatus", "youtubeProduct"
            ),
        )
        self.metrics = _M(*LOCATION_AND_TRAFFIC_METRICS)
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


class OperatingSystem(ReportType):
    _friendly_name = "Operating systems"

    def __init__(self):
        self.dimensions = _D(
            Required("operatingSystem"),
            ZeroOrMore(
                "day", "liveOrOnDemand", "subscribedStatus", "youtubeProduct"
            ),
        )
        self.metrics = _M(*LOCATION_AND_TRAFFIC_METRICS)
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


class DeviceTypeAndOperatingSystem(ReportType):
    _friendly_name = "Device types and operating systems"

    def __init__(self):
        self.dimensions = _D(
            Required("deviceType", "operatingSystem"),
            ZeroOrMore(
                "day", "liveOrOnDemand", "subscribedStatus", "youtubeProduct"
            ),
        )
        self.metrics = _M(*LOCATION_AND_TRAFFIC_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrOne("video", "group"),
            ZeroOrMore("liveOrOnDemand", "subscribedStatus", "youtubeProduct"),
        )


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


class AudienceRetention(ReportType):
    _friendly_name = "Audience retention"

    def __init__(self):
        self.dimensions = _D(Required("elapsedVideoTimeRatio"))
        self.metrics = _M("audienceWatchRatio", "relativeRetentionPerformance")
        self.filters = _F(
            Required("video"),
            ZeroOrMore("audienceType", "subscribedStatus", "youtubeProduct"),
        )

        # TODO: Custom verify


class TopVideosRegional(DetailedReportType):
    _friendly_name = "Top videos by region"

    def __init__(self):
        self.dimensions = _D(Required("video"))
        self.metrics = _M(*ALL_METRICS)
        self.filters = _F(ZeroOrOne("country", "continent", "subContinent"))
        self.max_results = 200


class TopVideosUS(DetailedReportType):
    _friendly_name = "Top videos by state"

    def __init__(self):
        self.dimensions = _D(Required("video"))
        self.metrics = _M(*ALL_PROVINCE_METRICS)
        self.filters = _F(
            Required("province"),
            Optional("subscribedStatus"),
        )
        self.max_results = 200


class TopVideosSubscribed(DetailedReportType):
    _friendly_name = "Top videos by subscription status"

    def __init__(self):
        self.dimensions = _D(Required("video"))
        self.metrics = _M(*SUBSCRIPTION_METRICS)
        self.filters = _F(
            Optional("subscribedStatus"),
            ZeroOrOne("country", "continent", "subContinent"),
        )
        self.max_results = 200


class TopVideosYouTubeProduct(DetailedReportType):
    _friendly_name = "Top videos by YouTube product"

    def __init__(self):
        self.dimensions = _D(Required("video"))
        self.metrics = _M(*VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.max_results = 200


class TopVideosPlaybackDetail(DetailedReportType):
    _friendly_name = "Top videos by playback detail"

    def __init__(self):
        self.dimensions = _D(Required("video"))
        self.metrics = _M(*LIVE_PLAYBACK_DETAIL_METRICS)
        self.filters = _F(
            ZeroOrOne("country", "province", "continent", "subContinent"),
            ZeroOrMore("subscribedStatus", "youtubeProduct"),
        )
        self.max_results = 200


def determine(metrics, dimensions, filters):
    curated = filters.get("isCurated", "0") == "1"

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
            return GeographyBasedActivityPlaylistUS
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


_ALL_REPORTS = {
    "BASIC_USER_ACTIVITY": BasicUserActivity,
    "BASIC_USER_ACTIVITY_US": BasicUserActivityUS,
    "TIME_BASED_ACTIVITY": TimeBasedActivity,
    "TIME_BASED_ACTIVITY_US": TimeBasedActivityUS,
    "GEOGRAPHY_BASED_ACTIVITY": object(),
    "GEOGRAPHY_BASED_ACTIVITY_US": object(),
    "PLAYBACK_DETAILS_SUBSCRIBED_STATUS": object(),
    "PLAYBACK_DETAILS_SUBSCRIBED_STATUS_US": object(),
    "PLAYBACK_DETAILS_LIVE_TIME_BASED": object(),
    "PLAYBACK_DETAILS_VIEW_PERCENTAGE_TIME_BASED": object(),
    "PLAYBACK_DETAILS_LIVE_GEOGRAPHY_BASED": object(),
    "PLAYBACK_DETAILS_VIEW_PERCENTAGE_GEOGRAPHY_BASED": object(),
    "PLAYBACK_DETAILS_LIVE_GEOGRAPHY_BASED_US": object(),
    "PLAYBACK_DETAILS_VIEW_PERCENTAGE_GEOGRAPHY_BASED_US": object(),
    "PLAYBACK_LOCATION": object(),
    "PLAYBACK_LOCATION_DETAIL": object(),
    "TRAFFIC_SOURCE": object(),
    "TRAFFIC_SOURCE_DETAIL": object(),
    "DEVICE_TYPE": object(),
    "OPERATING_SYSTEM": object(),
    "DEVICE_TYPE_AND_OPERATING_SYSTEM": object(),
    "VIEWER_DEMOGRAPHICS": object(),
    "ENGAGEMENT_AND_CONTENT_SHARING": object(),
    "AUDIENCE_RETENTION": object(),
    "TOP_VIDEOS_REGIONAL": object(),
    "TOP_VIDEOS_US": object(),
    "TOP_VIDEOS_SUBSCRIBED": object(),
    "TOP_VIDEOS_YOUTUBE_PRODUCT": object(),
    "TOP_VIDEOS_PLAYBACK_DETAIL": object(),
    "BASIC_USER_ACTIVITY_PLAYLIST": object(),
    "TIME_BASED_ACTIVITY_PLAYLIST": object(),
    "GEOGRAPHY_BASED_ACTIVITY_PLAYLIST": object(),
    "GEOGRAPHY_BASED_ACTIVITY_US_PLAYLIST": object(),
    "PLAYBACK_LOCATION_PLAYLIST": object(),
    "PLAYBACK_LOCATION_DETAIL_PLAYLIST": object(),
    "TRAFFIC_SOURCE_PLAYLIST": object(),
    "TRAFFIC_SOURCE_DETAIL_PLAYLIST": object(),
    "DEVICE_TYPE_PLAYLIST": object(),
    "OPERATING_SYSTEM_PLAYLIST": object(),
    "DEVICE_TYPE_AND_OPERATING_SYSTEM_PLAYLIST": object(),
    "VIEWER_DEMOGRAPHICS_PLAYLIST": object(),
    "TOP_PLAYLISTS": object(),
    "AD_PERFORMANCE": object(),
}
