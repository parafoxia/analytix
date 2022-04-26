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
        metrics=("estimatedRevenue", "estimatedAdRevenue", "grossRevenue"),
        start_date=dt.date(2022, 1, 1),
        end_date=dt.date(2022, 3, 31),
    )
    df = report.to_dataframe()

    sns.ecdfplot(data=df)
    plt.savefig("revenue-q1-2022.png")
