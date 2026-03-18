# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

"""Report resources.

These mirror YouTube Analytics API resources, but lack quality-of-life
features that the analytix interfaces provide.
"""

__all__ = ("ColumnHeader", "ColumnType", "DataType", "ResultTable")

from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import Literal


class DataType(Enum):
    """An enum of data types. Can be `STRING`, `INTEGER`, or `FLOAT`."""

    STRING = "STRING"
    """A string type."""

    INTEGER = "INTEGER"
    """An integer type."""

    FLOAT = "FLOAT"
    """A float type."""


class ColumnType(Enum):
    """An enum of column types. Can be `DIMENSION` or `METRIC`."""

    DIMENSION = "DIMENSION"
    """Of type dimension."""

    METRIC = "METRIC"
    """Of type metric."""


@dataclass(frozen=True)
class ColumnHeader:
    """A column header.

    Column headers contain various information about the columns in the
    report. You will never need to create one of these yourself.

    Parameters
    ----------
    name
        The column name.
    data_type
        The data type of the column.
    column_type
        The column type.
    """

    __slots__ = ("column_type", "data_type", "name")

    name: str
    data_type: "DataType"
    column_type: "ColumnType"

    @property
    def data(self) -> dict[str, Any]:
        """The raw data for this column header in JSON format.

        Returns
        -------
        Dict[str, Any]
            The response data.
        """
        return {
            "name": self.name,
            "dataType": self.data_type.value,
            "columnType": self.column_type.value,
        }


@dataclass(frozen=True)
class ResultTable:
    """A result table.

    This is the resource type that gets sent from the YouTube Analytics
    API.

    Parameters
    ----------
    kind
        The kind of resource this is. This will always be
        "youtubeAnalytics#resultTable".
    column_headers
        Information about the columns in the report, such as the name
        and the column type.
    rows
        The rows in the report. This will be a list of lists.

    See Also
    --------
    Instances of this class are presented as part of `Report` instances.
    """

    kind: Literal["youtubeAnalytics#resultTable"]
    column_headers: list["ColumnHeader"]
    rows: list[list[str | int | float]]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "ResultTable":
        """Create a new `ResultTable` instance from JSON data.

        Parameters
        ----------
        data
            The raw JSON data from the API.

        Returns
        -------
        ResultTable
            The newly created instance.
        """
        return cls(
            data["kind"],
            [
                ColumnHeader(
                    header["name"],
                    DataType(header["dataType"]),
                    ColumnType(header["columnType"]),
                )
                for header in data["columnHeaders"]
            ],
            data["rows"],
        )

    @property
    def data(self) -> dict[str, Any]:
        """The raw data for this result table in JSON format.

        Returns
        -------
        Dict[str, Any]
            The response data.
        """
        return {
            "kind": self.kind,
            "columnHeaders": [header.data for header in self.column_headers],
            "rows": self.rows,
        }
