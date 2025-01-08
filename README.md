#

<div align="center">
<img alt="analytix logo" src="https://raw.githubusercontent.com/parafoxia/analytix/main/assets/logo.png" width="400px">
<br /><br />
A simple yet powerful SDK for the YouTube Analytics API.
<br /><br />
<a href="https://pypi.python.org/pypi/analytix"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/analytix"></a>
<a href="https://pypi.python.org/pypi/analytix"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/analytix"></a>
<a href="https://pypi.python.org/pypi/analytix"><img alt="PyPI - Implementation" src="https://img.shields.io/pypi/implementation/analytix"></a>
<hr />
</div>

## Features

* Pythonic syntax lets you feel right at home
* Dynamic error handling saves hours of troubleshooting and makes sure only valid requests count toward your API quota
* A clever interface allows you to make multiple requests across multiple sessions without reauthorising
* Extra support enables you to export reports in a variety of filetypes and to a number of DataFrame formats
* Easy enough for beginners, but powerful enough for advanced users

## Installation

### Installing analytix

To install the latest stable version of analytix, use the following command:

```sh
pip install analytix
```

You can also install the latest development version using the following command:

```sh
pip install git+https://github.com/parafoxia/analytix
```

You may need to prefix these commands with a call to the Python interpreter depending on your OS and Python configuration.

### Dependencies

Below is a list of analytix's dependencies.
Note that the minimum version assumes you're using CPython 3.8.
The latest versions of each library are always supported.

| Name              | Min. version | Required? | Usage                                                         | 
|-------------------|--------------|-----------|---------------------------------------------------------------|
| `urllib3`         | 2.2.0        | Yes       | Making HTTP requests                                          |
| `jwt`             | 1.2.0        | No        | Decoding JWT ID tokens (from v5.1)                            |
| `openpyxl`        | 3.0.0        | No        | Exporting report data to Excel spreadsheets                   |
| `pandas`          | ~1.3.0       | No        | Exporting report data to pandas DataFrames                    |
| `polars`          | 0.15.17      | No        | Exporting report data to Polars DataFrames                    |
| `pyarrow`         | ~5.0.0       | No        | Exporting report data to Apache Arrow tables and file formats |

## OAuth authentication

All requests to the YouTube Analytics API need to be authorised through OAuth 2.
In order to do this, you will need a Google Developers project with the YouTube Analytics API enabled.
You can find instructions on how to do that in the [API setup guide](https://parafoxia.github.io/analytix/starting/googleapp/).

Once a project is set up, analytix handles authorisation — including token refreshing — for you.

More details regarding how and when refresh tokens expire can be found on the [Google Identity documentation](https://developers.google.com/identity/protocols/oauth2#expiration).

## Usage

### Retrieving reports

The following example creates a CSV file containing basic info for the 10 most viewed videos, from most to least viewed, in the US in 2022:

```py
from datetime import date

from analytix import Client

client = Client("secrets.json")
report = client.fetch_report(
    dimensions=("video",),
    filters={"country": "US"},
    metrics=("estimatedMinutesWatched", "views", "likes", "comments"),
    sort_options=("-estimatedMinutesWatched",),
    start_date=date(2022, 1, 1),
    end_date=date(2022, 12, 31),
    max_results=10,
)
report.to_csv("analytics.csv")
```

If you want to analyse this data using additional tools such as *pandas*, you can directly export the report as a DataFrame or table using the `to_pandas()`, `to_arrow()`, and `to_polars()` methods of the report instance.
You can also save the report as a `.tsv`, `.json`, `.xlsx`, `.parquet`, or `.feather` file.

There are more examples in the [GitHub repository](https://github.com/parafoxia/analytix/tree/main/examples).

### Fetching group information

You can also fetch groups and group items:

```py
from analytix import Client

# You can also use the client as context manager!
with Client("secrets.json") as client:
    groups = client.fetch_groups()
    group_items = client.fetch_group_items(groups[0].id)
```

### Logging

If you want to see what analytix is doing, you can enable the packaged logger:

```py
import analytix

analytix.enable_logging()
```

This defaults to showing all log messages of level INFO and above.
To show more (or less) messages, pass a logging level as an argument.

## Compatibility

CPython versions 3.8 through 3.13 and PyPy versions 3.9 and 3.10 are officially supported\*.
CPython 3.14-dev is provisionally supported\*.
Windows, MacOS, and Linux are all supported.

*For base analytix functionality; support cannot be guaranteed for functionality requiring external libraries.

## Contributing

Contributions are very much welcome! To get started:

* Familiarise yourself with the [code of conduct](https://github.com/parafoxia/analytix/blob/main/CODE_OF_CONDUCT.md)
* Have a look at the [contributing guide](https://github.com/parafoxia/analytix/blob/main/CONTRIBUTING.md)

## License

The analytix module for Python is licensed under the [BSD 3-Clause License](https://github.com/parafoxia/analytix/blob/main/LICENSE).
