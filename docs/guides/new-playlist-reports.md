# Working with new playlist reports

!!! info "See also"
    You can read about the API changes in full on the [YouTube Analytics API documentation](https://developers.google.com/youtube/analytics/revision_history#january-19,-2024).

## Overview

The YouTube Analytics API is introducing a new style of playlist report that is incompatible from the old one.
Old style playlist reports will stop working on 30 Jun 2024, so you need to make sure you're using the new playlist reports before then.
Old playlist reports were deprecated in v5.1.2, and support for new playlist reports will be introduced in v5.2.
Support for old playlist reports will be removed in a future analytix version.

## What's changing?

The following filters are being REMOVED from playlist reports:

* isCurated
* All location filters

The following dimensions are being REMOVED from playlist reports:

* subscriberStatus
* youtubeProduct

The following metrics are being REMOVED from playlist reports:

* All YouTube Red metrics

The following metrics are being ADDED to playlist reports:

* playlistAverageViewDuration
* playlistEstimatedMinutesWatched
* playlistSaves
* playlistViews

You will also need to now provide one of either `playlist` or `group`.
This is how analytix will distinguish playlist reports.

## How is analytix handling it?

Support for new playlist reports will be introduced in v5.2, and will co-exist alongside old playlist reports.
Old playlist reports will remain until at least v5.3 -- they will be removed as near to the removal date as possible.
There will be no breaking changes to analytix's functionality outside of these changes.
