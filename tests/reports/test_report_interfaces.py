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
import sys
from pathlib import Path

import pytest
from openpyxl import Workbook

import analytix
from analytix.errors import DataFrameConversionError, MissingOptionalComponents
from analytix.reports.interfaces import (
    AnalyticsReport,
    ColumnHeader,
    ColumnType,
    DataType,
    ResultTable,
)
from analytix.reports.types import GeographyBasedActivity, TimeBasedActivity
from tests import MockFile, create_request_data

if sys.version_info >= (3, 8):
    from unittest import mock
else:
    import mock


def test_data_type_enum():
    assert DataType.STRING.value == "STRING"
    assert DataType.INTEGER.value == "INTEGER"
    assert DataType.FLOAT.value == "FLOAT"

    assert DataType("STRING") == DataType.STRING
    assert DataType("INTEGER") == DataType.INTEGER
    assert DataType("FLOAT") == DataType.FLOAT


def test_column_type_enum():
    assert ColumnType.DIMENSION.value == "DIMENSION"
    assert ColumnType.METRIC.value == "METRIC"

    assert ColumnType("DIMENSION") == ColumnType.DIMENSION
    assert ColumnType("METRIC") == ColumnType.METRIC


@pytest.fixture()
def column_header():
    return ColumnHeader("views", DataType.INTEGER, ColumnType.DIMENSION)


def test_create_column_header(column_header):
    assert column_header.name == "views"
    assert column_header.data_type == DataType.INTEGER
    assert column_header.column_type == ColumnType.DIMENSION


def test_column_header_data_property(column_header):
    assert column_header.data == {
        "name": "views",
        "dataType": "INTEGER",
        "columnType": "DIMENSION",
    }


@pytest.fixture()
def request_data():
    return json.loads(create_request_data())


@pytest.fixture()
def report_type():
    return TimeBasedActivity()


@pytest.fixture()
def result_table():
    return ResultTable(
        "youtubeAnalytics#resultTable",
        [
            ColumnHeader("day", DataType.STRING, ColumnType.DIMENSION),
            ColumnHeader("views", DataType.INTEGER, ColumnType.METRIC),
            ColumnHeader("likes", DataType.INTEGER, ColumnType.METRIC),
            ColumnHeader("comments", DataType.INTEGER, ColumnType.METRIC),
            ColumnHeader("grossRevenue", DataType.FLOAT, ColumnType.METRIC),
        ],
        [
            ["2022-06-20", 778, 8, 0, 2.249],
            ["2022-06-21", 1062, 32, 8, 3.558],
            ["2022-06-22", 946, 38, 6, 2.91],
            ["2022-06-23", 5107, 199, 15, 24.428],
            ["2022-06-24", 2137, 61, 2, 6.691],
            ["2022-06-25", 1005, 31, 6, 4.316],
            ["2022-06-26", 888, 12, 1, 4.206],
        ],
    )


def test_create_result_table_from_json(request_data, result_table):
    assert ResultTable.from_json(request_data) == result_table


def test_result_table_data_property(request_data, result_table):
    assert result_table.data == request_data


@pytest.fixture()
def report(request_data, report_type):
    return AnalyticsReport(request_data, report_type)


def test_create_report(report, result_table, report_type):
    assert report.resource == result_table
    assert report.type == report_type
    assert report._shape == (7, 5)


def test_report_equal(report, request_data):
    assert report == AnalyticsReport(request_data, TimeBasedActivity())
    assert not report == AnalyticsReport(request_data, GeographyBasedActivity())
    assert not report == TimeBasedActivity()


def test_report_not_equal(report, request_data):
    assert not report != AnalyticsReport(request_data, TimeBasedActivity())
    assert report != AnalyticsReport(request_data, GeographyBasedActivity())
    assert report != TimeBasedActivity()


def test_report_shape_property(report):
    assert report.shape == report._shape
    assert report.shape == (7, 5)


@pytest.mark.dependency()
def test_report_columns_property(report):
    assert report.columns == ["day", "views", "likes", "comments", "grossRevenue"]


def test_report_dimensions_property(report):
    assert report.dimensions == ["day"]


def test_report_metrics_property(report):
    assert report.metrics == ["views", "likes", "comments", "grossRevenue"]


def test_report_numeric_property(report):
    assert report.numeric == ["views", "likes", "comments", "grossRevenue"]


def test_report_non_numeric_property(report):
    assert report.non_numeric == ["day"]


@mock.patch("builtins.open")
def test_report_to_json_indent_4(mock_open, request_data, report: AnalyticsReport):
    f = MockFile(json.dumps(request_data))
    mock_open.return_value = f

    report.to_json("report.json")
    assert f.write_data == json.dumps(request_data, indent=4)


@mock.patch("builtins.open")
def test_report_to_json_indent_0(mock_open, request_data, report: AnalyticsReport):
    f = MockFile(json.dumps(request_data))
    mock_open.return_value = f

    report.to_json("report.json", indent=None)
    assert f.write_data == json.dumps(request_data)


@pytest.fixture()
def report_csv():
    return """day,views,likes,comments,grossRevenue
2022-06-20,778,8,0,2.249
2022-06-21,1062,32,8,3.558
2022-06-22,946,38,6,2.91
2022-06-23,5107,199,15,24.428
2022-06-24,2137,61,2,6.691
2022-06-25,1005,31,6,4.316
2022-06-26,888,12,1,4.206
"""


@pytest.fixture()
def report_tsv():
    return """day\tviews\tlikes\tcomments\tgrossRevenue
2022-06-20\t778\t8\t0\t2.249
2022-06-21\t1062\t32\t8\t3.558
2022-06-22\t946\t38\t6\t2.91
2022-06-23\t5107\t199\t15\t24.428
2022-06-24\t2137\t61\t2\t6.691
2022-06-25\t1005\t31\t6\t4.316
2022-06-26\t888\t12\t1\t4.206
"""


@pytest.mark.dependency()
@mock.patch("builtins.open")
def test_report_to_csv(mock_open, report_csv, report: AnalyticsReport, caplog):
    f = MockFile(report_csv)
    mock_open.return_value = f

    report.to_csv("report.csv")
    assert f.write_data == report_csv
    assert "Saved report as CSV" in caplog.text


@pytest.mark.dependency(depends=["test_report_to_csv"])
@mock.patch("builtins.open")
def test_report_to_tsv(mock_open, report_tsv, report: AnalyticsReport, caplog):
    f = MockFile(report_tsv)
    mock_open.return_value = f

    report.to_csv("report.tsv", delimiter="\t")
    assert f.write_data == report_tsv
    assert "Saved report as TSV" in caplog.text


@mock.patch.object(Workbook, "save", return_value=None)
@mock.patch.object(Workbook, "active", new_callable=mock.PropertyMock)
def test_report_to_excel(mock_active, mock_save, report: AnalyticsReport, caplog):
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


@mock.patch("analytix.can_use", return_value=False)
def test_report_to_excel_without_openpyxl(_, report: AnalyticsReport):
    with pytest.raises(
        MissingOptionalComponents,
        match=re.escape(
            "some necessary libraries are not installed (hint: pip install openpyxl)"
        ),
    ):
        report.to_excel("report.xlsx")


@pytest.mark.dependency(depends=["test_report_columns_property"])
@pytest.mark.skipif(not analytix.can_use("pandas"), reason="pandas is not available")
def test_report_to_pandas(request_data, report: AnalyticsReport):
    import pandas as pd

    df = report.to_pandas()
    assert df.shape == (7, 5)
    assert list(df.columns) == report.columns

    assert df["day"][0] == pd.Timestamp(year=2022, month=6, day=20)
    for i, row in df.iterrows():
        assert list(row)[1:] == request_data["rows"][i][1:]


@pytest.mark.dependency(depends=["test_report_columns_property"])
@pytest.mark.skipif(not analytix.can_use("pandas"), reason="pandas is not available")
def test_report_to_pandas_skip_conversions(request_data, report: AnalyticsReport):
    df = report.to_pandas(skip_date_conversion=True)
    assert df.shape == (7, 5)
    assert list(df.columns) == report.columns

    assert df["day"][0] == "2022-06-20"
    for i, row in df.iterrows():
        assert list(row)[1:] == request_data["rows"][i][1:]


@pytest.fixture()
def empty_report(report_type):
    return AnalyticsReport(
        {
            "kind": "youtubeAnalytics#resultTable",
            "columnHeaders": [
                {"name": "day", "dataType": "STRING", "columnType": "DIMENSION"},
                {"name": "views", "dataType": "INTEGER", "columnType": "METRIC"},
                {"name": "likes", "dataType": "INTEGER", "columnType": "METRIC"},
                {"name": "comments", "dataType": "INTEGER", "columnType": "METRIC"},
                {"name": "grossRevenue", "dataType": "FLOAT", "columnType": "METRIC"},
            ],
            "rows": [],
        },
        report_type,
    )


@pytest.mark.dependency(depends=["test_report_columns_property"])
@pytest.mark.skipif(not analytix.can_use("pandas"), reason="pandas is not available")
def test_report_to_pandas_empty_df(empty_report: AnalyticsReport):
    assert empty_report.shape == (0, 5)

    with pytest.raises(
        DataFrameConversionError,
        match="cannot convert to DataFrame as the returned data has no rows",
    ):
        empty_report.to_pandas()


@mock.patch("analytix.can_use", return_value=False)
def test_report_to_pandas_without_pandas(_, report: AnalyticsReport):
    with pytest.raises(
        MissingOptionalComponents,
        match=re.escape(
            "some necessary libraries are not installed (hint: pip install pandas)"
        ),
    ):
        report.to_pandas()


@pytest.mark.dependency(
    depends=["test_report_columns_property", "test_report_to_pandas"]
)
@pytest.mark.skipif(not analytix.can_use("pyarrow"), reason="PyArrow is not available")
def test_report_to_arrow(report: AnalyticsReport):
    import pandas as pd

    table = report.to_arrow()
    assert table.shape == (7, 5)
    assert table.column_names == report.columns

    assert table["day"][0].as_py() == pd.Timestamp(year=2022, month=6, day=20)
    columns = list(zip(*report.resource.rows))

    for i, col in enumerate(table.itercolumns()):
        if i == 0:
            continue

        assert col.to_pylist() == list(columns[i])


@pytest.mark.dependency(
    depends=["test_report_columns_property", "test_report_to_pandas"]
)
@pytest.mark.skipif(not analytix.can_use("pyarrow"), reason="PyArrow is not available")
def test_report_to_arrow_skip_conversions(report: AnalyticsReport):
    table = report.to_arrow(skip_date_conversion=True)
    assert table.shape == (7, 5)
    assert table.column_names == report.columns

    assert table["day"][0].as_py() == "2022-06-20"
    columns = list(zip(*report.resource.rows))

    for i, col in enumerate(table.itercolumns()):
        if i == 0:
            continue

        assert col.to_pylist() == list(columns[i])


@pytest.mark.dependency(depends=["test_report_columns_property"])
@pytest.mark.skipif(not analytix.can_use("pyarrow"), reason="PyArrow is not available")
def test_report_to_arrow_empty_df(empty_report: AnalyticsReport):
    assert empty_report.shape == (0, 5)

    with pytest.raises(
        DataFrameConversionError,
        match="cannot convert to Arrow table as the returned data has no rows",
    ):
        empty_report.to_arrow()


@mock.patch("analytix.can_use", return_value=False)
def test_report_to_arrow_without_pyarrow(_, report: AnalyticsReport):
    with pytest.raises(
        MissingOptionalComponents,
        match=re.escape(
            "some necessary libraries are not installed (hint: pip install pyarrow)"
        ),
    ):
        report.to_arrow()


@pytest.mark.dependency(depends=["test_report_columns_property"])
@pytest.mark.skipif(not analytix.can_use("polars"), reason="Polars is not available")
def test_report_to_polars(request_data, report: AnalyticsReport):
    df = report.to_polars()
    assert df.shape == (7, 5)
    assert list(df.columns) == report.columns

    assert df["day"][0] == dt.date(2022, 6, 20)
    for i, row in enumerate(df.rows()):
        assert list(row)[1:] == request_data["rows"][i][1:]


@pytest.mark.dependency(depends=["test_report_columns_property"])
@pytest.mark.skipif(not analytix.can_use("polars"), reason="Polars is not available")
def test_report_to_polars_skip_conversions(request_data, report: AnalyticsReport):
    df = report.to_polars(skip_date_conversion=True)
    assert df.shape == (7, 5)
    assert list(df.columns) == report.columns

    assert df["day"][0] == "2022-06-20"
    for i, row in enumerate(df.rows()):
        assert list(row)[1:] == request_data["rows"][i][1:]


@pytest.mark.dependency(depends=["test_report_columns_property"])
@pytest.mark.skipif(not analytix.can_use("polars"), reason="polars is not available")
def test_report_to_polars_empty_df(empty_report: AnalyticsReport):
    assert empty_report.shape == (0, 5)

    with pytest.raises(
        DataFrameConversionError,
        match="cannot convert to DataFrame as the returned data has no rows",
    ):
        empty_report.to_polars()


@mock.patch("analytix.can_use", return_value=False)
def test_report_to_polars_without_polars(_, report: AnalyticsReport):
    with pytest.raises(
        MissingOptionalComponents,
        match=re.escape(
            "some necessary libraries are not installed (hint: pip install polars)"
        ),
    ):
        report.to_polars()


@pytest.mark.dependency(
    depends=["test_report_columns_property", "test_report_to_arrow"]
)
@pytest.mark.skipif(not analytix.can_use("pyarrow"), reason="PyArrow is not available")
def test_report_to_feather(report: AnalyticsReport):
    # The `to_feather` method uses the `to_arrow` method internally, and
    # additionally calls a PyArrow function to write the file. For this
    # reason, testing the write functionality seems largely unnecessary,
    # as any issues are likely outside of analytix's control.

    import pyarrow.feather as pf

    with mock.patch.object(pf, "write_feather") as mock_write:
        report.to_feather("report.feather")
        mock_write.assert_called_with(report.to_arrow(), Path("report.feather"))


@mock.patch("analytix.can_use", return_value=False)
def test_report_to_feather_without_pyarrow(_, report: AnalyticsReport):
    with pytest.raises(
        MissingOptionalComponents,
        match=re.escape(
            "some necessary libraries are not installed (hint: pip install pyarrow)"
        ),
    ):
        report.to_feather("report.feather")


@pytest.mark.dependency(
    depends=["test_report_columns_property", "test_report_to_arrow"]
)
@pytest.mark.skipif(not analytix.can_use("pyarrow"), reason="PyArrow is not available")
def test_report_to_parquet(report: AnalyticsReport):
    # The `to_parquet` method uses the `to_arrow` method internally, and
    # additionally calls a PyArrow function to write the file. For this
    # reason, testing the write functionality seems largely unnecessary,
    # as any issues are likely outside of analytix's control.

    import pyarrow.parquet as pq

    with mock.patch.object(pq, "write_table") as mock_write:
        report.to_parquet("report.parquet")
        mock_write.assert_called_with(report.to_arrow(), Path("report.parquet"))


@mock.patch("analytix.can_use", return_value=False)
def test_report_to_parquet_without_pyarrow(_, report: AnalyticsReport):
    with pytest.raises(
        MissingOptionalComponents,
        match=re.escape(
            "some necessary libraries are not installed (hint: pip install pyarrow)"
        ),
    ):
        report.to_parquet("report.parquet")
