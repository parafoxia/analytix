import datetime as dt

import matplotlib.pyplot as plt
import seaborn as sns

import analytix
from analytix import Analytics


if __name__ == "__main__":
    analytix.setup_logging()

    client = Analytics.with_secrets("secrets.json")
    report = client.retrieve(
        dimensions=("day",),
        metrics=("views",),
        start_date=dt.date(2021, 1, 1),
        end_date=dt.date(2021, 12, 31),
    )
    df = report.to_dataframe()

    sns.lineplot(data=df, x="day", y="views")
    plt.savefig("daily-views-2021.png")
