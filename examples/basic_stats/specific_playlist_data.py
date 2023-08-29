"""Statistics for a specific playlist

This example is identical to the total playlist views one, except only
data for a specific playlist is retrieved.
"""

from analytix import Client

METRICS = (
    "views",
    "playlistStarts",
    "estimatedMinutesWatched",
    "viewsPerPlaylistStart",
)
# You'll need to replace this with one of your own playlists.
PLAYLIST_ID = "PLYeOw6sTSy6aJ8ZlA4vGvgGVo42IhF-Pc"

if __name__ == "__main__":
    with Client("secrets.json") as client:
        report = client.fetch_report(
            metrics=METRICS, filters={"isCurated": "1", "playlist": PLAYLIST_ID}
        )

        for i, metric in enumerate(METRICS):
            print(f"{metric:>23}: {report.resource.rows[0][i]}")
