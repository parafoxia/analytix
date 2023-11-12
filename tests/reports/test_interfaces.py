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

import datetime as dt
import json
import re
from pathlib import Path
from unittest import mock

import pytest
from openpyxl import Workbook

from analytix import utils
from analytix.errors import DataFrameConversionError, MissingOptionalComponents
from analytix.reports.interfaces import Report
from analytix.reports.resources import ResultTable
from tests import MockFile


def test_report_init(report: Report, report_type, result_table: ResultTable):
    assert report.resource == result_table
    assert report.type == report_type
    assert report._shape == (7, 2)


def test_report_shape_property(report: Report):
    assert report.shape == (7, 2)


def test_report_columns_property(report: Report):
    assert report.columns == ["day", "views"]


def test_report_dimensions_property(report: Report):
    assert report.dimensions == ["day"]


def test_report_metrics_property(report: Report):
    assert report.metrics == ["views"]


@mock.patch("builtins.open")
def test_report_to_json_no_indent(
    mock_open, response_data: bytes, report: Report, caplog
):
    f = MockFile(response_data.decode("utf-8"))
    mock_open.return_value = f
    report.to_json("report.json")
    assert f.read_data == f.write_data
    assert "Saved report as JSON" in caplog.text


@mock.patch("builtins.open")
def test_report_to_json_with_indent_4(
    mock_open, response_data: bytes, report: Report, caplog
):
    f = MockFile(json.dumps(json.loads(response_data), indent=4))
    mock_open.return_value = f
    report.to_json("report.json", indent=4)
    assert f.read_data == f.write_data
    assert "Saved report as JSON" in caplog.text


@mock.patch("builtins.open")
def test_report_to_csv(mock_open, report_csv, report: Report, caplog):
    f = MockFile(report_csv)
    mock_open.return_value = f

    report.to_csv("report.csv")
    assert f.read_data == f.write_data
    assert "Saved report as CSV" in caplog.text


@mock.patch("builtins.open")
def test_report_to_tsv(mock_open, report_tsv, report: Report, caplog):
    f = MockFile(report_tsv)
    mock_open.return_value = f

    report.to_csv("report.tsv", delimiter="\t")
    assert f.read_data == f.write_data
    assert "Saved report as TSV" in caplog.text


@pytest.mark.skipif(not utils.can_use("openpyxl"), reason="openpyxl is not available")
@mock.patch.object(Workbook, "save", return_value=None)
@mock.patch.object(Workbook, "active", new_callable=mock.PropertyMock)
def test_report_to_excel(mock_active, mock_save, report: Report, caplog):
    # This needs Workbook to be imported globally, otherwise things
    # aren't mocked properly.
    wb = Workbook()
    mock_active.return_value = wb.create_sheet()

    report.to_excel("report.xlsx")
    mock_save.assert_called_with("report.xlsx")
    assert "Saved report as spreadsheet" in caplog.text

    ws = wb.active
    assert ws.title == "Analytics"
    assert len(list(ws.rows)) == 8

    for i, row in enumerate(ws.rows, start=-1):
        for j, cell in enumerate(row):
            if i == -1:
                assert cell.value == report.columns[j]
            else:
                assert cell.value == report.resource.rows[i][j]


@mock.patch.object(utils, "can_use", return_value=False)
def test_report_to_excel_without_openpyxl(_, report: Report):
    with pytest.raises(
        MissingOptionalComponents,
        match=re.escape(
            "some necessary libraries are not installed (hint: pip install openpyxl)"
        ),
    ):
        report.to_excel("report.xlsx")


@pytest.mark.skipif(not utils.can_use("pandas"), reason="pandas is not available")
def test_report_to_pandas(response_data, report: Report):
    import pandas as pd

    df = report.to_pandas()
    assert df.shape == (7, 2)
    assert list(df.columns) == report.columns

    assert df["day"][0] == pd.Timestamp(year=2022, month=6, day=20)
    for i, row in df.iterrows():
        assert list(row)[1:] == json.loads(response_data)["rows"][i][1:]


@pytest.mark.skipif(not utils.can_use("pandas"), reason="pandas is not available")
def test_report_to_pandas_skip_conversions(response_data, report: Report):
    df = report.to_pandas(skip_date_conversion=True)
    assert df.shape == (7, 2)
    assert list(df.columns) == report.columns

    assert df["day"][0] == "2022-06-20"
    for i, row in df.iterrows():
        assert list(row)[1:] == json.loads(response_data)["rows"][i][1:]


@pytest.mark.skipif(not utils.can_use("pandas"), reason="pandas is not available")
def test_report_to_pandas_empty_df(empty_report: Report):
    assert empty_report.shape == (0, 2)

    with pytest.raises(
        DataFrameConversionError,
        match="cannot convert to DataFrame as the returned data has no rows",
    ):
        empty_report.to_pandas()


@mock.patch.object(utils, "can_use", return_value=False)
def test_report_to_pandas_without_pandas(_, report: Report):
    with pytest.raises(
        MissingOptionalComponents,
        match=re.escape(
            "some necessary libraries are not installed (hint: pip install pandas)"
        ),
    ):
        report.to_pandas()


@pytest.mark.skipif(not utils.can_use("pyarrow"), reason="PyArrow is not available")
def test_report_to_arrow(report: Report):
    import pandas as pd

    table = report.to_arrow()
    assert table.shape == (7, 2)
    assert table.column_names == report.columns

    assert table["day"][0].as_py() == pd.Timestamp(year=2022, month=6, day=20)
    columns = list(zip(*report.resource.rows))

    for i, col in enumerate(table.itercolumns()):
        if i == 0:
            continue

        assert col.to_pylist() == list(columns[i])


@pytest.mark.skipif(not utils.can_use("pyarrow"), reason="PyArrow is not available")
def test_report_to_arrow_skip_conversions(report: Report):
    table = report.to_arrow(skip_date_conversion=True)
    assert table.shape == (7, 2)
    assert table.column_names == report.columns

    assert table["day"][0].as_py() == "2022-06-20"
    columns = list(zip(*report.resource.rows))

    for i, col in enumerate(table.itercolumns()):
        if i == 0:
            continue

        assert col.to_pylist() == list(columns[i])


@pytest.mark.skipif(not utils.can_use("pyarrow"), reason="PyArrow is not available")
def test_report_to_arrow_empty_df(empty_report: Report):
    assert empty_report.shape == (0, 2)

    with pytest.raises(
        DataFrameConversionError,
        match="cannot convert to Arrow table as the returned data has no rows",
    ):
        empty_report.to_arrow()


@mock.patch.object(utils, "can_use", return_value=False)
def test_report_to_arrow_without_pyarrow(_, report: Report):
    with pytest.raises(
        MissingOptionalComponents,
        match=re.escape(
            "some necessary libraries are not installed (hint: pip install pyarrow)"
        ),
    ):
        report.to_arrow()


@pytest.mark.skipif(not utils.can_use("polars"), reason="Polars is not available")
def test_report_to_polars(response_data, report: Report):
    df = report.to_polars()
    assert df.shape == (7, 2)
    assert list(df.columns) == report.columns

    assert df["day"][0] == dt.date(2022, 6, 20)
    for i, row in enumerate(df.rows()):
        assert list(row)[1:] == json.loads(response_data)["rows"][i][1:]


@pytest.mark.skipif(not utils.can_use("polars"), reason="Polars is not available")
def test_report_to_polars_skip_conversions(response_data, report: Report):
    df = report.to_polars(skip_date_conversion=True)
    assert df.shape == (7, 2)
    assert list(df.columns) == report.columns

    assert df["day"][0] == "2022-06-20"
    for i, row in enumerate(df.rows()):
        assert list(row)[1:] == json.loads(response_data)["rows"][i][1:]


@pytest.mark.skipif(not utils.can_use("polars"), reason="polars is not available")
def test_report_to_polars_empty_df(empty_report: Report):
    assert empty_report.shape == (0, 2)

    with pytest.raises(
        DataFrameConversionError,
        match="cannot convert to DataFrame as the returned data has no rows",
    ):
        empty_report.to_polars()


@mock.patch.object(utils, "can_use", return_value=False)
def test_report_to_polars_without_polars(_, report: Report):
    with pytest.raises(
        MissingOptionalComponents,
        match=re.escape(
            "some necessary libraries are not installed (hint: pip install polars)"
        ),
    ):
        report.to_polars()


@pytest.mark.skipif(not utils.can_use("pyarrow"), reason="PyArrow is not available")
def test_report_to_feather(report: Report):
    # The `to_feather` method uses the `to_arrow` method internally, and
    # additionally calls a PyArrow function to write the file. For this
    # reason, testing the write functionality seems largely unnecessary,
    # as any issues are likely outside of analytix's control.

    import pyarrow.feather as pf

    with mock.patch.object(pf, "write_feather") as mock_write:
        report.to_feather("report.feather")
        mock_write.assert_called_with(report.to_arrow(), Path("report.feather"))


@mock.patch.object(utils, "can_use", return_value=False)
def test_report_to_feather_without_pyarrow(_, report: Report):
    with pytest.raises(
        MissingOptionalComponents,
        match=re.escape(
            "some necessary libraries are not installed (hint: pip install pyarrow)"
        ),
    ):
        report.to_feather("report.feather")


@pytest.mark.skipif(not utils.can_use("pyarrow"), reason="PyArrow is not available")
def test_report_to_parquet(report: Report):
    # The `to_parquet` method uses the `to_arrow` method internally, and
    # additionally calls a PyArrow function to write the file. For this
    # reason, testing the write functionality seems largely unnecessary,
    # as any issues are likely outside of analytix's control.

    import pyarrow.parquet as pq

    with mock.patch.object(pq, "write_table") as mock_write:
        report.to_parquet("report.parquet")
        mock_write.assert_called_with(report.to_arrow(), Path("report.parquet"))


@mock.patch.object(utils, "can_use", return_value=False)
def test_report_to_parquet_without_pyarrow(_, report: Report):
    with pytest.raises(
        MissingOptionalComponents,
        match=re.escape(
            "some necessary libraries are not installed (hint: pip install pyarrow)"
        ),
    ):
        report.to_parquet("report.parquet")
