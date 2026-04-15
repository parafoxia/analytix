# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "analytix @ file:///${PROJECT_ROOT}",
#     "pandas",
# ]
# ///

import datetime as dt
import json
from pathlib import Path

import analytix


def main() -> None:
    with analytix.Client("secrets.json") as client:
        report = client.fetch_report(
            dimensions=("video",),
            start_date=dt.date.today() - dt.timedelta(days=90),
            end_date=dt.date.today(),  #
            sort_options=("-views",),
            max_results=10,
        )
        with Path("top_videos.json").open("w") as f:
            json.dump(report.data, f, indent=4)


if __name__ == "__main__":
    main()
