from analytix import InvalidRequest
from analytix.youtube import features
from analytix.youtube.features import FeatureAmount


class ReportType:
    __slots__ = ("dimensions", "metrics", "filters")

    def __init__(self):
        raise NotImplementedError("you should not use this class directly, nor call its __init__ method using super()")

    @property
    def all_dimensions(self):
        e = []
        for x in self.dimensions:
            e.extend(x[1])
        return e

    @property
    def all_filters(self):
        e = []
        for x in self.filters:
            e.extend(x[1])
        return e

    def verify(self, metrics, dimensions, filters):
        dimensions = set(dimensions)
        filters = set(filters)

        if metrics != "all":
            diff = set(metrics) - self.metrics
            if diff:
                raise InvalidRequest("unexpected metric(s): " + ", ".join(diff))

        diff = dimensions - set(self.all_dimensions)
        if diff:
            raise InvalidRequest("unexpected dimension(s): " + ", ".join(diff))

        diff = filters - set(self.all_filters)
        if diff:
            raise InvalidRequest("unexpected filter(s): " + ", ".join(diff))

        for amount, values in self.dimensions:
            similarities = len(dimensions & values)
            if amount == FeatureAmount.ZERO_OR_ONE and similarities > 1:
                raise InvalidRequest(f"expected 0 or 1 dimensions from {values}, got {len(dimensions)}")
            if amount == FeatureAmount.EXACTLY_ONE and similarities != 1:
                raise InvalidRequest(f"expected 1 dimension from {values}, got {len(dimensions)}")
            if amount == FeatureAmount.NON_ZERO and similarities == 0:
                raise InvalidRequest(f"expected at least 1 dimension from {values}, got {len(dimensions)}")

        for amount, values in self.filters:
            similarities = len(filters & values)
            if amount == FeatureAmount.ZERO_OR_ONE and similarities > 1:
                raise InvalidRequest(f"expected 0 or 1 filters from {values}, got {len(filters)}")
            if amount == FeatureAmount.EXACTLY_ONE and similarities != 1:
                raise InvalidRequest(f"expected 1 filter from {values}, got {len(filters)}")
            if amount == FeatureAmount.NON_ZERO and similarities == 0:
                raise InvalidRequest(f"expected at least 1 filter from {values}, got {len(filters)}")


class Generic(ReportType):
    def __init__(self):
        self.dimensions = []
        self.metrics = []
        self.filters = []

    def verify(self, *args):
        pass

    def __str__(self):
        return "Generic"


class BasicUserActivity(ReportType):
    def __init__(self):
        self.dimensions = []
        self.metrics = features.YOUTUBE_ANALYTICS_ALL_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"country", "continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
        ]

    def __str__(self):
        return "Basic user activity"


class BasicUserActivityUS(ReportType):
    def __init__(self):
        self.dimensions = []
        self.metrics = features.YOUTUBE_ANALYTICS_ALL_PROVINCE_METRICS
        self.filters = [(FeatureAmount.EXACTLY_ONE, {"province"}), (FeatureAmount.ZERO_OR_ONE, {"video", "group"})]

    def __str__(self):
        return "Basic user activity (US)"


class TimeBasedActivity(ReportType):
    def __init__(self):
        self.dimensions = [(FeatureAmount.EXACTLY_ONE, {"day", "month"})]
        self.metrics = features.YOUTUBE_ANALYTICS_ALL_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"country", "continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
        ]

    def __str__(self):
        return "Time-based activity"


class TimeBasedActivityUS(ReportType):
    def __init__(self):
        self.dimensions = [(FeatureAmount.EXACTLY_ONE, {"day", "month"})]
        self.metrics = features.YOUTUBE_ANALYTICS_ALL_PROVINCE_METRICS
        self.filters = [(FeatureAmount.EXACTLY_ONE, {"province"}), (FeatureAmount.ZERO_OR_ONE, {"video", "group"})]

    def __str__(self):
        return "Time-based activity (US)"


class GeographyBasedActivity(ReportType):
    def __init__(self):
        self.dimensions = [(FeatureAmount.EXACTLY_ONE, {"country"})]
        self.metrics = features.YOUTUBE_ANALYTICS_ALL_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
        ]

    def __str__(self):
        return "Geography-based activity"


class GeographyBasedActivityUS(ReportType):
    def __init__(self):
        self.dimensions = [(FeatureAmount.EXACTLY_ONE, {"province"})]
        self.metrics = features.YOUTUBE_ANALYTICS_ALL_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
        ]

    def __str__(self):
        return "Geography-based activity (US)"


class PlaybackDetailsSubscribedStatus(ReportType):
    def __init__(self):
        self.dimensions = [
            (FeatureAmount.ZERO_OR_ONE, {"subscribedStatus"}),
            (FeatureAmount.ZERO_OR_ONE, {"day", "month"}),
        ]
        self.metrics = features.YOUTUBE_ANALYTICS_SUBSCRIPTION_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"country", "continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ZERO_OR_ONE, {"subscribedStatus"}),
        ]

    def __str__(self):
        return "User activity by subscribed status"


class PlaybackDetailsSubscribedStatusUS(ReportType):
    def __init__(self):
        self.dimensions = [
            (FeatureAmount.ZERO_OR_ONE, {"subscribedStatus"}),
            (FeatureAmount.ZERO_OR_ONE, {"day", "month"}),
        ]
        self.metrics = {
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
        }
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ANY, {"province", "subscribedStatus"}),
        ]

    def __str__(self):
        return "User activity by subscribed status (US)"


class PlaybackDetailsLiveTimeBased(ReportType):
    def __init__(self):
        self.dimensions = [
            (FeatureAmount.ANY, {"liveOrOnDemand", "subscribedStatus", "youtubeProduct"}),
            (FeatureAmount.ZERO_OR_ONE, {"day", "month"}),
        ]
        self.metrics = features.YOUTUBE_ANALYTICS_LIVE_PLAYBACK_DETAIL_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"country", "province", "continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ANY, {"liveOrOnDemand", "subscribedStatus", "youtubeProduct"}),
        ]

    def __str__(self):
        return "Time-based playback details (live)"


class PlaybackDetailsViewPercentageTimeBased(ReportType):
    def __init__(self):
        self.dimensions = [
            (FeatureAmount.ANY, {"subscribedStatus", "youtubeProduct"}),
            (FeatureAmount.ZERO_OR_ONE, {"day", "month"}),
        ]
        self.metrics = features.YOUTUBE_ANALYTICS_VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"country", "province", "continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ANY, {"subscribedStatus", "youtubeProduct"}),
        ]

    def __str__(self):
        return "Time-based playback details (view percentage)"


class PlaybackDetailsLiveGeographyBased(ReportType):
    def __init__(self):
        self.dimensions = [
            (FeatureAmount.EXACTLY_ONE, {"country"}),
            (FeatureAmount.ANY, {"liveOrOnDemand", "subscribedStatus", "youtubeProduct"}),
        ]
        self.metrics = features.YOUTUBE_ANALYTICS_LIVE_PLAYBACK_DETAIL_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ANY, {"liveOrOnDemand", "subscribedStatus", "youtubeProduct"}),
        ]

    def __str__(self):
        return "Geography-based playback details (live)"


class PlaybackDetailsViewPercentageGeographyBased(ReportType):
    def __init__(self):
        self.dimensions = [
            (FeatureAmount.EXACTLY_ONE, {"country"}),
            (FeatureAmount.ANY, {"subscribedStatus", "youtubeProduct"}),
        ]
        self.metrics = features.YOUTUBE_ANALYTICS_VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ANY, {"subscribedStatus", "youtubeProduct"}),
        ]

    def __str__(self):
        return "Geography-based playback details (view percentage)"


class PlaybackDetailsLiveGeographyBasedUS(ReportType):
    def __init__(self):
        self.dimensions = [
            (FeatureAmount.EXACTLY_ONE, {"province"}),
            (FeatureAmount.ANY, {"liveOrOnDemand", "subscribedStatus", "youtubeProduct"}),
        ]
        self.metrics = features.YOUTUBE_ANALYTICS_LIVE_PLAYBACK_DETAIL_METRICS
        self.filters = [
            (FeatureAmount.EXACTLY_ONE, {"country"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ANY, {"liveOrOnDemand", "subscribedStatus", "youtubeProduct"}),
        ]

    def verify(self, metrics, dimensions, filters):
        super().verify(metrics, dimensions, filters)

        if filters["country"] != "US":
            raise InvalidRequest("the 'country' filter must be set to 'US'")

    def __str__(self):
        return "Geography-based playback details (live, US)"


class PlaybackDetailsViewPercentageGeographyBasedUS(ReportType):
    def __init__(self):
        self.dimensions = [
            (FeatureAmount.EXACTLY_ONE, {"province"}),
            (FeatureAmount.ANY, {"subscribedStatus", "youtubeProduct"}),
        ]
        self.metrics = features.YOUTUBE_ANALYTICS_VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
        self.filters = [
            (FeatureAmount.EXACTLY_ONE, {"country"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ANY, {"subscribedStatus", "youtubeProduct"}),
        ]

    def verify(self, metrics, dimensions, filters):
        super().verify(metrics, dimensions, filters)

        if filters["country"] != "US":
            raise InvalidRequest("the 'country' filter must be set to 'US'")

    def __str__(self):
        return "Geography-based playback details (view percentage, US)"


class PlaybackLocation(ReportType):
    def __init__(self):
        self.dimensions = [
            (FeatureAmount.EXACTLY_ONE, {"insightPlaybackLocationType"}),
            (FeatureAmount.ANY, {"day", "liveOrOnDemand", "subscribedStatus"}),
        ]
        self.metrics = features.YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"country", "province", "continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ANY, {"liveOrOnDemand", "subscribedStatus"}),
        ]

    def __str__(self):
        return "Playback locations"


class PlaybackLocationDetail(ReportType):
    def __init__(self):
        self.dimensions = [(FeatureAmount.EXACTLY_ONE, {"insightPlaybackLocationDetail"})]
        self.metrics = features.YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_METRICS
        self.filters = [
            (FeatureAmount.EXACTLY_ONE, {"insightPlaybackLocationType"}),
            (FeatureAmount.ZERO_OR_ONE, {"country", "province", "continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ANY, {"liveOrOnDemand", "subscribedStatus"}),
        ]

    def verify(self, metrics, dimensions, filters):
        super().verify(metrics, dimensions, filters)

        if filters["insightPlaybackLocationType"] != "EMBEDDED":
            raise InvalidRequest("the 'insightPlaybackLocationType' filter must be set to 'EMBEDDED'")

    def __str__(self):
        return "Playback locations (detailed)"


class TrafficSource(ReportType):
    def __init__(self):
        self.dimensions = [
            (FeatureAmount.EXACTLY_ONE, {"insightTrafficSourceType"}),
            (FeatureAmount.ANY, {"day", "liveOrOnDemand", "subscribedStatus"}),
        ]
        self.metrics = features.YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"country", "province", "continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ANY, {"liveOrOnDemand", "subscribedStatus"}),
        ]

    def __str__(self):
        return "Traffic sources"


class TrafficSourceDetail(ReportType):
    def __init__(self):
        self.dimensions = [(FeatureAmount.EXACTLY_ONE, {"insightTrafficSourceDetail"})]
        self.metrics = features.YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_METRICS
        self.filters = [
            (FeatureAmount.EXACTLY_ONE, {"insightTrafficSourceType"}),
            (FeatureAmount.ZERO_OR_ONE, {"country", "province", "continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ANY, {"liveOrOnDemand", "subscribedStatus"}),
        ]

    def __str__(self):
        return "Traffic sources (detailed)"


class DeviceType(ReportType):
    def __init__(self):
        self.dimensions = [
            (FeatureAmount.EXACTLY_ONE, {"deviceType"}),
            (FeatureAmount.ANY, {"day", "liveOrOnDemand", "subscribedStatus", "youtubeProduct"}),
        ]
        self.metrics = features.YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"country", "province", "continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ANY, {"operatingSystem", "liveOrOnDemand", "subscribedStatus", "youtubeProduct"}),
        ]

    def __str__(self):
        return "Device types"


class OperatingSystem(ReportType):
    def __init__(self):
        self.dimensions = [
            (FeatureAmount.EXACTLY_ONE, {"operatingSystem"}),
            (FeatureAmount.ANY, {"day", "liveOrOnDemand", "subscribedStatus", "youtubeProduct"}),
        ]
        self.metrics = features.YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"country", "province", "continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ANY, {"deviceType", "liveOrOnDemand", "subscribedStatus", "youtubeProduct"}),
        ]

    def __str__(self):
        return "Operating systems"


class DeviceTypeAndOperatingSystem(ReportType):
    def __init__(self):
        self.dimensions = [
            # TODO: Look at this.
            (FeatureAmount.EXACTLY_ONE, {"deviceType", "operatingSystem"}),
            (FeatureAmount.ANY, {"day", "liveOrOnDemand", "subscribedStatus", "youtubeProduct"}),
        ]
        self.metrics = features.YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"country", "province", "continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ANY, {"liveOrOnDemand", "subscribedStatus", "youtubeProduct"}),
        ]

    def __str__(self):
        return "Device types and operating systems"


class ViewerDemographics(ReportType):
    def __init__(self):
        self.dimensions = [
            (FeatureAmount.NON_ZERO, {"ageGroup", "gender"}),
            (FeatureAmount.ANY, {"liveOrOnDemand", "subscribedStatus"}),
        ]
        self.metrics = {"viewerPercentage"}
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"country", "province", "continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ANY, {"liveOrOnDemand", "subscribedStatus"}),
        ]

    def __str__(self):
        return "Viewer demographics"


class EngagementAndContentSharing(ReportType):
    def __init__(self):
        self.dimensions = [
            (FeatureAmount.EXACTLY_ONE, {"sharingService"}),
            (FeatureAmount.ZERO_OR_ONE, {"subscribedStatus"}),
        ]
        self.metrics = {"shares"}
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"country", "continent", "subContinent"}),
            (FeatureAmount.ZERO_OR_ONE, {"video", "group"}),
            (FeatureAmount.ZERO_OR_ONE, {"subscribedStatus"}),
        ]

    def __str__(self):
        return "Engagement and content sharing"


class AudienceRetention(ReportType):
    def __init__(self):
        self.dimensions = [(FeatureAmount.EXACTLY_ONE, {"elaspedVideoTimeRatio"})]
        self.metrics = {"audienceWatchRatio", "relativeRetentionPerformance"}
        self.filters = [
            (FeatureAmount.EXACTLY_ONE, {"video"}),
            (FeatureAmount.ANY, {"audienceType", "subscribedStatus", "youtubeProduct"}),
        ]

    def __str__(self):
        return "Audience retention"


class TopVideosRegional(ReportType):
    def __init__(self):
        self.dimensions = [(FeatureAmount.EXACTLY_ONE, {"video"})]
        self.metrics = features.YOUTUBE_ANALYTICS_ALL_METRICS
        self.filters = [(FeatureAmount.ZERO_OR_ONE, {"country", "continent", "subContinent"})]

    def __str__(self):
        return "Top videos by region"


class TopVideosUS(ReportType):
    def __init__(self):
        self.dimensions = [(FeatureAmount.EXACTLY_ONE, {"video"})]
        self.metrics = features.YOUTUBE_ANALYTICS_ALL_PROVINCE_METRICS
        self.filters = [(FeatureAmount.EXACTLY_ONE, {"province"}), (FeatureAmount.ZERO_OR_ONE, {"subscribedStatus"})]

    def __str__(self):
        return "Top videos by state"


class TopVideosSubscribed(ReportType):
    def __init__(self):
        self.dimensions = [(FeatureAmount.EXACTLY_ONE, {"video"})]
        self.metrics = features.YOUTUBE_ANALYTICS_SUBSCRIPTION_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"subscribedStatus"}),
            (FeatureAmount.ZERO_OR_ONE, {"country", "continent", "subContinent"}),
        ]

    def __str__(self):
        return "Top videos by subscription status"


class TopVideosYouTubeProduct(ReportType):
    def __init__(self):
        self.dimensions = [(FeatureAmount.EXACTLY_ONE, {"video"})]
        self.metrics = features.YOUTUBE_ANALYTICS_VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"country", "province", "continent", "subContinent"}),
            (FeatureAmount.ANY, {"subscribedStatus", "youtubeProduct"}),
        ]

    def __str__(self):
        return "Top videos by YouTube product"


class TopVideosPlaybackDetail(ReportType):
    def __init__(self):
        self.dimensions = [(FeatureAmount.EXACTLY_ONE, {"video"})]
        self.metrics = features.YOUTUBE_ANALYTICS_LIVE_PLAYBACK_DETAIL_METRICS
        self.filters = [
            (FeatureAmount.ZERO_OR_ONE, {"country", "province", "continent", "subContinent"}),
            (FeatureAmount.ANY, {"subscribedStatus", "youtubeProduct"}),
        ]

    def __str__(self):
        return "Top videos by playback detail"


def determine(metrics, dimensions, filters):
    if "insightPlaybackLocationType" in dimensions:
        return PlaybackLocation

    if "insightPlaybackLocationDetail" in dimensions:
        return PlaybackLocationDetail

    if "insightTrafficSourceType" in dimensions:
        return TrafficSource

    if "insightTrafficSourceDetail" in dimensions:
        return TrafficSourceDetail

    if "ageGroup" in dimensions or "gender" in dimensions:
        return ViewerDemographics

    if "sharingService" in dimensions:
        return EngagementAndContentSharing

    if "elapsedVideoTimeRatio" in dimensions:
        return AudienceRetention

    if "deviceType" in dimensions:
        if "operatingSystem" in dimensions:
            return DeviceTypeAndOperatingSystem
        return DeviceType

    if "operatingSystem" in dimensions:
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
        if "province" in filters:
            return TimeBasedActivityUS
        return TimeBasedActivity

    return None
