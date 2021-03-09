from enum import Enum, auto

YOUTUBE_ANALYTICS_ALL_METRICS = (
    "views",
    "redViews",
    "comments",
    "likes",
    "dislikes",
    "videosAddedToPlaylists",
    "videosRemovedFromPlaylists",
    "shares",
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
    "subscribersGained",
    "subscribersLost",
    "estimatedRevenue",
    "estimatedAdRevenue",
    "grossRevenue",
    "estimatedRedPartnerRevenue",
    "monetizedPlaybacks",
    "playbackBasedCpm",
    "adImpressions",
    "cpm",
)
YOUTUBE_ANALYTICS_ALL_PROVINCE_METRICS = (
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
YOUTUBE_ANALYTICS_SUBSCRIPTION_METRICS = (
    "views",
    "redViews",
    "likes",
    "dislikes",
    "videosAddedToPlaylists",
    "videosRemovedFromPlaylists",
    "shares",
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
YOUTUBE_ANALYTICS_LIVE_PLAYBACK_DETAIL_METRICS = (
    "views",
    "redViews",
    "estimatedMinutesWatched",
    "estimatedRedMinutesWatched",
    "averageViewDuration",
)
YOUTUBE_ANALYTICS_VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS = (
    "views",
    "redViews",
    "estimatedMinutesWatched",
    "estimatedRedMinutesWatched",
    "averageViewDuration",
    "averageViewPercentage",
)
YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_METRICS = (
    "views",
    "estimatedMinutesWatched",
)
YOUTUBE_ANALYTICS_ALL_PLAYLIST_METRICS = (
    "views",
    "redViews",
    "estimatedMinutesWatched",
    "estimatedRedMinutesWatched",
    "averageViewDuration",
    "playlistStarts",
    "viewsPerPlaylistStart",
    "averageTimeInPlaylist",
)
YOUTUBE_ANALYTICS_LOCATION_AND_TRAFFIC_PLAYLIST_METRICS = (
    "views",
    "estimatedMinutesWatched",
    "playlistStarts",
    "viewsPerPlaylistStart",
    "averageTimeInPlaylist",
)


class FeatureAmount(Enum):
    ANY = auto()
    NON_ZERO = auto()
    ZERO_OR_ONE = auto()
    EXACTLY_ONE = auto()
    REQUIRED = auto()
