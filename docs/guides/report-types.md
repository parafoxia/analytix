# What are report types?

## Overview

Report types define what can be provided in a request.
analytix automatically selects the most appropriate report type based on the dimensions, filters, and metrics you provide, so it is probably easier to think of report types as a single standard for validating requests.

## Validation

Each report type has a set of valid:

* Dimensions
* Filters
* Metrics
* Sort options (usually the same as the valid metrics)

After a report type is selected by analytix, the provided attributes are compared against the valid ones for that report type, and errors are thrown on mismatches.
For example, if "day" and "country" (two incompatible dimensions) are both provided, analytix will detect this and throw an error.
From v4.1.4, these errors are much clearer.

This provides a system with which to prevent invalid requests from counting toward your API quota, as well as one to detail the errors you make, something that the YouTube Analytics API doesn't do.

## Detailed report types

Some report types are stricter that others; they also have:

* A reduced set of valid sort options, separate to the set of valid metrics
* A maximum number of results (normally 200)

These report types are referred to internally as "detailed report types".
Oftentimes, they are also far more picky about what filters can be provided and the values that can be passed to them.

## List of report types

Below is a list of all possible report types, complete with links to official documentation resources.

!!! warning
    The official documentation is not 100% accurate.
    analytix does account for this wherever possible, but note some behaviour may not be as expected.

!!! note
    Content owner reports are not supported.

### Video report types

* [Basic user activity](https://developers.google.com/youtube/analytics/channel_reports#basic-user-activity-statistics)
* [Basic user activity (US)](https://developers.google.com/youtube/analytics/channel_reports#basic-user-activity-statistics-for-u.s.-states)
* [Time-based activity](https://developers.google.com/youtube/analytics/channel_reports#user-activity-by-country-for-specific-time-periods)
* [Time-based activity (US)](https://developers.google.com/youtube/analytics/channel_reports#user-activity-in-u.s.-states-for-specific-time-periods)
* [Geography-based activity](https://developers.google.com/youtube/analytics/channel_reports#user-activity-by-country)
* [Geography-based activity (US)](https://developers.google.com/youtube/analytics/channel_reports#user-activity-by-province)
* [Geography-based activity (by city)](https://developers.google.com/youtube/analytics/channel_reports#user-activity-by-city-=-250-results) [^1] [^2]
* [User activity by subscribed status](https://developers.google.com/youtube/analytics/channel_reports#user-activity-by-subscribed-status)
* [User activity by subscribed status (US)](https://developers.google.com/youtube/analytics/channel_reports#user-activity-by-subscribed-status-for-provinces)
* [Time-based playback details (live)](https://developers.google.com/youtube/analytics/channel_reports#playback-details-with-optional-time-dimension-and-liveorondemand-statistics)
* [Time-based playback details (view percentage)](https://developers.google.com/youtube/analytics/channel_reports#playback-details-with-optional-time-dimension-and-averageviewpercentage-metric)
* [Geography-based playback details (live)](https://developers.google.com/youtube/analytics/channel_reports#playback-details-by-country-with-liveorondemand-statistics)
* [Geography-based playback details (view percentage)](https://developers.google.com/youtube/analytics/channel_reports#playback-details-by-country-with-averageviewpercentage-metric)
* [Geography-based playback details (live, US)](https://developers.google.com/youtube/analytics/channel_reports#playback-details-by-province-with-liveorondemand-statistics)
* [Geography-based playback details (view percentage, US)](https://developers.google.com/youtube/analytics/channel_reports#playback-details-by-province-with-averageviewpercentage-metric)
* [Playback locations](https://developers.google.com/youtube/analytics/channel_reports#video-playback-location-report)
* [Playback locations (detailed)](https://developers.google.com/youtube/analytics/channel_reports#playback-location-detail-=-25-results) [^1]
* [Traffic sources](https://developers.google.com/youtube/analytics/channel_reports#traffic-source)
* [Traffic sources (detailed)](https://developers.google.com/youtube/analytics/channel_reports#traffic-source-detail-=-25-results) [^1]
* [Device types](https://developers.google.com/youtube/analytics/channel_reports#device-type)
* [Operating systems](https://developers.google.com/youtube/analytics/channel_reports#operating-system)
* [Device types and operating systems](https://developers.google.com/youtube/analytics/channel_reports#operating-system-and-device-type)
* [Viewer demographics](https://developers.google.com/youtube/analytics/channel_reports#demographic-reports)
* [Engagement and content sharing](https://developers.google.com/youtube/analytics/channel_reports#social-reports)
* [Audience retention](https://developers.google.com/youtube/analytics/channel_reports#audience-retention-reports)
* [Top videos by region](https://developers.google.com/youtube/analytics/channel_reports#top-videos-with-optional-regional-filters-=-200-results) [^1]
* [Top videos by state](https://developers.google.com/youtube/analytics/channel_reports#top-videos-by-state-=-200-results) [^1]
* [Top videos by subscription status](https://developers.google.com/youtube/analytics/channel_reports#top-videos-for-subscribed-or-unsubscribed-viewers=-200-results) [^1]
* [Top videos by YouTube product](https://developers.google.com/youtube/analytics/channel_reports#top-videos-by-youtube-product-=-200-results) [^1]
* [Top videos by playback detail](https://developers.google.com/youtube/analytics/channel_reports#top-videos-with-playback-detail-filters-=-200-results) [^1]

### Playlist report types

* [Basic user activity for playlists](https://developers.google.com/youtube/analytics/channel_reports#basic-stats-playlist-reports)
* [Time-based activity for playlists](https://developers.google.com/youtube/analytics/channel_reports#time-based-playlist-reports)
* [Geography-based activity for playlists](https://developers.google.com/youtube/analytics/channel_reports#playlist-activity-by-country)
* [Geography-based activity for playlists (US)](https://developers.google.com/youtube/analytics/channel_reports#playlist-activity-by-province)
* [Playback locations for playlists](https://developers.google.com/youtube/analytics/channel_reports#playback-location-playlist-reports)
* [Playback locations for playlists (detailed)](https://developers.google.com/youtube/analytics/channel_reports#playback-location-detail-=-25-results_1) [^1]
* [Traffic sources for playlists](https://developers.google.com/youtube/analytics/channel_reports#traffic-source-playlist-reports)
* [Traffic sources for playlists (detailed)](https://developers.google.com/youtube/analytics/channel_reports#traffic-source-detail-=-25-results_1) [^1]
* [Device types for playlists](https://developers.google.com/youtube/analytics/channel_reports#device-type_1)
* [Operating systems for playlists](https://developers.google.com/youtube/analytics/channel_reports#operating-system_1)
* [Device types and operating systems for playlists](https://developers.google.com/youtube/analytics/channel_reports#operating-system-and-device-type_1)
* [Viewer demographics for playlists](https://developers.google.com/youtube/analytics/channel_reports#demographic-playlist-reports)
* [Top playlists](https://developers.google.com/youtube/analytics/channel_reports#top-playlists-reports) [^1]

### Ad performance report types

* [Ad performance](https://developers.google.com/youtube/analytics/channel_reports#ad-performance-by-ad-type)

[^1]: Detailed report type
[^2]: The documentation for this report type is incorrect (as of 15 Jan 2023). The actual max number of results is 25.
