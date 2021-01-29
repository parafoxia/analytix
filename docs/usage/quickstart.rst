Quickstart
==========

This provides a useful set of basic examples to help you get started with analytix.

.. important::

    You need to have created a Google Developers project with the YouTube Analytics API enabled in order to use analytix. You can find instructions on how to do that in the `YouTube Analytics API Docs`_.

.. _YouTube Analytics API Docs: https://developers.google.com/youtube/reporting/v1/code_samples/python#set-up-authorization-credentials/

Creating a YouTube Service
--------------------------

All requests to the YouTube Analytics API need to be authorised. To make this easier, analytix provides a :code:`YouTubeService` object.

.. code-block:: py

    from analytix.youtube import YouTubeService

You can then create the service using a secrets file (you can also pass a dictionary of credentials):

.. code-block:: py

    service = YouTubeService("./secrets.json")

Before the service can be authorised, you need to decide what scopes you want to use.

.. list-table::
    :widths: 25 75

    * - Scope
      - Description
    * - yt-analytics.readonly
      - View YouTube Analytics reports for your YouTube content. This scope provides access to user activity metrics, like view counts and rating counts.
    * - yt-analytics-monetary.readonly
      - View YouTube Analytics monetary reports for your YouTube content. This scope provides access to user activity metrics and to estimated revenue and ad performance metrics.

Once you have decided on the scopes you want, you can pass them into the :code:`authorise` method as a series of args:

.. code-block:: py

    service.authorise("yt-analytics.readonly", "yt-analytics-monetary.readonly")

From there, follow the authorisation flow, and you're good to go!

Getting Basic User Activity
---------------------------

Once you have authorised a service, you can start pulling data from the API. analytix provides a number of classes to get different types of reports, but for this example we will just grab some basic activity information using the :code:`BasicYouTubeAnalytics` class. We also need to import the :code:`datetime` module for this example:

.. code-block:: py

    import datetime as dt

    from analytix.youtube import BasicYouTubeAnalytics

From there, create an object to perform operations on:

.. code-block:: py

    analytics = BasicYouTubeAnalytics(service)

Now you can actually pull data from the API. To do this, you use the :code:`retrieve` method. This method takes a number of options, but we will use the most basic (and only required) options: :code:`metrics` and :code:`start_date`. This snippet pulls the number of views, likes, and comments in the last 28 days:

.. code-block:: py

    report = analytics.retrieve(
        ("views", "likes", "comments"),
        start_date=dt.date.today() - dt.timedelta(days=28),
    )

The :code:`retrieve` method returns a :code:`YouTubeAnalyticsReport` object, which can be exported to either the JSON or CSV format:

.. code-block:: py

    report.to_json("./analytics.json")
    report.to_csv("./analytics.csv")

And that's it! From here, you can :doc:`find more examples<./examples>`, or browse through the :doc:`API docs<../api>`.
