# What are sort options?

## Overview

Sort options control how the report is sorted.
This is useful when you want data sorted by a particular metric instead of the default behaviour.

## Sorting reports

By default, reports are sorted by dimensions (from left to right), however you can sort the report by any metric by providing it as a sort option:

```py
sort_options=["views"]
```

This will sort all rows in the report by the number of views from lowest to highest.

## Sorting in descending order

If you wish to sort in descending order, prefix the metric with a hyphen:

```py
sort_options=["-views"]
```

This will now sort all rows from highest to lowest.

## Sorting by multiple metrics

To sort by multiple metrics, provide multiple sort options:

```py
sort_options=["views", "-likes", "comments"]
```

This will sort the report using the following rules:

* Sort all rows by the number of views from lowest to highest
* Sort all rows with the same number of views by the number of likes from highest to lowest
* Sort all rows with the same number of views and likes by the number of comments from lowest to highest

Note that the order *does* matter.
For example, putting "likes" first in the list would mean all rows are sorted by likes first.

## Valid sort options

See the list of [valid metrics](../metrics).
