from analytix import InvalidRequest
from analytix.youtube.abc import Features

YOUTUBE_ANALYTICS_DEFAULT_METRICS = (
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
YOUTUBE_ANALYTICS_DEFAULT_PROVINCE_METRICS = (
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


class Dimensions(Features):
    def __init__(self, none=False, req=[], opt=[], many=[]):
        super().__init__(none, req, opt, many)

    def verify(self, against):
        against = set(against)

        if self.none and against:
            raise InvalidRequest(f"expected 0 dimensions, got {len(against)}")

        every = self.every
        for f in against:
            if f not in every:
                raise InvalidRequest(f"unexpected dimension: {f}")

        for req in self.req:
            if len(against & req) != 1:
                raise InvalidRequest(f"expected 1 dimension from {req}, got {len(against)}")

        for opt in self.opt:
            if not 0 <= len(against & opt) <= 1:
                raise InvalidRequest(f"expected 0 or 1 dimensions from {opt}, got {len(against)}")

        for many in self.many:
            if len(against & many) == 0:
                raise InvalidRequest(f"expected at least 1 dimension from {many}, got {len(against)}")


class Filters(Features):
    def __init__(self, none=False, req=[], opt=[], many=[]):
        super().__init__(none, req, opt, many)

    def verify(self, against):
        if not isinstance(against, dict):
            raise InvalidRequest(f"expected dict of features, got {type(against).__name__}")
        against = set(against.keys())

        if self.none and against:
            raise InvalidRequest(f"expected 0 filters, got {len(against)}")

        every = self.every
        for f in against:
            if f not in every:
                raise InvalidRequest(f"unexpected filter: {f}")

        for req in self.req:
            if len(against & req) != 1:
                raise InvalidRequest(f"expected 1 filter from {req}, got {len(against)}")

        for opt in self.opt:
            if not 0 <= len(against & opt) <= 1:
                raise InvalidRequest(f"expected 0 or 1 filters from {opt}, got {len(against)}")

        for many in self.many:
            if len(against & many) == 0:
                raise InvalidRequest(f"expected at least 1 filter from {many}, got {len(against)}")
