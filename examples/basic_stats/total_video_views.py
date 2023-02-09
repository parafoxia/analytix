"""Total view counts, estimated watch time, and more for a channel

This example retrieves the total number of views, comments, likes,
dislikes, estimated minutes watched, and average view duration of videos
over the default time period, which is the last 28 days.

It then displays it in a human-readable format.
"""

from analytix import Client

METRICS = (
    "views",
    "comments",
    "likes",
    "dislikes",
    "estimatedMinutesWatched",
    "averageViewDuration",
)

if __name__ == "__main__":
    with Client("secrets.json") as client:
        report = client.retrieve_report(metrics=METRICS)

        for i, metric in enumerate(METRICS):
            print(f"{metric:>23}: {report.resource.rows[0][i]}")
