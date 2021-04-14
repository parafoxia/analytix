Metrics, dimensions, and filters
================================

Metrics
-------

Metrics are essentially the columns of the report. Each metric is a different bit of information; passing the "views" metric would mean that information regarding views is included in the report. Different report types accept different metrics, and some accept all of them. If you do not provide any metrics, analytix will automatically use all available metrics for that report type.

Here is a full list of metrics you can use:

* views
* redViews
* comments
* likes
* dislikes
* videosAddedToPlaylists
* videosRemovedFromPlaylists
* shares
* estimatedMinutesWatched
* estimatedRedMinutesWatched
* averageViewDuration
* averageViewPercentage
* annotationClickThroughRate
* annotationCloseRate
* annotationImpressions
* annotationClickableImpressions
* annotationClosableImpressions
* annotationClicks
* annotationCloses
* cardClickRate
* cardTeaserClickRate
* cardImpressions
* cardTeaserImpressions
* cardClicks
* cardTeaserClicks
* subscribersGained
* subscribersLost
* estimatedRevenue
* estimatedAdRevenue
* grossRevenue
* estimatedRedPartnerRevenue
* monetizedPlaybacks
* playbackBasedCpm
* adImpressions
* cpm

Dimensions
----------

Dimensions are used to "split" data per se; if you were to provide no dimensions, you would get a single row, but if you were to provide "day" as a dimension, you could get a row for every individual date included in the report. Some report types allow you to pass multiple dimensions which split the data twice; if you passed the "day" and "subscribedStatus" dimension, you would get two rows for each day -- one for subscribed viewers, and one for unsubscribed viewers. analytix primarily uses these dimensions to determine what type of report you want.

Here is a full list of dimensions you can use:

* day
* month
* country
* province
* subscribedStatus
* liveOrOnDemand
* youtubeProduct
* insightPlaybackLocationType
* insightPlaybackLocationDetail
* insightTrafficSourceType
* insightTrafficSourceDetail
* deviceType
* operatingSystem
* ageGroup
* gender
* sharingService
* elaspedVideoTimeRatio
* audienceWatchRatio
* relativeRetentionPerformance
* playlist
* adType

Filters
-------

Filters are used to filter the data...obviously. However, like metrics and dimensions, only certain filters can be used with certain reports.

Here is a full list of filters you can use (valid values for each will come in a future doc version):

* country
* continent
* subContinent
* video
* group
* province
* subscribedStatus
* liveOrOnDemand
* youtubeProduct
* insightPlaybackLocationType
* insightTrafficSourceType
* operatingSystem
* deviceType
* audienceType
* isCurated
* playlist

.. Report types
.. ------------

.. The YouTube Analytics API provides 42 unique report types, all with different requirements. analytix automatically determines the report type you want based on the metrics, dimensions, and filters you give it.
