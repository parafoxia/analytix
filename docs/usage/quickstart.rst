Quickstart
==========

This provides a useful set of basic examples to help you get started with analytix.

.. important::

    You need to have created a Google Developers project with the YouTube Analytics API enabled in order to use analytix. You can find instructions on how to do that in the `YouTube Analytics API Docs`_.

.. _YouTube Analytics API Docs: https://developers.google.com/youtube/reporting/v1/code_samples/python#set-up-authorization-credentials/

Creating a YouTube service
--------------------------

All requests to the YouTube Analytics API need to be authorised. To make this easier, analytix provides a :code:`YouTubeService` object.

.. code-block:: py

    from analytix.youtube import YouTubeService

You can then create the service using a secrets file (you can also pass a dictionary of credentials):

.. code-block:: py

    service = YouTubeService("./secrets.json")

You can authorise your service by simply doing the following:

.. code-block:: py

    service.authorise()

From there, follow the authorisation flow, and you're good to go!

Getting basic user activity
---------------------------

Once you have authorised a service, you can start pulling data from the API. From v1.0.0, analytix uses a single class to get any report, regardless of type. Alongside that, we also need to import the :code:`datetime` module for this example:

.. code-block:: py

    import datetime as dt

    from analytix.youtube import YouTubeAnalytics

From there, create an object to perform operations on:

.. code-block:: py

    analytics = YouTubeAnalytics(service)

Now you can actually pull data from the API. To do this, you use the :code:`retrieve` method. This method takes a number of options, but we will use the most basic (and only required) options: :code:`metrics` and :code:`start_date`. This snippet pulls the number of views, likes, and comments in the last 90 days:

.. code-block:: py

    report = analytics.retrieve(
        metrics=("views", "likes", "comments"),
        start_date=dt.date.today() - dt.timedelta(days=90),
    )

The :code:`retrieve` method returns a :code:`YouTubeAnalyticsReport` object, which can be exported to either the JSON or CSV format:

.. code-block:: py

    report.to_json("./analytics.json")
    report.to_csv("./analytics.csv")

And that's it! From here, you can :doc:`find more examples<./examples>`, or browse through the :doc:`API docs<../api>`.
