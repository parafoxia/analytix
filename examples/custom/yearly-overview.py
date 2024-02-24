"""Yearly overview

This creates a table with overviews of each year's core metrics (i.e.
those that appear on the Studio Analytics front screen). You could
easily save this to a CSV or something if you wanted.
"""

import datetime as dt

from tabulate import tabulate  # pip install tabulate

from analytix import Client, Scopes, enable_logging

START_DATE = dt.date(2019, 7, 13)

if __name__ == "__main__":
    enable_logging()

    with Client("secrets.json", scopes=Scopes.ALL) as client:
        df = client.fetch_report(
            dimensions=("month",),
            metrics=(
                "views",
                "estimatedMinutesWatched",
                "subscribersGained",
                "subscribersLost",
                "estimatedRevenue",
            ),
            start_date=START_DATE,
            currency="GBP",
        ).to_pandas()

        df = df.set_index("month")
        df = df.groupby(df.index.year).sum()
        df["estimatedHoursWatched"] = df["estimatedMinutesWatched"] / 60
        df["subscriberTotal"] = df["subscribersGained"] - df["subscribersLost"]

        print(
            tabulate(
                df[
                    [
                        "views",
                        "estimatedHoursWatched",
                        "subscriberTotal",
                        "estimatedRevenue",
                    ]
                ],
                headers=[
                    "Year",
                    "Views",
                    "Watch Time (h)",
                    "Subscribers",
                    "Revenue (£)",
                ],
                floatfmt=",.0f",
            )
        )
