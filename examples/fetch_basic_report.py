# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "analytix @ file:///${PROJECT_ROOT}",
#     "pandas",
# ]
# ///

import datetime as dt
import json
import logging
from pathlib import Path

import analytix
from analytix import Scopes


def main() -> None:
    with analytix.Client("secrets.json", scopes=Scopes.ALL) as client:
        report = client.fetch_report(
            dimensions=("day",),
            start_date=dt.date(2024, 1, 1),
            end_date=dt.date(2024, 12, 31),
        )
        with Path("report.json").open("w") as f:
            json.dump(report.resource.data, f, indent=4)


if __name__ == "__main__":
    analytix.enable_logging(logging.DEBUG)
    main()
