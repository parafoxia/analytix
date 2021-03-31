Changelog
=========

v1.1.1
------

Fixed bug that meant JSON reports could not be saved.

v1.1.0
------

- Added playlist report type support.
- If no specific report type could be determined, analytix now falls back to a basic user activity report.
- A few minor efficient enhancements.

v1.0.2
------

- Fixed ordering issue.

v1.0.1
------

- Fixed an issue with report type that have required and optional dimensions.
- Fixed some stuff in the docs.

v1.0.0
------

- Corrected some bugs in rc1.
- Added some extra verification.
- Made some messages look a little nicer, especially some error messages.
- Made it impossible to install on unsupported versions.
- Corrected some issues in the docs.

v1.0.0rc1
---------

.. warning::

    This release contains multiple breaking changes. Code written using v0.1.0 will not function from this version.

- The number of supported video report types has increased from 6 to 29 (though playlist report types have been temporarily removed -- they'll be back in v1.1).
- There is now just one class that caters for all report types, rather than a separate class for each one.
- You no longer need to specify which scopes to use.
- :code:`start_date` is now optional.
- You can now choose to bypass request verification.
- All available metrics are used by default if none are passed by the user.

v0.1.0
------

Added support for the following report types:

- Geographical data
- Basic user data for playlists
- Time based data for playlists
- Geographical data for playlists

v0.1.0a2
--------

- Adds the :code:`YouTubeService.authorize` alias.
- Adds auto-docs.

v0.1.0a1
--------

The first release on PyPI. Added the base code, and some basic classes:

- :code:`BasicYouTubeAnalytics`
- :code:`TimeBasedYouTubeAnalytics`

Also added the ability to save the report as a JSON or a CSV.
