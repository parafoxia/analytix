# analytix: examples

This folder contains various examples of how *analytix* can be used to retrieve data. This set does not aim to be exhaustive, but instead cover the most common use cases (predominantly things you can do on the "Channel analytics" page on the YouTube Studio).

Note that each example requires a secrets file, which is not provided.

## Directory

* [daily-views.py](https://github.com/parafoxia/analytix/blob/main/examples/daily-views.py) — Plots your channel's daily views for 2021 on a lineplot.
* [monthy-likes.py](https://github.com/parafoxia/analytix/blob/main/examples/monthy-likes.py) — Plots your channel's monthly likes for 2021 on a violinplot (a type of boxplot). Each month is split by days you received dislikes, and days you didn't.
* [revenue-ecdf.py](https://github.com/parafoxia/analytix/blob/main/examples/revenue-ecdf.py) — Plots your channel's revenue, ad revenue, and gross revenue for the first quarter of 2022 as a ECDF graph.

## License

These examples (and ONLY these examples) are put into the public domain via [The Unlicense](https://github.com/parafoxia/analytix/blob/main/examples/LICENSE).

The *analytix* module for Python is licensed under the [BSD 3-Clause License](https://github.com/parafoxia/analytix/blob/main/LICENSE).
