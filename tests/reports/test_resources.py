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


from analytix.reports.resources import ColumnHeader, ColumnType, DataType, ResultTable


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
    column_header_dimension: ColumnHeader, column_header_dimension_data
):
    assert column_header_dimension.data == column_header_dimension_data


def test_column_header_metric_init(column_header_metric: ColumnHeader):
    assert column_header_metric.name == "views"
    assert column_header_metric.data_type == DataType.INTEGER
    assert column_header_metric.data_type.value == "INTEGER"
    assert column_header_metric.column_type == ColumnType.METRIC
    assert column_header_metric.column_type.value == "METRIC"


def test_column_header_metric_data_property(
    column_header_metric: ColumnHeader, column_header_metric_data
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
