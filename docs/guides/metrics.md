# What are metrics?

## Overview

Metrics define the information you wish to retrieve, and every provided metric is a column in the report (always to the right of all dimensions).
This is useful when you want to fine-tune exactly what information you retrieve.

All metric data is numeric.

## Selecting metrics

The YouTube Analytics API defines many report types (for which there is a [separate guide](../report-types)), and each defines a different set of valid metrics.
It can be difficult to tell exactly which metrics are valid for each report, but if you're not sure, you may not have to worry.
If you do not provide any metrics when retrieving reports, analytix will automatically include every metric the report type supports in the report.
This means you only ever need to supply a series of metrics if you want your report to focus on very specific information.

## Valid metrics

* views [^1]
* redViews
* comments [^1]
* likes [^1]
* dislikes [^1]
* videosAddedToPlaylists
* videosRemovedFromPlaylists
* shares [^1]
* estimatedMinutesWatched [^1]
* estimatedRedMinutesWatched
* averageViewDuration [^1]
* averageViewPercentage
* annotationClickThroughRate [^1]
* annotationCloseRate [^1]
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
* subscribersGained [^1]
* subscribersLost [^1]
* estimatedRevenue [^1]
* estimatedAdRevenue
* grossRevenue
* estimatedRedPartnerRevenue
* monetizedPlaybacks
* playbackBasedCpm
* adImpressions
* cpm
* viewerPercentage [^1]
* audienceWatchRatio
* relativeRetentionPerformance
* playlistStarts
* viewsPerPlaylistStart
* averageTimeInPlaylist

[^1]: Core metric (subject to YouTube’s deprecation policy)
