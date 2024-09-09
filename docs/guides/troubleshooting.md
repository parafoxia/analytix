# Troubleshooting

## I'm getting a 400: Bad Request error

There are two instances where you could expect to see this:

* When fetching geography-based activity by city with more than 25 rows
* When filtering by a non-existent or private video

If this error is raised under any other circumstances, it's probably a bug in analytix's validation system.
[Submit a bug report!](https://github.com/parafoxia/analytix/issues/new/choose)

## I'm getting a 403: Forbidden error

If you're receiving 403: Forbidden errors from the API, you are most likely trying to get monetary data from a non-partnered channel.
From v5.0, analytix will not attempt to fetch monetary data unless instructed to, but earlier versions will by default, potentially triggering the error.

To resolve the issue, pass `scopes=Scopes.READONLY` to the client constructor (this is the default from v5.0):

```py
from analytix import Client, Scopes

client = Client("secrets.json", scopes=Scopes.READONLY)
```

## My refresh token keeps expiring

This has nothing to do with analytix, but is worth knowing.
By default, refresh tokens only last for 7 days before expiring, forcing you to reauthorise from scratch.
You'll need to publish your application if you want more time.

## I'm getting an `InvalidRequest` error

The YouTube Analytics API is a collection of [report types](./report-types.md), and all requests must abide by at least one of these.
While analytix makes things easier by inferring which report type you want, it will throw one of these errors if the report type can't be extrapolated.

Typically, these errors serve as an FYI and can only be resolved by checking the [Channel Reports documentation](https://developers.google.com/youtube/analytics/channel_reports#video-reports).

The wording of these errors can provide hints on what exactly is wrong.
For example, any message containing the word "invalid" indicates you've included something the YouTube Analytics API itself doesn't support.
Otherwise, the issue probably relates to the combination of dimensions, filters, metrics, and sort options not being supported by any report types.

Some messages have additional caveats:

### Invalid value 'x' for filter 'y'

If you see this, you're filtering by a valid attribute but with an unsupported value.

Some filters, such as "operatingSystem", can only accept one of a possible set of values.
If these are string values, they are typically all upper-case.
A few filters require more thought and research than others; for example, where the "country" filter accepts ISO 3166-1 country codes, which are letters, the "continent" filter accepts UN M49 codes, which are numeric.

A list of all available filters, as well as all their supported values, is provided in the _[What are filters?](./filters.md)_ guide.

### Sort option 'x' is not part of the given metrics

The set of sort options must be a subset of the provided (or inferred) metrics.

If you need to sort the report by a metric you don't want to include in the report, you will have to provide the metric initially and drop the column in postprocessing.

### Anything else

Check the [Channel Reports documentation](https://developers.google.com/youtube/analytics/channel_reports#video-reports).
[Enabling debug logging](../reference/ux.md) should help you track down what you need to find.
