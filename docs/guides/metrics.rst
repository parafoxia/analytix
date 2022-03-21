Understanding metrics
#####################

Overview
========

Metrics define the information you wish to retrieve, and every provided metric is a column in the report (always to the right of all dimensions). This is useful when you want to fine-tune exactly what information you retrieve.

There is a case to be made that you never need to worry about metrics; if you do not provide any metrics when retrieving reports, analytix will automatically include every metric the report type supports in the report.

All metric data is numeric.

Valid metrics
=============

Below is a list of available metrics. When no metrics are provided, the metrics will be sorted in this order in the report.

- views [#f3]_
- redViews
- comments [#f3]_
- likes [#f3]_
- dislikes [#f3]_
- videosAddedToPlaylists
- videosRemovedFromPlaylists
- shares [#f3]_
- estimatedMinutesWatched [#f3]_
- estimatedRedMinutesWatched
- averageViewDuration [#f3]_
- averageViewPercentage
- annotationClickThroughRate [#f3]_
- annotationCloseRate [#f3]_
- annotationImpressions
- annotationClickableImpressions
- annotationClosableImpressions
- annotationClicks
- annotationCloses
- cardClickRate
- cardTeaserClickRate
- cardImpressions
- cardTeaserImpressions
- cardClicks
- cardTeaserClicks
- subscribersGained [#f3]_
- subscribersLost [#f3]_
- estimatedRevenue [#f3]_
- estimatedAdRevenue
- grossRevenue
- estimatedRedPartnerRevenue
- monetizedPlaybacks
- playbackBasedCpm
- adImpressions
- cpm
- viewerPercentage [#f3]_
- audienceWatchRatio
- relativeRetentionPerformance
- playlistStarts
- viewsPerPlaylistStart
- averageTimeInPlaylist

.. [#f3] Core metric (subject to YouTube's deprecation policy)

For more information about what each metric does, look at the `official documentation <https://developers.google.com/youtube/analytics/metrics>`_.
