# SPDX-FileCopyrightText: 2026 Ethan Henderson
# SPDX-License-Identifier: 0BSD
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "analytix @ file:///${PROJECT_ROOT}",
#     "pandas",
# ]
# ///

import logging

import analytix


def main() -> None:
    with analytix.Client("secrets.json") as client:
        report = client.fetch_report(dimensions=("day",))
        df = report.to_pandas()
        print(df.head())  # noqa: T201


if __name__ == "__main__":
    analytix.enable_logging(logging.DEBUG)
    main()
