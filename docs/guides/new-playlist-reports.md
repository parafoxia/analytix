# Migrating to new playlist reports

!!! warning
    This page details actions to mitigate breaking changes in the YouTube Analytics API.
    You will need to complete these migrations by 30 Jun 2024 in order to use playlist reports.

!!! info "See also"
    You can read about the API changes in full on the [YouTube Analytics API documentation](https://developers.google.com/youtube/analytics/revision_history#january-19,-2024).

## Overview

The "isCurated" filter has been deprecated by YouTube and will cease to work on 30 Jun 2024.
As a result, all playlist reports will be changing, as will the way in which you create them.

Support for the new playlist reports was introduced in v5.2.
Deprecated playlist reports will continue to work in analytix until at least v5.3.

There will be no breaking changes to analytix's functionality outside of these API changes.

## What's different?

### Accessing playlist reports

For now, if the "isCurated" filter is provided, a deprecated playlist report is returned (this will error in future versions of analytix).
New playlist reports are returned if any of the following conditions are true:

* The "playlist" dimension is provided
* The "playlist" filter is provided
* The "group" filter and at least one playlist metric are provided

### Dimensions and filters

Most new playlist reports support far fewer dimensions and filters and most require you to filter either by playlist or by group.
The only exception is the "Top playlists" report which takes "playlist" as a dimension.

As an example, when fetching time-based playlist activity, this is possible using deprecated reports:

```py
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
