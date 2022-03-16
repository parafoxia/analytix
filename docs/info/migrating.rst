Migrating to version 3
######################

.. important::
    This page only details changes and additions between versions 2.2.0 and 3.0.0. Make sure to check the `changelog <https://github.com/parafoxia/analytix/releases>`_ for updates beyond v3.0.0.

Breaking changes
================

* Python 3.6 is no longer supported

Analytics
---------

* The ``YouTubeAnalytics`` class is now called ``Analytics``
* The ``Analytics`` class is now imported as ``analytix.Analytics``
* The ``_token`` instance attribute is now ``_tokens``, and stores all tokens as a ``Tokens`` object instead of just the access token
* The ``secrets`` instance attribute is now a ``Secrets`` object rather than a dictionary
* The ``authorized`` property alias no longer exists
* The ``project_id`` property no longer exists
* The ``YouTubeAnalytics.from_file`` classmethod is now ``Analytics.with_secrets``
* The ``YouTubeAnalytics.from_dict`` classmethod no longer exists
* The ``authorise`` method
    * no longer provides the ``store_token`` keyword argument -- tokens are now always stored (though you can choose where)
    * no longer uses the ``requests_oauthlib.OAuth2Session`` to handle requests, so you can no longer pass those options
* The ``retrieve`` method
    * now takes ``start_date`` as a keyword argument rather than a positional one
    * now takes ``metrics=None`` as "all metrics" rather than ``metrics="all"``
    * now raises more specific errors, all of which subclasses of ``InvalidRequest``
* The ``daily_analytics``, ``monthly_analytics``, ``regional_analytics``, and ``top_videos`` methods no longer exist

Reports
-------

* The ``YouTubeAnalyticsReport`` class is now called ``Report``
* The ``Report`` class is now imported as ``analytix.reports.Report``
* The order of the ``data`` and ``type`` positional arguments to the constructor have been swapped
* Providing a tab as the delimiter in the ``to_csv`` method now automatically saves the file as a TSV
* The ``to_dataframe`` method will now raise a ``DataFrameConversionError`` if the data contains no rows

Beyond that, most of the backend functionality has been rewritten, and in some cases, completely redesigned.

New features
============

Async support
-------------

* The ``AsyncAnalytics`` class provides an asynchonous interface for ``Analytics``
* ``Report.ato_json`` and ``Report.ato_csv`` can be used to write files asynchonously

Typehinting
-----------

* analytix is now fully Mypy compliant (strict)

Token refreshing
----------------

* analytix is now capable of refreshing access tokens
* This can be done manually, but is generally handles automatically
* This means you no longer need to reauthorise analytix every hour

Update checks
-------------

* analytix now automatically checks for new versions once per session

100% test coverage
------------------

* analytix is now has 100% test coverage (about 15% more than version 2)
