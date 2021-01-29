# analytix

[![PyPi version](https://img.shields.io/pypi/v/analytix.svg)](https://pypi.python.org/pypi/analytix/) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/analytix.svg)](https://pypi.python.org/pypi/analytix/) [![License](https://img.shields.io/github/license/parafoxia/analytix.svg)](https://github.com/parafoxia/analytix/blob/main/LICENSE)

analytix is a simple yet powerful API wrapper to make getting analytical information from your favourite services easier than ever. Note: Only the YouTube Anaytics API is supported as this time, though more will be added over time!

## Installation

**Python 3.6 or greater is required.**

You can install the latest version of analytix using the following command:

```bash
# Linux/macOS
python3 -m pip install -U analytix

# Windows
py -3 -m pip install -U analytix

# In a virtual environment
pip install analytix
```

You can also install the development version by running the following (this example assumes you're on Linux/macOS):

```bash
$ git clone https://github.com/parafoxia/analytix
$ cd analytix
$ git checkout develop
$ python3 -m pip install -U .
```

## Getting started

To get started with analytix, have a look at the documentation.

### Quick example

The following example shows you how to save a CSV of day-by-day analytics for 2020 from the YouTube Analytics API:

```py
import datetime as dt

from analytics.youtube import TimeBasedYouTubeAnalytics, YouTubeService

service = YouTubeService("./secrets.json")  # Load from secrets file
service.authorise("yt-analytics.readonly", "yt-analytics-monetary.readonly")
analytics = TimeBasedYouTubeAnalytics(service)
report = analytics.retrieve(
    ("views", "likes", "comments"),
    start_date=dt.date(2020, 1, 1),
    end_date=dt.date(2020, 12, 31),
    dimensions=("day",)
)
report.to_csv("./analytics.csv")
```

You can also import the following to get all available metrics (note that some report types support different metrics):

```py
from analytix.youtube.features import YOUTUBE_ANALYTICS_DEFAULT_METRICS
```

## Contributing

If you're interested in contributing to analytix, check out the [contributing guide](https://github.com/parafoxia/analytix/blob/main/CONTRIBUTING.md).

## License

The analytix module for Python is licensed under the [BSD-3-Clause License](https://github.com/parafoxia/analytix/blob/main/LICENSE).
