import httpx

from analytix import Analytics

# Retrieve the IDs of the top videos using the Analytics API.
client = Analytics.with_secrets("secrets.json")
report = client.retrieve(
    dimensions=("video",),
    metrics=("views",),
    sort_options=("-views",),
    max_results=10,
)
df = report.to_dataframe()

# Retrieve the titles of the videos using the Data API.
client = httpx.Client()

with open("api_key") as f:
    key = f.read()

for i, row in df.iterrows():
    data = {}

    while "items" not in data.keys():
        # This is done because the Data API isn't amazingly reliable for
        # this sort of thing.
        data = client.get(
            "https://www.googleapis.com/youtube/v3/videos"
            f"?id={row.video}&part=snippet&key={key}"
        ).json()

    title = data["items"][0]["snippet"]["title"]
    print(f"\33[1m{i + 1:>2}.\33[0m {title} (\33[1m{row.views:,}\33[0m views)")
