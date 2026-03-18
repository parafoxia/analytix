# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause


from analytix.reports.resources import ColumnHeader
from analytix.reports.resources import ColumnType
from analytix.reports.resources import DataType
from analytix.reports.resources import ResultTable


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


def test_column_header_dimension_init(column_header_dimension: ColumnHeader):
    assert column_header_dimension.name == "day"
    assert column_header_dimension.data_type == DataType.STRING
    assert column_header_dimension.data_type.value == "STRING"
    assert column_header_dimension.column_type == ColumnType.DIMENSION
    assert column_header_dimension.column_type.value == "DIMENSION"


def test_column_header_dimension_data_property(
    column_header_dimension: ColumnHeader,
    column_header_dimension_data,
):
    assert column_header_dimension.data == column_header_dimension_data


def test_column_header_metric_init(column_header_metric: ColumnHeader):
    assert column_header_metric.name == "views"
    assert column_header_metric.data_type == DataType.INTEGER
    assert column_header_metric.data_type.value == "INTEGER"
    assert column_header_metric.column_type == ColumnType.METRIC
    assert column_header_metric.column_type.value == "METRIC"


def test_column_header_metric_data_property(
    column_header_metric: ColumnHeader,
    column_header_metric_data,
):
    assert column_header_metric.data == column_header_metric_data


def test_result_table_init(result_table: ResultTable, column_headers, row_data):
    assert result_table.kind == "youtubeAnalytics#resultTable"
    assert result_table.column_headers == column_headers
    assert result_table.rows == row_data


def test_result_table_from_json(result_table: ResultTable, result_table_data):
    assert ResultTable.from_json(result_table_data) == result_table


def test_result_table_data_property(result_table: ResultTable, result_table_data):
    assert result_table.data == result_table_data
