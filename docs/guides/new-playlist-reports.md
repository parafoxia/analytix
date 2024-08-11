# Migrating to new playlist reports

!!! info "See Also"
    You can read about the API changes in full on the [YouTube Analytics API documentation](https://developers.google.com/youtube/analytics/revision_history#january-19,-2024).

## Overview

The "isCurated" filter was deprecated by YouTube and ceased to work on 30 Jun 2024.
As a result, legacy playlist reports will no longer work.

From v5.3, only new playlist reports are supported (though v5.2 supported both new and legacy playlist reports).
Attempting to fetch playlist reports in earlier versions will raise an `APIError`.

There are no breaking changes to analytix's functionality outside of these API changes.

## What's different?

### Accessing playlist reports

Previously, analytix determined a report was a playlist report if the "isCurated" filter was provided.
Now, this determination is made based on whether any of these conditions are true:

* The "playlist" dimension is provided
* The "playlist" filter is provided
* The "group" filter and at least one playlist metric are provided

### Dimensions and filters

Most new playlist reports support far fewer dimensions and filters and most require you to filter either by playlist or by group.
The only exception is the "Top playlists" report which takes "playlist" as a dimension.

As an example, when fetching time-based playlist activity, this is possible using deprecated reports:

```py
# This will no longer work.
report = client.fetch_report(
    dimensions=("day", "youtubeProduct"),
    filters={
        "isCurated": "1",
        "playlist": "a1b2c3d4e5",
        "country": "US",
        "subscribedStatus": "SUBSCRIBED",
    },
)
assert report.type.name == "Time-based activity for playlists (deprecated)"
```

With the new reports, this is as close as you can get:

```py
report = client.fetch_report(
    dimensions=("day",),
    filters={
        "playlist": "a1b2c3d4e5",
    },
)
assert report.type.name == "Time-based activity for playlists"
```

### Metrics

YouTube Red-related metrics are not supported in new playlist reports, though some new metrics have been added:

* playlistAverageViewDuration
* playlistEstimatedMinutesWatched
* playlistSaves
* playlistViews

There are also now two types of playlist metrics:

* Aggregate video metrics, which look at all data for videos within a playlist (only supported when the "isCurated" filter is not provided)
* In-playlist metrics, which only look at data where the interactions happened *within the playlist itself*

Previously, all metrics were in-playlist.

Some metrics are making the switch between in-playlist and aggregate, an example being the "views" metric.
When the "isCurated" filter is provided, it acts as an *in-playlist* metric, otherwise it acts as an *aggregate* metric.
In this case, the "playlistViews" metric serves as the in-playlist equivalent to "views".

So this...

```py
report = client.fetch_report(
    metrics=("views",),
    filters={
        "isCurated": "1",
        "playlist": "a1b2c3d4e5",
    },
)
assert report.type.name == "Basic user activity for playlists (deprecated)"
```

...is equivalent to this:

```py
report = client.fetch_report(
    metrics=("playlistViews",),
    filters={
        "playlist": "a1b2c3d4e5",
    },
)
assert report.type.name == "Basic user activity for playlists"
```

Both can be selected in the same report, and analytix always does so where possible by default.
