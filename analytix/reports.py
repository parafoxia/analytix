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

import json
import logging
import typing as t
from pathlib import Path

import aiofiles

import analytix
from analytix import errors
from analytix.abc import ReportType

if analytix.can_use(all, "pandas"):
    import pandas as pd

log = logging.getLogger(__name__)


class Report:
    """A class representing a YouTube Analytics API report. You will
    never need to manually create an instance of this.

    Args:
        data:
            The raw data retrieved from the API.
        type:
            The report type.
    """

    __slots__ = ("data", "type", "columns", "_ncolumns", "_nrows")

    def __init__(self, data: dict[t.Any, t.Any], type: ReportType) -> None:
        self.data = data
        self.type = type
        self.columns = [c["name"] for c in data["columnHeaders"]]
        self._ncolumns = len(self.columns)
        self._nrows = len(data["rows"])

    @property
    def shape(self) -> tuple[int, int]:
        """The shape of the report in the format ``(rows, columns)``."""

        return (self._nrows, self._ncolumns)

    def to_json(self, path: str, *, indent: int = 4) -> None:
        """Write the report data to a JSON file.

        Args:
            path:
                The path the file should be saved to.

        Keyword Args:
            indent:
                The amount of indentation the data should be written
                with. Defaults to ``4``.
        """

        if not path.endswith(".json"):
            path += ".json"

        with open(path, "w") as f:
            json.dump(self.data, f, indent=indent)

        log.info(f"Saved report as JSON to {Path(path).resolve()}")

    async def ato_json(self, path: str, *, indent: int = 4) -> None:
        """Asynchronously write the report data to a JSON file.

        Args:
            path:
                The path the file should be saved to.

        Keyword Args:
            indent:
                The amount of indentation the data should be written
                with. Defaults to ``4``.
        """

        if not path.endswith(".json"):
            path += ".json"

        async with aiofiles.open(path, "w") as f:
            await f.write(json.dumps(self.data, indent=indent))

        log.info(f"Saved report as JSON to {Path(path).resolve()}")

    def to_csv(self, path: str, *, delimiter: str = ",") -> None:
        """Write the report data to a CSV file.

        Args:
            path:
                The path the file should be saved to.

        Keyword Args:
            delimiter:
                The delimiter to use. Defaults to a comma. Passing a tab
                here will save the file as a TSV instead.
        """

        extension = ".tsv" if delimiter == "\t" else ".csv"

        if not path.endswith(extension):
            path += extension

        with open(path, "w") as f:
            f.write(f"{delimiter.join(self.columns)}\n")
            for row in self.data["rows"]:
                line = delimiter.join(f"{v}" for v in row)
                f.write(f"{line}\n")

        log.info(f"Saved report as CSV to {Path(path).resolve()}")

    async def ato_csv(self, path: str, *, delimiter: str = ",") -> None:
        """Asynchronously write the report data to a CSV file.

        Args:
            path:
                The path the file should be saved to.

        Keyword Args:
            delimiter:
                The delimiter to use. Defaults to a comma. Passing a tab
                here will save the file as a TSV instead.
        """

        extension = ".tsv" if delimiter == "\t" else ".csv"

        if not path.endswith(extension):
            path += extension

        async with aiofiles.open(path, "w") as f:
            await f.write(f"{delimiter.join(self.columns)}\n")
            for row in self.data["rows"]:
                line = delimiter.join(f"{v}" for v in row)
                await f.write(f"{line}\n")

        log.info(f"Saved report as CSV to {Path(path).resolve()}")

    def to_dataframe(self, *, skip_date_conversion: bool = False) -> pd.DataFrame:
        """Export the report data to a pandas DataFrame.

        .. note::
            The pandas library is required to do this, but is not
            automatically installed by analytix.

        Keyword Args:
            skip_date_conversion:
                Whether to skip automatically converting date columns to
                the ``datetime64[ns]`` format. Defaults to ``False``.
        """

        if not analytix.can_use(all, "pandas"):
            raise errors.MissingOptionalComponents("pandas")

        if not self._nrows:
            raise errors.DataFrameConversionError(
                "cannot convert to DataFrame as the returned data has no rows"
            )

        df = pd.DataFrame(self.data["rows"])
        df.columns = self.columns

        if not skip_date_conversion:
            for col in ("day", "month"):
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], format="%Y-%m-%d")
                    log.info(f"Converted {col!r} column to datetime64[ns] format")

        return df
