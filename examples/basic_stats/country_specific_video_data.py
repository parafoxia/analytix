"""Country-specific view counts (and more) for a channel

This report retrieves the total number of views, comments, likes,
dislikes, and estimated minutes watched your videos received in the US
over the last 28 days. It then prints a pandas DataFrame to the console.
"""

from analytix import Client

if __name__ == "__main__":
    with Client("secrets.json") as client:
        report = client.retrieve_report(
            metrics=(
                "views",
                "comments",
                "likes",
                "dislikes",
                "estimatedMinutesWatched",
            ),
            filters={"country": "US"},
        )
        print(report.to_pandas())
