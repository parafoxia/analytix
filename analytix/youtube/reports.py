import csv
import json
import logging
import sqlite3

from analytix.errors import MissingOptionalComponents

try:
    import pandas as pd

    _PA = True
except ImportError:
    _PA = False


class AnalyticsReport:
    __slots__ = ("data", "ncolumns", "nrows", "type")

    def __init__(self, data, type):
        self.data = data
        self.ncolumns = len(data["columnHeaders"])
        self.nrows = len(data["rows"])
        self.type = type
        logging.info(f"Report created! Shape: ({self.nrows}, {self.ncolumns})")

    def __str__(self):
        return self.type

    @property
    def shape(self):
        return (self.nrows, self.ncolumns)

    def to_dataframe(self):
        if not _PA:
            raise MissingOptionalComponents(
                "the pandas library needs to be installed to create data frames"
            )

        df = pd.DataFrame()
        df = df.append(self.data["rows"])
        df.columns = [c["name"] for c in self.data["columnHeaders"]]
        return df

    def to_json(self, file, *, indent=4):
        if not file.endswith(".json"):
            file += ".json"

        with open(file, mode="w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=indent, ensure_ascii=False)

    def to_csv(self, file, *, delimiter=","):
        if not file.endswith(".csv"):
            file += ".csv"

        with open(file, mode="w", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow([c["name"] for c in self.data["columnHeaders"]])

            for r in self.data["rows"]:
                writer.writerow(r)
