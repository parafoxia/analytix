"""Total playlist views for a channel

This example does much the same as it's video-based equivalent, but
retrieves data more relevant to playlists.

Note: Only views made within the context of a playlist are counted in
this report.
"""

from analytix import Client

METRICS = (
    "views",
    "playlistStarts",
    "estimatedMinutesWatched",
    "viewsPerPlaylistStart",
)

if __name__ == "__main__":
    with Client("secrets.json") as client:
        report = client.retrieve_report(metrics=METRICS, filters={"isCurated": "1"})

        for i, metric in enumerate(METRICS):
            print(f"{metric:>23}: {report.resource.rows[0][i]}")
