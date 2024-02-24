"""Subscriber journey

This creates a CSV with your channel's subscriber count at the end of
each day, as well as the net subscribers for each day. Perfect for
retroactively finding out when you hit channel milestones, or simply
reliving how your channel began!
"""

import datetime as dt

from analytix import Client, enable_logging

START_DATE = dt.date(2019, 7, 13)

if __name__ == "__main__":
    enable_logging()

    with Client("secrets.json") as client:
        df = client.fetch_report(
            dimensions=("day",),
            metrics=("subscribersGained", "subscribersLost"),
            start_date=START_DATE,
        ).to_pandas()

        df["subscribersNet"] = df["subscribersGained"] - df["subscribersLost"]
        df["subscriberTotal"] = df["subscribersNet"].cumsum()
        df[["day", "subscriberTotal", "subscribersNet"]].to_csv("subjourney.csv")
