import datetime as dt

import seaborn as sns
import matplotlib.pyplot as plt

import analytix
from analytix import Analytics

if __name__ == "__main__":
    analytix.setup_logging()

    client = Analytics.with_secrets("secrets.json")
    report = client.retrieve(
        dimensions=("day", "subscribedStatus"),
        metrics=("likes", "dislikes"),
        start_date=dt.date(2021, 1, 1),
        end_date=dt.date(2021, 12, 31),
    )

    df = report.to_dataframe()
    df.insert(1, "month", [t.month for t in df["day"]])
    df["dislikes"] = df["dislikes"] > 0

    sns.violinplot(data=df, x="month", y="likes", hue="dislikes", split=True)
    plt.savefig("likes-2021.png")
