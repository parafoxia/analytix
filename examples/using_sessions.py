# SPDX-FileCopyrightText: 2026 Ethan Henderson
# SPDX-License-Identifier: 0BSD
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "analytix @ file:///${PROJECT_ROOT}",
#     "openpyxl",
# ]
# ///

import datetime as dt
import logging
from pathlib import Path

import analytix


def main() -> None:
    # Delete previous version.
    Path("yearly_summaries.xlsx").unlink(missing_ok=True)

    # Using a session reuses the access token for all requests within
    # it, meaning we don't need to reauthorise every time.
    with analytix.Client("secrets.json") as client, client.session():
        for year in range(2019, dt.date.today().year + 1):
            report = client.fetch_report(
                dimensions=("day",),
                start_date=dt.date(year, 1, 1),
                end_date=dt.date(year, 12, 31),
            )
            report.to_excel("yearly_summaries.xlsx", sheet_name=str(year))


if __name__ == "__main__":
    analytix.enable_logging(logging.DEBUG)
    main()
