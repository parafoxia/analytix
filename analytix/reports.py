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
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import analytix
from analytix import errors
from analytix.utils import requires

if t.TYPE_CHECKING:
    import pandas as pd
    import pyarrow as pa

    from analytix.abc import ReportType
    from analytix.types import PathLikeT, ResponseT

_log = logging.getLogger(__name__)


class DataType(Enum):
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"


class ColumnType(Enum):
    DIMENSION = "DIMENSION"
    METRIC = "METRIC"


@dataclass(frozen=True)
class ColumnHeader:
    __slots__ = ("name", "data_type", "column_type")

    name: str
    data_type: DataType
    column_type: ColumnType

    @property
    def data(self) -> ResponseT:
        return {
            "name": self.name,
            "dataType": self.data_type.value,
            "columnType": self.column_type.value,
        }


@dataclass(frozen=True)
class ResultTable:
    kind: str
    column_headers: list[ColumnHeader]
    rows: list[list[str | int | float]]

    @classmethod
    def from_json(cls, data: ResponseT) -> ResultTable:
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
        return {
            "kind": self.kind,
            "columnHeaders": [header.data for header in self.column_headers],
            "rows": self.rows,
        }


class AnalyticsReport:
    def __init__(self, data: ResponseT, type: ReportType) -> None:
        self.resource = ResultTable.from_json(data)
        self.type = type
        self._shape = (len(data["rows"]), len(self.resource.column_headers))

    @property
    def shape(self) -> tuple[int, int]:
        return self._shape

    @property
    def columns(self) -> list[str]:
        return [c.name for c in self.resource.column_headers]

    @property
    def dimensions(self) -> list[str]:
        return [
            c.name
            for c in self.resource.column_headers
            if c.column_type == ColumnType.DIMENSION
        ]

    @property
    def metrics(self) -> list[str]:
        return [
            c.name
            for c in self.resource.column_headers
            if c.column_type == ColumnType.METRIC
        ]

    @property
    def numeric(self) -> list[str]:
        return [
            c.name
            for c in self.resource.column_headers
            if c.data_type != DataType.STRING
        ]

    @property
    def non_numeric(self) -> list[str]:
        return [
            c.name
            for c in self.resource.column_headers
            if c.data_type == DataType.STRING
        ]

    def _set_and_validate_path(
        self, path: PathLikeT, extension: str, overwrite: bool
    ) -> Path:
        if not isinstance(path, Path):
            path = Path(path)

        if path.suffix != extension:
            path = Path(path.name + extension)

        if not overwrite and path.is_file():
            raise FileExistsError("file already exists and `overwrite` is set to False")

        return path

    def to_json(
        self, path: PathLikeT, *, indent: int = 4, overwrite: bool = True
    ) -> ResponseT:
        path = self._set_and_validate_path(path, ".json", overwrite)
        data = self.resource.data

        with open(path, "w") as f:
            json.dump(data, f, indent=indent)

        _log.info(f"Saved report as JSON to {path.resolve()}")
        return data

    def to_csv(
        self, path: PathLikeT, *, delimiter: str = ",", overwrite: bool = True
    ) -> None:
        extension = ".tsv" if delimiter == "\t" else ".csv"
        path = self._set_and_validate_path(path, extension, overwrite)

        with open(path, "w") as f:
            f.write(f"{delimiter.join(self.columns)}\n")
            for row in self.resource.data["rows"]:
                line = delimiter.join(f"{v}" for v in row)
                f.write(f"{line}\n")

        _log.info(f"Saved report as {extension[1:].upper()} to {path.resolve()}")

    @requires("openpyxl")
    def to_excel(
        self, path: PathLikeT, *, sheet_name: str = "Analytics", overwrite: bool = True
    ) -> None:
        from openpyxl import Workbook

        path = self._set_and_validate_path(path, ".xlsx", overwrite)
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name

        ws.append(self.columns)
        for row in self.resource.data["rows"]:
            ws.append(row)

        wb.save(path)
        _log.info(f"Saved report as spreadsheet to {path.resolve()}")

    def to_dataframe(self, *, skip_date_conversion: bool = False) -> pd.DataFrame:
        if analytix.can_use("modin"):
            import modin.pandas as pd
        elif analytix.can_use("pandas", required=True):
            import pandas as pd

        if not self._shape[0]:
            raise errors.DataFrameConversionError(
                "cannot convert to DataFrame as the returned data has no rows"
            )

        df = pd.DataFrame(self.resource.data["rows"], columns=self.columns)

        if not skip_date_conversion:
            for col in ("day", "month"):
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], format="%Y-%m-%d")
                    _log.info(f"Converted {col!r} column to datetime64[ns] format")
                    break

        return df

    @requires("pyarrow")
    def to_arrow_table(self, *, skip_date_conversion: bool = False) -> pa.Table:
        import pyarrow as pa

        data = list(zip(*self.resource.data["rows"]))

        if not skip_date_conversion:
            for i, col in enumerate(data):
                if isinstance(col[0], str) and "-" in col[0]:
                    fmt = f"%Y-%m{'-%d'if len(col[0].split('-')) == 3 else ''}"
                    data[i] = [dt.datetime.strptime(record, fmt) for record in data[i]]
                    _log.info("Converted time-series column to timestamp[us] format")
                    break

        return pa.Table.from_arrays(data, names=self.columns)

    @requires("pyarrow")
    def to_feather(
        self,
        path: PathLikeT,
        *,
        skip_date_conversion: bool = False,
        overwrite: bool = True,
    ) -> pa.Table:
        import pyarrow.feather as pf

        path = self._set_and_validate_path(path, ".feather", overwrite)
        pf.write_feather(
            self.to_arrow_table(skip_date_conversion=skip_date_conversion), path
        )
        _log.info(f"Saved report as Apache Feather file to {path.resolve()}")

    @requires("pyarrow")
    def to_parquet(
        self,
        path: PathLikeT,
        *,
        skip_date_conversion: bool = False,
        overwrite: bool = True,
    ) -> pa.Table:
        import pyarrow.parquet as pq

        path = self._set_and_validate_path(path, ".parquet", overwrite)
        pq.write_table(
            self.to_arrow_table(skip_date_conversion=skip_date_conversion), path
        )
        _log.info(f"Saved report as Apache Parquet file to {path.resolve()}")
