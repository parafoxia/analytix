# analytix

[![PyPi version](https://img.shields.io/pypi/v/analytix.svg)](https://pypi.python.org/pypi/analytix/)
[![PyPI - Status](https://img.shields.io/pypi/status/analytix)](https://pypi.python.org/pypi/analytix/)
[![Downloads](https://pepy.tech/badge/analytix)](https://pepy.tech/project/analytix)
[![GitHub last commit](https://img.shields.io/github/last-commit/parafoxia/analytix)](https://github.com/parafoxia/analytix)
[![License](https://img.shields.io/github/license/parafoxia/analytix.svg)](https://github.com/parafoxia/analytix/blob/main/LICENSE)

[![CI (Tests)](https://github.com/parafoxia/analytix/actions/workflows/ci-tests.yml/badge.svg)](https://github.com/parafoxia/analytix/actions/workflows/ci-tests.yml)
[![Read the Docs](https://img.shields.io/readthedocs/analytix)](https://analytix.readthedocs.io/en/latest/index.html)
[![Maintainability](https://api.codeclimate.com/v1/badges/8819bdebb2d4aa8dfcb7/maintainability)](https://codeclimate.com/github/parafoxia/analytix/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/8819bdebb2d4aa8dfcb7/test_coverage)](https://codeclimate.com/github/parafoxia/analytix/test_coverage)

A simple yet powerful wrapper for the YouTube Analytics API.

CPython versions 3.6 through 3.11-dev and PyPy versions 3.6 and 3.7 are officially supported.

Windows, MacOS, and Linux are all supported.

## Features

- Pythonic syntax lets you feel right at home
- Dynamic error handling saves hours of troubleshooting, and makes sure only valid requests count toward your API quota
- A clever interface allows you to make multiple requests across multiple sessions without reauthorising
- Extra support allows the native saving of CSV files and conversion to DataFrame objects
- Easy enough for beginners, but powerful enough for advanced users

## Installation

**You need Python 3.6.0 or greater to run analytix.**

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
pip install git+https://github.com/parafoxia/analytix
```

You may need to prefix these commands with a call to the Python interpreter depending on your OS and Python configuration.

## Quickstart

Before you begin, you will need to have a Google Developers project with the YouTube Analytics API enabled. You can find instructions on how to do that in the [API setup guide](https://analytix.readthedocs.io/en/latest/refs/yt-analytics-setup.html).

Once you've done that, retrieving reports is easy. The below example loads credentials from a secrets file, and gets as much information as possible from the last 28 days.

```py
import datetime as dt

from analytix import YouTubeAnalytics

client = YouTubeAnalytics.from_file("./secrets.json")
start_date = dt.date.today() - dt.timedelta(days=28)
report = client.retrieve(start_date, dimensions=("day",))
report.to_csv("./analytics-28d.csv")
```

From version 2.1, you can do the same operation in an easier way.

```py
from analytix import YouTubeAnalytics

client = YouTubeAnalytics.from_file("./secrets.json")
report = client.daily_analytics().to_csv("./analytics-28d.csv")
```

To read up further, [have a look at the documentation](https://analytix.readthedocs.io/en/latest/).

## Contributing

analytix is open to contributions. To find out where to get started, have a look at the [contributing guide](https://github.com/parafoxia/analytix/blob/main/CONTRIBUTING.md).

## License

The analytix module for Python is licensed under the [BSD 3-Clause License](https://github.com/parafoxia/analytix/blob/main/LICENSE).
