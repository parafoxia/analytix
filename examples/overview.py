from analytix import Analytics

client = Analytics.with_secrets("secrets.json")
report = client.retrieve(
    dimensions=("day",),
    metrics=(
        "views",
        "estimatedMinutesWatched",
        "subscribersGained",
        "subscribersLost",
        "estimatedAdRevenue",
    ),
)

df = report.to_dataframe()
total_views = sum(df["views"])
watch_time = sum(df["estimatedMinutesWatched"]) / 60
subscribers = sum(df["subscribersGained"]) - sum(df["subscribersLost"])
est_revenue = sum(df["estimatedAdRevenue"])

print(
    f"Views:              \33[1m{total_views:,}\33[0m\n"
    f"Watch time (hours): \33[1m{watch_time:,.1f}\33[0m\n"
    f"Subscribers:        \33[1m{subscribers:,}\33[0m\n"
    f"Estimated revenue:  \33[1m${est_revenue:,.2f}\33[0m"
)
