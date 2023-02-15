# Copyright (c) 2021-present, Ethan Henderson
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import annotations

__all__ = ("ResultTable", "AnalyticsReport")

import json
import logging
import typing as t
from dataclasses import dataclass
from enum import Enum

from analytix import errors
from analytix.utils import process_path, requires

if t.TYPE_CHECKING:
    import pandas as pd
    import polars as pl
    import pyarrow as pa

    from analytix.abc import ReportType
    from analytix.types import PathLikeT, ResponseT

_log = logging.getLogger(__name__)


class DataType(Enum):
    """An enum representing data types. Can be `STRING`, `INTEGER`,
    or `FLOAT`.
    """

    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"


class ColumnType(Enum):
    """An enum representing column types. Can be `DIMENSION` or
    `METRIC`.
    """

    DIMENSION = "DIMENSION"
    METRIC = "METRIC"


@dataclass(frozen=True)
class ColumnHeader:
    """A representation of a column header.

    Column headers contain various information about the columns in the
    report. You will never need to create one of these yourself.

    Parameters
    ----------
    name : str
        The column name.
    data_type : DataType
        The data type of the column.
    column_type : ColumnType
        The column type.

    Attributes
    ----------
    name : str
        The column name.
    data_type : DataType
        The data type of the column.
    column_type : ColumnType
        The column type.
    """

    __slots__ = ("name", "data_type", "column_type")

    name: str
    data_type: DataType
    column_type: ColumnType

    @property
    def data(self) -> ResponseT:
        """The raw data for this column header in JSON format.

        Returns
        -------
        dict of str-Any
            The response data.
        """

        return {
            "name": self.name,
            "dataType": self.data_type.value,
            "columnType": self.column_type.value,
        }


@dataclass(frozen=True)
class ResultTable:
    """A representation of a resultTable resource.

    This is the resource type that gets sent from the YouTube Analytics
    API.

    Parameters
    ----------
    kind : str
        The kind of resource this is. This will always be
        "youtubeAnalytics#resultTable".
    column_headers : list of ColumnHeader
        Information about the columns in the report, such as the name
        and the column type.
    rows : list of list of str int and float
        The rows in the report. This will be a list of lists.

    Attributes
    ----------
    kind : str
        The kind of resource this is. This will always be
        "youtubeAnalytics#resultTable".
    column_headers : list of ColumnHeader
        Information about the columns in the report, such as the name
        and the column type.
    rows : list of list of str int and float
        The rows in the report. This will be a list of lists.

    !!! info "See also"
        Instances of this class are presented as part of
        `AnalyticsReport` instances.
    """

    kind: str
    column_headers: list[ColumnHeader]
    rows: list[list[str | int | float]]

    @classmethod
    def from_json(cls, data: ResponseT) -> ResultTable:
        """Create a new `ResultTable` instance from JSON data.

        Parameters
        ----------
        data : JSON object
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
    def data(self) -> ResponseT:
        """The raw data for this result table in JSON format.

        Returns
        -------
        dict of str-Any
            The response data.
        """

        return {
            "kind": self.kind,
            "columnHeaders": [header.data for header in self.column_headers],
            "rows": self.rows,
        }


class AnalyticsReport:
    """A representation of an analytics report.

    This does not represent a direct resultTable resource, but instead
    provides additional methods on top of one, largely designed to save
    the report data into different formats.

    Parameters
    ----------
    data : JSON object
        The raw JSON data from the API.
    type : ReportType
        The report type.

    Attributes
    ----------
    resource : ResultTable
        An instance representing a resultTable resource.
    type : ReportType
        The report type.
    """

    def __init__(self, data: ResponseT, type: ReportType) -> None:
        self.resource = ResultTable.from_json(data)
        self.type = type
        self._shape = (len(data["rows"]), len(self.resource.column_headers))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.resource == other.resource and self.type == other.type

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.resource != other.resource or self.type != other.type

    @property
    def shape(self) -> tuple[int, int]:
        """The shape of the report.

        This is presented in (rows, columns) format.

        Returns
        -------
        tuple of two ints
            The shape of the report.

        ??? example "Basic example"
            ```py
            >>> report.shape
            (120, 42)
            ```

        ??? example "Getting the number of rows only"
            ```py
            >>> report.shape[0]
            120
            ```
        """

        return self._shape

    @property
    def columns(self) -> list[str]:
        """A list of all columns names in the report.

        Returns
        -------
        list of str
            The column list.

        !!! info "See also"
            This does not return a list of column headers. If you want
            that, use `report.resource.column_headers` instead.
        """

        return [c.name for c in self.resource.column_headers]

    @property
    def dimensions(self) -> list[str]:
        """A list of all dimensions in the report.

        Returns
        -------
        list of str
            The dimension list.
        """

        return [
            c.name
            for c in self.resource.column_headers
            if c.column_type == ColumnType.DIMENSION
        ]

    @property
    def metrics(self) -> list[str]:
        """A list of all metrics in the report.

        Returns
        -------
        list of str
            The metric list.
        """

        return [
            c.name
            for c in self.resource.column_headers
            if c.column_type == ColumnType.METRIC
        ]

    @property
    def numeric(self) -> list[str]:
        """A list of all numerical columns in the report.

        Returns
        -------
        list of str
            The list of numerical columns.
        """

        return [
            c.name
            for c in self.resource.column_headers
            if c.data_type != DataType.STRING
        ]

    @property
    def non_numeric(self) -> list[str]:
        """A list of all non-numerical columns in the report.

        Returns
        -------
        list of str
            The list of non-numerical columns.
        """

        return [
            c.name
            for c in self.resource.column_headers
            if c.data_type == DataType.STRING
        ]

    def to_json(
        self, path: PathLikeT, *, indent: int | None = 4, overwrite: bool = True
    ) -> ResponseT:
        """Save this report in JSON format.

        This saves the data as it arrived from the YouTube Analytics
        API.

        Parameters
        ----------
        path : Path object or str
            The path to save the file to.
        indent : int, optional
            The number of spaces to indent each line of the data. To
            create a one-line file, pass `None`.
        overwrite : bool, optional
            Whether to overwrite an existing file.

        Returns
        -------
        dict of str-Any
            The raw JSON data.

        ??? example "Basic example"
            ```py
            >>> report.to_json("output.json")
            ```

        ??? example "Saving in a minimal format"
            ```py
            # Note that passing `indent=0` will not have the same
            # effect.
            >>> report.to_json("output.json", indent=None)
            ```
        """

        path = process_path(path, ".json", overwrite)
        data = self.resource.data

        with open(path, "w") as f:
            json.dump(data, f, indent=indent)

        _log.info(f"Saved report as JSON to {path.resolve()}")
        return data

    def to_csv(
        self, path: PathLikeT, *, delimiter: str = ",", overwrite: bool = True
    ) -> None:
        """Save this report as a CSV or TSV file.

        The filetype is dependent on the delimiter you provide — if you
        pass a tab character as a delimiter, the file will be saved as
        a TSV. It will be saved as a CSV in all other cases.

        Parameters
        ----------
        path : Path object or str
            The path to save the file to.
        delimiter : int, optional
            The character to use as a delimiter.
        overwrite : bool, optional
            Whether to overwrite an existing file.

        Returns
        -------
        None

        ??? example "Basic example"
            ```py
            >>> report.to_csv("output.csv")
            ```

        ??? example "Saving as a TSV"
            ```py
            >>> report.to_csv("output.tsv", delimiter="\\t")
            ```
        """

        extension = ".tsv" if delimiter == "\t" else ".csv"
        path = process_path(path, extension, overwrite)

        with open(path, "w") as f:
            f.write(f"{delimiter.join(self.columns)}\n")
            for row in self.resource.rows:
                line = delimiter.join(f"{v}" for v in row)
                f.write(f"{line}\n")

        _log.info(f"Saved report as {extension[1:].upper()} to {path.resolve()}")

    @requires("openpyxl")
    def to_excel(
        self, path: PathLikeT, *, sheet_name: str = "Analytics", overwrite: bool = True
    ) -> None:
        """Save this report as an Excel spreadsheet.

        Parameters
        ----------
        path : Path object or str
            The path to save the spreadsheet to.
        sheet_name : str, optional
            The name to give the sheet the data will be inserted into.
        overwrite : bool, optional
            Whether to overwrite an existing file.

        Returns
        -------
        None

        !!! warning
            The data cannot be saved to a sheet in an existing workbook.
            If you wish to do this, you will need to save the data to
            a new spreadsheet file, then copy the data over.

        !!! note
            This requires `openpyxl` to be installed to use, which is an
            optional dependency.

        ??? example "Basic example"
            ```py
            >>> report.to_excel("output.xlsx")
            ```

        ??? example "Saving with a custom sheet name"
            ```py
            >>> report.to_excel("output.xlsx", sheet_name="My Sheet")
            ```
        """

        from openpyxl import Workbook

        path = process_path(path, ".xlsx", overwrite)
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name

        ws.append(self.columns)
        for row in self.resource.rows:
            ws.append(row)

        wb.save(str(path))
        _log.info(f"Saved report as spreadsheet to {path.resolve()}")

    @requires("pandas")
    def to_pandas(self, *, skip_date_conversion: bool = False) -> pd.DataFrame:
        """Return this report as a pandas DataFrame.

        If Modin is installed, it will automatically be used instead of
        pandas. However, you will need to select and initialise your
        preferred engine before calling this method.

        Parameters
        ----------
        skip_date_conversion : bool, optional
            Whether or not to skip the conversion of "day" and "month"
            columns into the `datetime64[ns]` format. If you choose to
            skip this, these columns will be left as strings.

        Returns
        -------
        pandas DataFrame
            A pandas DataFrame.

        !!! note
            This requires `pandas` to be installed to use, which is an
            optional dependency.

        ??? example "Basic example"
            ```py
            >>> df = report.to_pandas()
            >>> df.head(5)
                     day  views  likes  comments  grossRevenue
            0 2022-06-20    778      8         0         2.249
            1 2022-06-21   1062     32         8         3.558
            2 2022-06-22    946     38         6         2.910
            3 2022-06-23   5107    199        15        24.428
            4 2022-06-24   2137     61         2         6.691
            ```
        """

        import pandas as pd

        if not self._shape[0]:
            raise errors.DataFrameConversionError(
                "cannot convert to DataFrame as the returned data has no rows"
            )

        df = pd.DataFrame(self.resource.rows, columns=self.columns)

        if not skip_date_conversion:
            s = {"day", "month"} & set(df.columns)
            if len(s):
                col = next(iter(s))
                df[col] = pd.to_datetime(df[col], format="%Y-%m-%d")
                _log.info(f"Converted {col!r} column to datetime64[ns] format")

        return df

    @requires("pyarrow")
    def to_arrow(self, *, skip_date_conversion: bool = False) -> pa.Table:
        """Return this report as a Apache Arrow table.

        Parameters
        ----------
        skip_date_conversion : bool, optional
            Whether or not to skip the conversion of "day" and "month"
            columns into the `timestamp[ns]` format. If you choose to
            skip this, these columns will be left as strings.

        Returns
        -------
        PyArrow Table
            An Apache Arrow table.

        !!! note
            This requires `pyarrow` to be installed to use, which is an
            optional dependency.

        ??? example "Basic example"
            ```py
            >>> table = report.to_arrow()
            >>> table.slice(length=3)
            pyarrow.Table
            day: timestamp[ns]
            views: int64
            likes: int64
            comments: int64
            grossRevenue: double
            ----
            day: [[2022-06-20 00:00:00.000000000,...]]
            views: [[778,1062,946,5107,2137]]
            likes: [[8,32,38,199,61]]
            comments: [[0,8,6,15,2]]
            grossRevenue: [[2.249,3.558,2.91,24.428,6.691]]
            ```
        """

        import pyarrow as pa
        import pyarrow.compute as pc

        table = pa.table(list(zip(*self.resource.rows)), names=self.columns)

        if not skip_date_conversion:
            s = {"day", "month"} & set(table.column_names)
            if len(s):
                col = next(iter(s))
                fmt = {"day": "%Y-%m-%d", "month": "%Y-%m"}[col]
                dt_series = pc.strptime(table.column(col), format=fmt, unit="ns")
                table = table.set_column(0, "day", dt_series)
                _log.info(f"Converted {col!r} column to timestamp[ns] format")

        return table

    @requires("polars")
    def to_polars(self, *, skip_date_conversion: bool = False) -> pl.DataFrame:
        """Return the data as a Polars DataFrame.

        Parameters
        ----------
        skip_date_conversion : bool, optional
            Whether or not to skip the conversion of "day" and "month"
            columns into the `date` format. If you choose to skip this,
            these columns will be left as strings.

        Returns
        -------
        Polars DataFrame
            A Polars DataFrame.

        !!! note
            This requires `polars` to be installed to use, which is an
            optional dependency.

        ??? example "Basic example"
            ```py
            >>> df = report.to_polars()
            >>> df.head(5)
            shape: (5, 5)
            ┌────────────┬───────┬───────┬──────────┬──────────────┐
            │ day        ┆ views ┆ likes ┆ comments ┆ grossRevenue │
            │ ---        ┆ ---   ┆ ---   ┆ ---      ┆ ---          │
            │ date       ┆ i64   ┆ i64   ┆ i64      ┆ f64          │
            ╞════════════╪═══════╪═══════╪══════════╪══════════════╡
            │ 2022-06-20 ┆ 778   ┆ 8     ┆ 0        ┆ 2.249        │
            ├╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌╌╌┤
            │ 2022-06-21 ┆ 1062  ┆ 32    ┆ 8        ┆ 3.558        │
            ├╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌╌╌┤
            │ 2022-06-22 ┆ 946   ┆ 38    ┆ 6        ┆ 2.91         │
            ├╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌╌╌┤
            │ 2022-06-23 ┆ 5107  ┆ 199   ┆ 15       ┆ 24.428       │
            ├╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌╌╌┤
            │ 2022-06-24 ┆ 2137  ┆ 61    ┆ 2        ┆ 6.691        │
            └────────────┴───────┴───────┴──────────┴──────────────┘
            ```
        """

        import polars as pl

        df = pl.DataFrame(self.resource.rows, schema=self.columns)

        if not skip_date_conversion:
            s = {"day", "month"} & set(df.columns)
            if len(s):
                col = next(iter(s))
                fmt = {"day": "%Y-%m-%d", "month": "%Y-%m"}[col]
                df = df.with_columns(pl.col(col).str.strptime(pl.Date, fmt=fmt))
                _log.info(f"Converted {col!r} column to date format")

        return df

    @requires("pyarrow")
    def to_feather(
        self,
        path: PathLikeT,
        *,
        skip_date_conversion: bool = False,
        overwrite: bool = True,
    ) -> pa.Table:
        """Save this report as an Apache Feather file.

        To do this, the data is first converted to an Apache Arrow
        table, which is returned from the method.

        Parameters
        ----------
        path : Path object or str
            The path to save the file to.
        skip_date_conversion : bool, optional
            Whether or not to skip the conversion of "day" and "month"
            columns into the `timestamp[ns]` format. If you choose to
            skip this, these columns will be left as strings.
        overwrite : bool, optional
            Whether to overwrite an existing file.

        Returns
        -------
        PyArrow Table
            The Apache Arrow table that was saved.

        !!! note
            This requires `pyarrow` to be installed to use, which is an
            optional dependency.

        ??? example "Basic example"
            ```py
            >>> table = report.to_feather("output.feather")
            >>> table.shape
            (7, 5)
            ```
        """

        import pyarrow.feather as pf

        path = process_path(path, ".feather", overwrite)
        table = self.to_arrow(skip_date_conversion=skip_date_conversion)
        pf.write_feather(table, path)
        _log.info(f"Saved report as Apache Feather file to {path.resolve()}")
        return table

    @requires("pyarrow")
    def to_parquet(
        self,
        path: PathLikeT,
        *,
        skip_date_conversion: bool = False,
        overwrite: bool = True,
    ) -> pa.Table:
        """Save this report as an Apache Parquet file.

        To do this, the data is first converted to an Apache Arrow
        table, which is returned from the method.

        Parameters
        ----------
        path : Path object or str
            The path to save the file to.
        skip_date_conversion : bool, optional
            Whether or not to skip the conversion of "day" and "month"
            columns into the `timestamp[ns]` format. If you choose to
            skip this, these columns will be left as strings.
        overwrite : bool, optional
            Whether to overwrite an existing file.

        Returns
        -------
        PyArrow Table
            The Apache Arrow table that was saved.

        !!! note
            This requires `pyarrow` to be installed to use, which is an
            optional dependency.

        ??? example "Basic example"
            ```py
            >>> table = report.to_parquet("output.parquet")
            >>> table.shape
            (7, 5)
            ```
        """

        import pyarrow.parquet as pq

        path = process_path(path, ".parquet", overwrite)
        table = self.to_arrow(skip_date_conversion=skip_date_conversion)
        pq.write_table(table, path)
        _log.info(f"Saved report as Apache Parquet file to {path.resolve()}")
        return table
