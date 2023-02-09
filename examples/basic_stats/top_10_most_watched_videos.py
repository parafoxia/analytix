"""Top 10 - Most watched videos for a channel

This example gets information about the 10 most watched videos on your
channel over the last 28 days, which is then saved to a CSV file.
"""

import analytix
from analytix import Client

# Let's enable the logger so we can see what's going on.
analytix.enable_logging()

if __name__ == "__main__":
    with Client("secrets.json") as client:
        report = client.retrieve_report(
            dimensions=("video",),
            metrics=("estimatedMinutesWatched", "views", "likes", "subscribersGained"),
            max_results=10,
            sort_options=("-estimatedMinutesWatched",),
        )
        report.to_csv("top_10_watched_videos.csv")
