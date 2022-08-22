# Dependencies

This guide will go through all of analytix's required and optional dependencies.

## Required

* python-dateutil >= 2.7 — used to convert timezone-aware datetimes of groups
* requests >= 2.19 — used to make API requests

## Optional

* openpyxl >= 3.0 — required when exporting reports to Excel spreadsheets
* pandas >= 0.23.2 — required when creating pandas DataFrames from reports
* polars >= 0.14.4 — required when creating Polars DataFrames from reports
* pyarrow >= 2.0 — required when creating Apache Arrow tables from reports
