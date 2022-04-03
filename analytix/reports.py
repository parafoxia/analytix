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

import datetime as dt
import json
import logging
import typing as t
from pathlib import Path

import aiofiles

import analytix
from analytix import errors
from analytix.abc import DynamicReportWriter

if t.TYPE_CHECKING:
    import pandas as pd
    import pyarrow as pa

    from analytix.abc import ReportType

log = logging.getLogger(__name__)


class JSONReportWriter(DynamicReportWriter):
    __slots__ = ()

    def _run_sync(self) -> None:
        if not self._path.endswith(".json"):
            self._path += ".json"

        with open(self._path, "w") as f:
            json.dump(self._data, f, indent=self._indent)

        return log.info(f"Saved report as JSON to {Path(self._path).resolve()}")

    async def _run_async(self) -> None:
        if not self._path.endswith(".json"):
            self._path += ".json"

        async with aiofiles.open(self._path, "w") as f:
            await f.write(json.dumps(self._data, indent=self._indent))

        return log.info(f"Saved report as JSON to {Path(self._path).resolve()}")


class CSVReportWriter(DynamicReportWriter):
    __slots__ = ()

    def _run_sync(self) -> None:
        extension = ".tsv" if self._delimiter == "\t" else ".csv"

        if not self._path.endswith(extension):
            self._path += extension

        with open(self._path, "w") as f:
            f.write(f"{self._delimiter.join(self._columns)}\n")
            for row in self._data["rows"]:
                line = self._delimiter.join(f"{v}" for v in row)
                f.write(f"{line}\n")

        return log.info(f"Saved report as CSV to {Path(self._path).resolve()}")

    async def _run_async(self) -> None:
        extension = ".tsv" if self._delimiter == "\t" else ".csv"

        if not self._path.endswith(extension):
            self._path += extension

        async with aiofiles.open(self._path, "w") as f:
            await f.write(f"{self._delimiter.join(self._columns)}\n")
            for row in self._data["rows"]:
                line = self._delimiter.join(f"{v}" for v in row)
                await f.write(f"{line}\n")

        return log.info(f"Saved report as CSV to {Path(self._path).resolve()}")


class Report:
    """A class representing a YouTube Analytics API report. You will
    never need to manually create an instance of this.

    Args:
        data:
            The raw data retrieved from the API.
        type:
            The report type.
    """

    __slots__ = ("data", "type", "columns", "_shape")

    def __init__(self, data: dict[t.Any, t.Any], type: ReportType) -> None:
        self.data = data
        self.type = type
        self.columns = [c["name"] for c in data["columnHeaders"]]
        self._shape = (len(data["rows"]), len(self.columns))

    @property
    def shape(self) -> tuple[int, int]:
        """The shape of the report in the format ``(rows, columns)``."""

        return self._shape

    @property
    def dimensions(self) -> set[str]:
        """The names of columns which are dimensions in the report.

        .. versionadded:: 3.3.0
        """

        return set(self.columns) - self.type.metrics.values

    @property
    def metrics(self) -> set[str]:
        """The names of columns which are metrics in the report.

        .. versionadded:: 3.3.0
        """

        return self.type.metrics.values

    def to_dataframe(self, *, skip_date_conversion: bool = False) -> pd.DataFrame:
        """Export the report data to a pandas or Modin DataFrame. If you
        wish to use Modin, you are responsible for selecting and
        initialising your desired engine.

        Keyword Args:
            skip_date_conversion:
                Whether to skip automatically converting date columns to
                the ``datetime64[ns]`` format. Defaults to ``False``.

        Returns:
            The newly created DataFrame.
        """

        if analytix.can_use("modin"):
            import modin.pandas as pd
        elif analytix.can_use("pandas"):
            import pandas as pd
        else:
            raise errors.MissingOptionalComponents("pandas")

        if not self._shape[0]:
            raise errors.DataFrameConversionError(
                "cannot convert to DataFrame as the returned data has no rows"
            )

        df = pd.DataFrame(self.data["rows"], columns=self.columns)

        if not skip_date_conversion:
            for col in ("day", "month"):
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], format="%Y-%m-%d")
                    log.info(f"Converted {col!r} column to datetime64[ns] format")
                    break

        return df

    def to_arrow_table(self, *, skip_date_conversion: bool = False) -> pa.Table:
        """Export the report data to an Apache Arrow Table.

        Keyword Args:
            skip_date_conversion:
                Whether to skip automatically converting date columns to
                the ``datetime64[ns]`` format. Defaults to ``False``.

        Returns:
            The newly constructed Apache Arrow Table.

        .. versionadded:: 3.2.0
        """

        if analytix.can_use("pyarrow"):
            import pyarrow as pa
        else:
            raise errors.MissingOptionalComponents("pyarrow")

        data = list(zip(*self.data["rows"]))

        if not skip_date_conversion:
            for i, col in enumerate(data):
                if isinstance(col[0], str) and "-" in col[0]:
                    fmt = f"%Y-%m{'-%d'if len(col[0].split('-')) == 3 else ''}"
                    data[i] = [dt.datetime.strptime(record, fmt) for record in data[i]]
                    log.info("Converted time-series column to timestamp[us] format")
                    break

        table = pa.Table.from_arrays(data, names=self.columns)
        return table

    def to_json(self, path: str, *, indent: int = 4) -> JSONReportWriter:
        """Write the report data to a JSON file.

        .. note::
            This method can also be run asynchronously by awaiting it.

        Args:
            path:
                The path the file should be saved to.

        Keyword Args:
            indent:
                The amount of indentation the data should be written
                with. Defaults to ``4``.

        Returns:
            The report writer. This is done to allow this method to run
            sync or async in a typed context.
        """

        return JSONReportWriter(path, data=self.data, indent=indent)

    async def ato_json(self, path: str, *, indent: int = 4) -> None:
        log.warning(
            "The `report.ato_json` method is deprecated -- "
            "use `await report.to_json` instead"
        )
        await self.to_json(path, indent=indent)

    def to_csv(self, path: str, *, delimiter: str = ",") -> CSVReportWriter:
        """Write the report data to a CSV file.

        .. note::
            This method can also be run asynchronously by awaiting it.

        Args:
            path:
                The path the file should be saved to.

        Keyword Args:
            delimiter:
                The delimiter to use. Defaults to a comma. Passing a tab
                here will save the file as a TSV instead.

        Returns:
            The report writer. This is done to allow this method to run
            sync or async in a typed context.
        """

        return CSVReportWriter(
            path,
            data=self.data,
            delimiter=delimiter,
            columns=self.columns,
        )

    async def ato_csv(self, path: str, *, delimiter: str = ",") -> None:
        log.warning(
            "The `report.ato_csv` method is deprecated -- "
            "use `await report.to_csv` instead"
        )
        await self.to_csv(path, delimiter=delimiter)

    def to_excel(self, path: str, *, sheet_name: str = "Analytics") -> None:
        """Write the report data to an Excel spreadsheet.

        Args:
            path:
                The path the file should be saved to.

        Keyword Args:
            sheet_name:
                The name for the worksheet.

        .. versionadded:: 3.1.0
        """

        if analytix.can_use("openpyxl"):
            from openpyxl import Workbook
        else:
            raise errors.MissingOptionalComponents("openpyxl")

        if not path.endswith(".xlsx"):
            path += ".xlsx"

        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name

        ws.append(self.columns)
        for row in self.data["rows"]:
            ws.append(row)

        wb.save(path)
        log.info(f"Saved report as spreadsheet to {Path(path).resolve()}")

    def to_feather(self, path: str) -> None:
        """Write the report data to an Apache Feather file.

        Args:
            path:
                The path the file should be saved to.

        .. versionadded:: 3.2.0
        """

        if analytix.can_use("pyarrow"):
            import pyarrow.feather as pf
        else:
            raise errors.MissingOptionalComponents("pyarrow")

        if not path.endswith(".feather"):
            path += ".feather"

        pf.write_feather(self.to_arrow_table(), path)
        log.info(f"Saved report as Apache Feather file to {Path(path).resolve()}")

    def to_parquet(self, path: str) -> None:
        """Write the report data to an Apache Parquet file.

        Args:
            path:
                The path the file should be saved to.

        .. versionadded:: 3.2.0
        """

        if analytix.can_use("pyarrow"):
            import pyarrow.parquet as pq
        else:
            raise errors.MissingOptionalComponents("pyarrow")

        if not path.endswith(".parquet"):
            path += ".parquet"

        pq.write_table(self.to_arrow_table(), path)
        log.info(f"Saved report as Apache Parquet file to {Path(path).resolve()}")
