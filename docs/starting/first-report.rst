Retrieving your first YouTube Analytics report
##############################################

This section will run you through the basics of using analytix, and provide an example you can use to retrieve your first report from the YouTube Analytics API. In order to follow this, you will need to have a Google Developers project with the YouTube Analytics API enabled. You also need your :code:`secrets.json` file to hand. If you don't already have these, you can learn from the :doc:`relevant documentation <../refs/yt-analytics-setup>`.

Setting up
==========

All requests to the YouTube Analytics API need to be authorised. analytix provides a client class which makes this process easier, which can be imported like so:

.. code-block:: python

    from analytix import YouTubeAnalytics

You then need to pass your project secrets to the client for it to use. You can do this in two ways:

.. code-block:: python

    # Method 1: Loading directly from the secrets.json file
    client = YouTubeAnalytics.from_file("/path/to/secrets.json")

    # Method 2: Taking the secrets from a dictionary
    secrets_dict = {...}
    client = YouTubeAnalytics.from_dict(secrets_dict)

analytix will prompt you for authorisation when it's needed, but you can authorise the client manually if you want to:

.. code-block:: python

    client.authorise()

.. note::

    You will need to authorise the service manually if you do not want the token to be stored for future use. To do this, pass :code:`store_token=False` to the method.

Retrieving a report
===================

You can retrieve reports using the client's :code:`retrieve` method. This method takes a series of parameters and returns a :class:`YouTubeAnalyticsReport` instance with the retrieved data. Seen as this is your first report, we'll make it simple and just get data on views, likes, and comments for the last 28 days. You can do that with the following:

.. code-block:: python

    import datetime as dt

    report = client.retrieve(
        dt.date.today() - dt.timedelta(days=28),
        metrics=("views", "likes", "comments"),
        dimensions=("day",),
    )

.. note::

    If you're retrieving reports containing revenue data, some dates may be missing as revenue analytics are typically delayed by a few days. analytix does not account for this.

In this example, the first argument (:code:`dt.date.today() - dt.timedelta(days=28)`) is the date in which data should be collected from. You need to supply this for every request you make. It must also be a :code:`datetime.date` object, and *not* a :code:`datetime.datetime` object.

Once the report has been retrieved, you can either save it as a JSON file, save it as a CSV file, or convert it to a pandas DataFrame (provided pandas is currently installed). Note that the JSON file would contain the raw data from the API:

.. code-block:: python

    report.to_json("./analytics.json")
    report.to_csv("./analytics.csv")
    df = report.to_dataframe()

And that's it! There are millions of different reports you can retrieve, so why not experiment! If you get stuck, have a look at the :doc:`library reference <../app/yt-analytics>` or the :doc:`report reference <../refs/yt-analytics-reports>`.
