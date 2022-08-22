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
For example, if "day" and "country" (two incompatible dimensions) are both provided, analytix will select the "Geography-based activity" report type (as the "country" dimension is checked before the "day" dimension), and the "day" dimension will be flagged as invalid.

This provides a system with which to prevent invalid requests from counting toward your API quota, as well as one to detail the errors you make, something that the YouTube Analytics API doesn't do.

## Detailed report types

Some report types are stricter that others; they also have:

* A reduced set of valid sort options, separate to the set of valid metrics
* A maximum number of results (normally 200)

These report types are referred to internally as "detailed report types".
Oftentimes, they are also far more picky about what filters can be provided and the values that can be passed to them.

## List of report types

### Video report types

* Basic user activity
* Basic user activity (US)
* Time-based activity
* Time-based activity (US)
* Geography-based activity
* Geography-based activity (US)
* User activity by subscribed status
* User activity by subscribed status (US)
* Time-based playback details (live)
* Time-based playback details (view percentage)
* Geography-based playback details (live)
* Geography-based playback details (view percentage)
* Geography-based playback details (live, US)
* Geography-based playback details (view percentage, US)
* Playback locations
* Playback locations (detailed) [^1]
* Traffic sources
* Traffic sources (detailed) [^1]
* Device types
* Operating systems
* Device types and operating systems
* Viewer demographics
* Engagement and content sharing
* Audience retention
* Top videos by region [^1]
* Top videos by state [^1]
* Top videos by subscription status [^1]
* Top videos by YouTube product [^1]
* Top videos by playback detail [^1]

### Playlist report types

* Basic user activity for playlists
* Time-based activity for playlists
* Geography-based activity for playlists
* Geography-based activity for playlists (US)
* Playback locations for playlists
* Playback locations for playlists (detailed) [^1]
* Top sources for playlists
* Top sources for playlists (detailed) [^1]
* Device types for playlists
* Operating systems for playlists
* Device types and operating systems for playlists
* Viewer demographics for playlists
* Top playlists [^1]

### Ad performance report types

* Ad performance

[^1]: Detailed report type
