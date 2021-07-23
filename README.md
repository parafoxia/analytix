# analytix

[![PyPi version](https://img.shields.io/pypi/v/analytix.svg)](https://pypi.python.org/pypi/analytix/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/analytix.svg)](https://pypi.python.org/pypi/analytix/)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/analytix)](https://pypi.python.org/pypi/analytix/)
[![PyPI - Status](https://img.shields.io/pypi/status/analytix)](https://pypi.python.org/pypi/analytix/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/analytix)](https://pypi.python.org/pypi/analytix/)

[![Maintenance](https://img.shields.io/maintenance/yes/2021)](https://github.com/parafoxia/analytix)
[![GitHub Release Date](https://img.shields.io/github/release-date/parafoxia/analytix)](https://github.com/parafoxia/analytix)
[![GitHub last commit](https://img.shields.io/github/last-commit/parafoxia/analytix)](https://github.com/parafoxia/analytix)
[![Read the Docs](https://img.shields.io/readthedocs/analytix)](https://analytix.readthedocs.io/en/latest/index.html)
[![License](https://img.shields.io/github/license/parafoxia/analytix.svg)](https://github.com/parafoxia/analytix/blob/main/LICENSE)

A simple yet powerful API wrapper to make getting analytical information from the YouTube Analytics API easier than ever. More services are coming in the future.

## Features

- Pythonic syntax lets you feel right at home
- Dynamic error handling saves hours of troubleshooting, and makes sure only valid requests count toward your API quota
- A clever interface allows you to make multiple requests per session without reauthorising
- Extra support allows the native saving of CSV files and conversion to DataFrame objects
- Easy enough for beginners, but powerful enough for advanced users

## Installation

**You need Python 3.6.0 or greater to run analytix.** It is recommended you install analytix in a virtual environment.

To install the latest stable version of analytix, use the following command:
```sh
pip install analytix
```

To install with optional dependencies, use the following command:
```sh
pip install "analytix[opt]"
```

You can also install the latest development version using the following command:
```sh
pip install git+https://github.com/parafoxia/analytix.git@develop
```

You may need to prefix these commands with `py -m` or `python3.9 -m` (or similar) depending on your OS.

## Quickstart

Before you begin, you will need to have a Google Developers project with the YouTube Analytics API enabled. You can find instructions on how to do that in the [YouTube Analytics API docs](https://developers.google.com/youtube/reporting/v1/code_samples/python#set-up-authorization-credentials/).

Once you've done that, pulling reports down is easy. The below example loads credentials from a secrets file, and gets as much information as possible from the last 28 days.

```py
import datetime as dt

from analytix import YouTubeAnalytics

client = YouTubeAnalytics.from_file("./secrets.json")
start_date = dt.date.today() - dt.timedelta(days=28)
report = client.retrieve(start_date, dimensions=("day",))
report.to_csv("./analytics-28d.csv")
```

To read up further, [have a look at the documentation](https://analytix.readthedocs.io/en/latest/).

## License

The analytix module for Python is licensed under the [BSD-3-Clause License](https://github.com/parafoxia/analytix/blob/main/LICENSE).
