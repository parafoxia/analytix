"""Top 10 - Most watched playlists for a channel

This example gets information about the 10 most watched playlists on
your channel over the last 28 days, which is then saved to a CSV file.

Note: The averageTimeInPlaylist metrics is displayed in minutes.
"""

import analytix
from analytix import Client

# Let's enable the logger so we can see what's going on.
analytix.enable_logging()

if __name__ == "__main__":
    with Client("secrets.json") as client:
        report = client.retrieve_report(
            dimensions=("playlist",),
            metrics=(
                "estimatedMinutesWatched",
                "views",
                "playlistStarts",
                "averageTimeInPlaylist",
            ),
            filters={"isCurated": "1"},
            max_results=10,
            sort_options=("-estimatedMinutesWatched",),
        )
        report.to_csv("top_10_watched_playlists.csv")
