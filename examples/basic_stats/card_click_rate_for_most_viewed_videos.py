"""Top 10 - Card click rates for a channel's most viewed videos

This is a modified version of the annotation click-through rate to use
cards instead. As well as the views and likes, it gets the number of
times a card (and it's teaser) were seen vs. how many times it was
clicked. It then provides a percentage click-through rate (CTR) for
that each video.
"""

from analytix import Client

if __name__ == "__main__":
    with Client("secrets.json") as client:
        report = client.retrieve_report(
            dimensions=("video",),
            metrics=(
                "views",
                "likes",
                "cardTeaserImpressions",
                "cardTeaserClicks",
                "cardTeaserClickRate",
                "cardImpressions",
                "cardClicks",
                "cardClickRate",
            ),
            max_results=10,
            sort_options=("-views",),
        )
        print(report.to_pandas())
