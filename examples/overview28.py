import datetime as dt
import logging

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

import analytix
from analytix import Client

# Set up Matplotlib and Seaborn.
mpl.rcParams["figure.figsize"] = (20, 12)
sns.set_style("darkgrid")

if __name__ == "__main__":
    # Enable logging. Note that Matplotlib DEBUG logging is
    # *astonishingly* verbose -- might be best to avoid it if you can.
    analytix.enable_logging()

    # Let's use the client as a context manager so we don't have to
    # manually tear it down once we're done.
    with Client("./secrets.json") as client:
        # Retrieve the data!
        report = client.retrieve_report(
            dimensions=("day",),
            metrics=(
                "views",
                "estimatedMinutesWatched",
                "subscribersGained",
                "subscribersLost",
                "estimatedRevenue",
            ),
            # The YouTube API doesn't necessarily return all data within
            # a given time range -- if you want to guarantee 28 rows,
            # it's best to extend the range, then crop the data at the
            # other end.
            start_date=dt.date.today() - dt.timedelta(days=30),
        )

        # Convert to a pandas DataFrame, including optionally cropping
        # the data to 28 days.
        df = report.to_pandas()[:28]

        # Draw the data to various subplots.
        fig, axs = plt.subplots(2, 2, sharex=True)
        sns.lineplot(ax=axs[0][0], data=df, x="day", y="views")
        sns.lineplot(
            ax=axs[0][1], data=df, x="day", y=df["estimatedMinutesWatched"] / 60
        )
        sns.lineplot(
            ax=axs[1][0],
            data=df,
            x="day",
            y=df["subscribersGained"] - df["subscribersLost"],
        )
        sns.lineplot(ax=axs[1][1], data=df, x="day", y="estimatedRevenue")

        # Do some fancy stuff to make it look nicer.
        fig.suptitle(
            f"28-day Overview ({df['day'][0].strftime('%d/%m/%Y')} - "
            f"{df['day'][27].strftime('%d/%m/%Y')})"
        )
        axs[0][0].set_ylabel("Views")
        axs[0][1].set_ylabel("Watch time (hours)")
        axs[1][0].set_xlabel("Day")
        axs[1][0].set_ylabel("Net subscribers")
        axs[1][1].set_xlabel("Day")
        axs[1][1].set_ylabel("Est. revenue (USD)")
        fig.autofmt_xdate(rotation=45)
        plt.subplots_adjust(bottom=0.1, left=0.05, right=0.95)

        # Save the figure to disk!
        plt.savefig("output.png")
