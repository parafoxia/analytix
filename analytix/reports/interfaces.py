# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

from .resources import ResultTable


class Report:
    def __init__(self, data: dict) -> None:
        self.resource = ResultTable.from_json(data)

    @property
    def shape(self) -> tuple[int, int]:
        return (len(self.resource.rows), len(self.resource.column_headers))
