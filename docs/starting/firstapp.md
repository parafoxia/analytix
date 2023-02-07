# Creating your first analytix program

## Creating a client

In order to make requests to the YouTube Analytics API, you need a client.
analytix provides a few different clients you can use; to find out the differences between them, see the [client documentation](../reference/client.md).
For this guide, we'll just use the standard `Client`.

You can create a client like so:

```py
from analytix import Client

client = Client("secrets.json")
```

Here, we're telling the client we want to use the secrets file we downloaded when we [created our Google Developers application](./googleapp.md).

There is also another way to create our client:

```py
with Client("secrets.json") as client:
    ...
```

By using a context manager, the client will automatically tear itself down once outside of that block.
Creating a client the other way means we would need to manually call `client.teardown()` to do the same thing.
The way you create your client is up to you, but bear that difference in mind.

!!! info
    If you are looking to build an async application, the [`AsyncClient`](../reference/client.md#analytix.client.AsyncClient) would be more suited to you.
    For web application development, you will probably want the [`AsyncBaseClient`](../reference/client.md#analytix.client.AsyncBaseClient)

## Authorisation

While your client will authorise itself where necessary, it's worth knowing how it goes about doing so.

When your client first authorises itself, it will prompt you to follow an OAuth 2 flow in order to get the necessary access token for the API.
This just involves signing into Google and giving your Google Developers application permission to access your analytics data.
Your client will then store your access and refresh tokens, and attempt to use them in future requests.
If your access token cannot be used or refreshed, you will need to reauthorise from scratch.

Your Google Developers application is probably in "Testing" mode (if you're not sure, it definitely is), which means your refresh token will expire after seven days.
To extend this time, you will need to publish your application, though this is never necessary when using analytix for your own personal projects.

!!! info
    You can manually authorise your client using the [`client.authorise()`](../reference/client.md#analytix.client.Client.authorise) method if you wish. This is particularly helpful when you are trying to pull data from multiple channels.

## Retrieving analytics data

Now the real fun begins!

Retrieving an analyrics report is simple:

```py
report = client.retrieve_report()
```

Unfortunately, deciding what data you want in the report given the constraints imposed by the API is more complicated.
Let's run over some examples:

```py
from datetime import date

report = client.retrieve_report(
    dimensions=("day",),
    start_date=date(2022, 1, 1),
    end_date=date(2022, 12, 31),
)
```

The above example gets your day-by-day analytics for the 2022 calendar year -- each row in the resultant report will be for a different day.

Now let's spice it up a bit:

```py
report = client.retrieve_report(
    dimensions=("video",),
    filters={"subscribedStatus": "UNSUBSCRIBED"},
    sort_options=("-views"),
    start_date=date(2022, 1, 1),
    end_date=date(2022, 12, 31),
    max_results=10,
)
```

This more complex example gets the ten best performing videos (by views) in the 2022 calendar year for unsubscribed viewers.

There's a lot more to creating reports than this though, which is why there is some [helpful guides](../guides/dimensions.md) which should hopefully help.

## Processing and saving analytics data

Once you have your reports, you can either process them using a data manipulation library such as pandas, or save them to disk.

pandas, Arrow, and Polars are all supported natively:

=== "pandas"
    ```py
    df = report.to_pandas()
    ```

=== "Arrow"
    ```py
    table = report.to_arrow()
    ```

=== "Polars"
    ```py
    df = report.to_polars()
    ```

If you want to save your reports to disk, you can do so in a few ways:

=== "CSV"
    ```py
    report.to_csv("output.csv")
    ```

=== "JSON"
    ```py
    report.to_json("output.json")
    ```

=== "Excel"
    ```py
    report.to_excel("output.xlsx")
    ```

## What next?

Now you've got some analytix experience under your belt, you can move onto bigger and better things.
Here's some good places to go next:

* [The `Client` reference](../reference/client.md#analytix.client.Client)
* [The guides (especially the one about report types)](../guides/report-types.md)
* [The example store](https://github.com/parafoxia/analytix/tree/main/examples)

If you ever get stuck, feel free to [start a discussion](https://github.com/parafoxia/analytix/discussions)!
