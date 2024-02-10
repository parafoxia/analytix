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

"""Report interfaces for analytix.

These are report interfaces equipped with various methods of saving and
exporting report data to different formats. They are not designed to be
like-for-like mappings of YouTube Analytics API resources.

Currently, there is only one of these interfaces.
"""

__all__ = ("Report",)

import json
import logging
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from analytix import utils
from analytix.errors import DataFrameConversionError
from analytix.errors import MissingOptionalComponents
from analytix.reports.resources import ColumnType
from analytix.reports.resources import ResultTable
from analytix.utils import process_path

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl
    import pyarrow as pa

    from analytix.abc import ReportType
    from analytix.types import PathLike

_log = logging.getLogger(__name__)


class Report:
    """An analytics report.

    This is an abstraction of the `resultTable` resource rather than a
    direct mapping. This class provides additional properties and
    methods designed to make it easier to perform certain operations.

    ???+ note "Changed in version 5.0"
        This used to be `AnalyticsReport`.

    Parameters
    ----------
    data
        The raw JSON data from the API.
    type
        The report type.

    Attributes
    ----------
    resource : ResultTable
        An instance representing a `resultTable` resource.
    type : ReportType
        The report type.
    """

    def __init__(self, data: Dict[str, Any], type: "ReportType") -> None:
        self.resource = ResultTable.from_json(data)
        self.type = type
        self._shape = (len(data["rows"]), len(self.resource.column_headers))

    @property
    def shape(self) -> Tuple[int, int]:
        """The shape of the report.

        This is presented in (rows, columns) format.

        Returns
        -------
        Tuple[int, int]
            The shape of the report.

        Examples
        --------
        >>> report.shape
        (120, 42)
        """
        return self._shape

    @property
    def columns(self) -> List[str]:
        """A list of all columns names in the report.

        Returns
        -------
        List[str]
            The column list.

        See Also
        --------
        This does not return a list of column headers. If you want that,
        use `report.resource.column_headers` instead.

        Examples
        --------
        >>> report.columns
        ["day", "subscribedStatus", "views", "likes", "comments"]
        """
        return [c.name for c in self.resource.column_headers]

    @property
    def dimensions(self) -> List[str]:
        """A list of all dimensions in the report.

        Returns
        -------
        List[str]
            The dimension list.

        Examples
        --------
        >>> report.dimensions
        ["day", "subscribedStatus"]
        """
        return [
            c.name
            for c in self.resource.column_headers
            if c.column_type == ColumnType.DIMENSION
        ]

    @property
    def metrics(self) -> List[str]:
        """A list of all metrics in the report.

        Returns
        -------
        List[str]
            The metric list.

        Examples
        --------
        >>> report.metrics
        ["views", "likes", "comments"]
        """
        return [
            c.name
            for c in self.resource.column_headers
            if c.column_type == ColumnType.METRIC
        ]

    def to_json(
        self,
        path: "PathLike",
        *,
        overwrite: bool = False,
        **kwargs: Any,
    ) -> None:
        """Save this report in JSON format.

        This saves the data as it arrived from the YouTube Analytics
        API.

        ???+ note "Changed in version 5.0"
            * `indent` is no longer an argument, but can still be
              provided as part of the `**kwargs`; as such, JSON exports
              are no longer indented by default
            * This will no longer overwrite existing files by default
            * You can now pass additional keyword arguments to be passed
              to the `json.dump` function

        Parameters
        ----------
        path
            The path to save the file to.
        overwrite
            Whether to overwrite an existing file.
        **kwargs
            Additional arguments to pass to `json.dump`. This includes
            `indent`.

        Returns
        -------
        None
            This method doesn't return anything.

        Examples
        --------
        >>> report.to_json("output.json")

        Saving in a pretty format.

        >>> report.to_json("output.json", indent=4)
        """
        path = process_path(path, ".json", overwrite=overwrite)
        data = self.resource.data

        with open(path, "w") as f:
            json.dump(data, f, **kwargs)

        _log.info(f"Saved report as JSON to {path.resolve()}")

    def to_csv(
        self,
        path: "PathLike",
        *,
        delimiter: str = ",",
        overwrite: bool = False,
    ) -> None:
        """Save this report as a CSV or TSV file.

        The filetype is dependent on the delimiter you provide — if you
        pass a tab character as a delimiter, the file will be saved as
        a TSV. It will be saved as a CSV in all other instances.

        ???+ note "Changed in version 5.0"
            This will no longer overwrite existing files by default.

        Parameters
        ----------
        path
            The path to save the file to.
        delimiter
            The character to use as a delimiter. If this is `\\t`, the
            report will be saved as a TSV.
        overwrite
            Whether to overwrite an existing file.

        Returns
        -------
        None
            This method doesn't return anything.

        Examples
        --------
        >>> report.to_csv("output.csv")

        Saving as a TSV.

        >>> report.to_csv("output.tsv", delimiter="\\t")
        """
        extension = ".tsv" if delimiter == "\t" else ".csv"
        path = process_path(path, extension, overwrite=overwrite)

        with open(path, "w") as f:
            f.write(f"{delimiter.join(self.columns)}\n")
            for row in self.resource.rows:
                line = delimiter.join(f"{v}" for v in row)
                f.write(f"{line}\n")

        _log.info(f"Saved report as {extension[1:].upper()} to {path.resolve()}")

    def to_excel(
        self,
        path: "PathLike",
        *,
        sheet_name: str = "Analytics",
        overwrite: bool = False,
    ) -> None:
        """Save this report as an Excel spreadsheet.

        The data cannot be saved to a new sheet in an existing workbook.
        If you wish to do this, you will need to save the data to a new
        spreadsheet file, then copy the data over.

        ???+ note "Changed in version 5.0"
            This will no longer overwrite existing files by default.

        Parameters
        ----------
        path
            The path to save the spreadsheet to.
        sheet_name
            The name to give the sheet the data will be inserted into.
        overwrite
            Whether to overwrite an existing file.

        Returns
        -------
        None
            This method doesn't return anything.

        Notes
        -----
        This requires `openpyxl` to be installed to use, which is an
        optional dependency.

        Examples
        --------
        >>> report.to_excel("output.xlsx")
        """
        if not utils.can_use("openpyxl"):
            raise MissingOptionalComponents("openpyxl")

        from openpyxl import Workbook

        path = process_path(path, ".xlsx", overwrite=overwrite)
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name

        ws.append(self.columns)
        for row in self.resource.rows:
            ws.append(row)

        wb.save(str(path))
        _log.info(f"Saved report as spreadsheet to {path.resolve()}")

    def to_pandas(self, *, skip_date_conversion: bool = False) -> "pd.DataFrame":
        """Return this report as a pandas DataFrame.

        Parameters
        ----------
        skip_date_conversion
            Whether or not to skip the conversion of "day" and "month"
            columns into a datetime format. If you choose to skip this,
            these columns will be left as strings.

        Returns
        -------
        pandas DataFrame
            A pandas DataFrame.

        Raises
        ------
        MissingOptionalComponents
            pandas is not installed.
        DataFrameConversionError
            There is no data from which to create a DataFrame.

        Notes
        -----
        This requires `pandas` to be installed to use, which is an
        optional dependency.

        Examples
        --------
        >>> df = report.to_pandas()
        >>> df.head(5)
                 day  views  likes  comments  grossRevenue
        0 2022-06-20    778      8         0         2.249
        1 2022-06-21   1062     32         8         3.558
        2 2022-06-22    946     38         6         2.910
        3 2022-06-23   5107    199        15        24.428
        4 2022-06-24   2137     61         2         6.691
        """
        # sourcery skip: class-extract-method
        if not utils.can_use("pandas"):
            raise MissingOptionalComponents("pandas")

        if not self._shape[0]:
            raise DataFrameConversionError(
                "cannot convert to DataFrame as the returned data has no rows",
            )

        import pandas as pd

        df = pd.DataFrame(self.resource.rows, columns=self.columns)

        if not skip_date_conversion and len(s := {"day", "month"} & set(df.columns)):
            col = next(iter(s))
            fmt = {"day": "%Y-%m-%d", "month": "%Y-%m"}[col]
            df[col] = pd.to_datetime(df[col], format=fmt)
            _log.debug(f"Converted {col!r} column to datetime format")

        return df

    def to_arrow(self, *, skip_date_conversion: bool = False) -> "pa.Table":
        """Export this report as an Apache Arrow table.

        Parameters
        ----------
        skip_date_conversion
            Whether or not to skip the conversion of "day" and "month"
            columns into a datetime format. If you choose to skip this,
            these columns will be left as strings.

        Returns
        -------
        PyArrow Table
            An Apache Arrow table.

        Raises
        ------
        MissingOptionalComponents
            PyArrow is not installed.
        DataFrameConversionError
            There is no data from which to create an Arrow table.

        Notes
        -----
        This requires `pyarrow` to be installed to use, which is an
        optional dependency.

        Examples
        --------
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
        """
        if not utils.can_use("pyarrow"):
            raise MissingOptionalComponents("pyarrow")

        if not self._shape[0]:
            raise DataFrameConversionError(
                "cannot convert to Arrow table as the returned data has no rows",
            )

        import pyarrow as pa
        import pyarrow.compute as pc

        table = pa.table(list(zip(*self.resource.rows)), names=self.columns)

        if not skip_date_conversion and len(
            s := {"day", "month"} & set(table.column_names),
        ):
            col = next(iter(s))
            fmt = {"day": "%Y-%m-%d", "month": "%Y-%m"}[col]
            dt_series = pc.strptime(table.column(col), format=fmt, unit="ns")
            table = table.set_column(0, "day", dt_series)
            _log.debug(f"Converted {col!r} column to datetime format")

        return table

    def to_polars(self, *, skip_date_conversion: bool = False) -> "pl.DataFrame":
        """Return the data as a Polars DataFrame.

        Parameters
        ----------
        skip_date_conversion
            Whether or not to skip the conversion of "day" and "month"
            columns into a date format. If you choose to skip this,
            these columns will be left as strings.

        Returns
        -------
        Polars DataFrame
            A Polars DataFrame.

        Raises
        ------
        MissingOptionalComponents
            Polars is not installed.
        DataFrameConversionError
            There is no data from which to create a DataFrame.

        Notes
        -----
        This requires `polars` to be installed to use, which is an
        optional dependency.

        Examples
        --------
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
        """
        if not utils.can_use("polars"):
            raise MissingOptionalComponents("polars")

        if not self._shape[0]:
            raise DataFrameConversionError(
                "cannot convert to DataFrame as the returned data has no rows",
            )

        import polars as pl

        df = pl.DataFrame(self.resource.rows, schema=self.columns)

        if not skip_date_conversion and len(s := {"day", "month"} & set(df.columns)):
            col = next(iter(s))
            fmt = {"day": "%Y-%m-%d", "month": "%Y-%m"}[col]
            df = df.with_columns(pl.col(col).str.strptime(pl.Date, fmt))
            _log.debug(f"Converted {col!r} column to date format")

        return df

    def to_feather(
        self,
        path: "PathLike",
        *,
        skip_date_conversion: bool = False,
        overwrite: bool = False,
        **kwargs: Any,
    ) -> None:
        """Save this report as an Apache Feather file.

        ???+ note "Changed in version 5.0"
            * This will no longer overwrite existing files by default
            * You can now pass additional keyword arguments to be passed
              to the `pf.write_feather` function
            * This no longer returns a PyArrow table

        Parameters
        ----------
        path
            The path to save the file to.
        skip_date_conversion
            Whether or not to skip the conversion of "day" and "month"
            columns into a datetime format. If you choose to skip this,
            these columns will be left as strings.
        overwrite
            Whether to overwrite an existing file.

        Returns
        -------
        None
            This method doesn't return anything.

        Other Parameters
        ----------------
        **kwargs
            Additional arguments to pass to `pf.write_feather`.

        Notes
        -----
        This requires `pyarrow` to be installed to use, which is an
        optional dependency.

        Examples
        --------
        >>> report.to_feather("output.feather")
        """
        if not utils.can_use("pyarrow"):
            raise MissingOptionalComponents("pyarrow")

        import pyarrow.feather as pf

        path = process_path(path, ".feather", overwrite=overwrite)
        pf.write_feather(
            self.to_arrow(skip_date_conversion=skip_date_conversion),
            path,
            **kwargs,
        )

        _log.info(f"Saved report as Apache Feather file to {path.resolve()}")

    def to_parquet(
        self,
        path: "PathLike",
        *,
        skip_date_conversion: bool = False,
        overwrite: bool = False,
        **kwargs: Any,
    ) -> None:
        """Save this report as an Apache Parquet file.

        ???+ note "Changed in version 5.0"
            * This will no longer overwrite existing files by default
            * You can now pass additional keyword arguments to be passed
              to the `pq.write_table` function
            * This no longer returns a PyArrow table

        Parameters
        ----------
        path
            The path to save the file to.
        skip_date_conversion
            Whether or not to skip the conversion of "day" and "month"
            columns into a datetime format. If you choose to skip this,
            these columns will be left as strings.
        overwrite
            Whether to overwrite an existing file.

        Returns
        -------
        None
            This method doesn't return anything.

        Other Parameters
        ----------------
        **kwargs
            Additional arguments to pass to `pq.write_table`.

        Notes
        -----
        This requires `pyarrow` to be installed to use, which is an
        optional dependency.

        Examples
        --------
        >>> report.to_parquet("output.parquet")
        """

        if not utils.can_use("pyarrow"):
            raise MissingOptionalComponents("pyarrow")

        import pyarrow.parquet as pq

        path = process_path(path, ".parquet", overwrite=overwrite)
        pq.write_table(
            self.to_arrow(skip_date_conversion=skip_date_conversion),
            path,
            **kwargs,
        )

        _log.info(f"Saved report as Apache Parquet file to {path.resolve()}")
