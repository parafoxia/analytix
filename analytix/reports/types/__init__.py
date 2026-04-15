# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

from collections.abc import Collection
from dataclasses import dataclass
from dataclasses import field

from analytix.errors import ValidationError
from analytix.reports.constraints import ZeroOrMore
from analytix.reports.parameters import Dimensions
from analytix.reports.parameters import Filters
from analytix.reports.parameters import Metrics
from analytix.reports.parameters import SortOptions


@dataclass(slots=True, kw_only=True)
class ReportType:
    name: str
    metrics: Metrics
    dimensions: Dimensions = field(default_factory=Dimensions)
    filters: Filters = field(default_factory=Filters)
    sort_options: SortOptions = field(default_factory=SortOptions)
    max_results: int = 0

    def __post_init__(self) -> None:
        if not self.sort_options.constraints:
            # If this isn't defined, assume any metric can be used.
            self.sort_options.constraints = (ZeroOrMore(*self.metrics.all_keys),)

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return id(self)

    def validate(
        self,
        *,
        input_dimensions: Collection[str],
        input_filters: dict[str, str],
        input_metrics: Collection[str],
        input_sort_options: Collection[str],
        max_results: int = 0,
        start_index: int = 1,
    ) -> list[ValidationError]:
        errors = [
            *self.dimensions.validate(input_dimensions),
            *self.filters.validate(input_filters),
            *self.metrics.validate(input_metrics),
            *self.sort_options.validate(input_sort_options),
        ]

        metrics = input_metrics or self.metrics.all_keys
        if diff := {o.strip("-") for o in input_sort_options} - set(metrics):
            err = ValidationError(
                "sort options must be a subset of the requested (or available) metrics",
            )
            err.add_note(f"Offending sort options: {', '.join(diff)}")
            errors.append(err)

        if self.max_results:
            if not max_results:
                errors.append(ValidationError("expected a maximum number of results"))
            elif max_results > self.max_results:
                errors.append(
                    ValidationError(
                        f"expected no more than {self.max_results} results, got "
                        f"{max_results:,}",
                    ),
                )

            if start_index + max_results > self.max_results + 1:
                errors.append(ValidationError("the start index is too high"))

        return errors
