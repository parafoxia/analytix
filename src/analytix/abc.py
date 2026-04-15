# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-FileCopyrightText: 2022 Jonxslays
# SPDX-License-Identifier: BSD-3-Clause

__all__ = (
    "DetailedReportType",
    "FeatureType",
    "MappingFeatureType",
    "ReportType",
    "SegmentedFeatureType",
    "SetType",
)

import abc
from collections.abc import Collection
from dataclasses import dataclass
from typing import TYPE_CHECKING

from analytix.errors import InvalidRequest

if TYPE_CHECKING:
    from analytix.reports.features import Dimensions
    from analytix.reports.features import Filters
    from analytix.reports.features import Metrics
    from analytix.reports.features import SortOptions


@dataclass()
class ReportType(metaclass=abc.ABCMeta):
    __slots__ = ("dimensions", "filters", "metrics", "name", "sort_options")

    name: str
    dimensions: "Dimensions"
    filters: "Filters"
    metrics: "Metrics"
    sort_options: "SortOptions"

    def __str__(self) -> str:
        return self.name

    def validate(
        self,
        dimensions: Collection[str],
        filters: dict[str, str],
        metrics: Collection[str],
        sort_options: Collection[str],
        max_results: int = 0,
        start_index: int = 1,
    ) -> None:
        self.dimensions.validate(dimensions)
        self.filters.validate(filters)
        self.metrics.validate(metrics)
        self.sort_options.validate(sort_options)


@dataclass()
class DetailedReportType(ReportType, metaclass=abc.ABCMeta):
    __slots__ = ("max_results",)

    max_results: int

    def validate(
        self,
        dimensions: Collection[str],
        filters: dict[str, str],
        metrics: Collection[str],
        sort_options: Collection[str],
        max_results: int = 0,
        start_index: int = 1,
    ) -> None:
        super().validate(dimensions, filters, metrics, sort_options)

        if not max_results or max_results > self.max_results:
            if max_results == 0:
                raise InvalidRequest("expected a maximum number of results")
            raise InvalidRequest(
                f"expected no more than {self.max_results} results, got "
                f"{max_results:,}",
            )

        if self.max_results and start_index + max_results > self.max_results + 1:
            raise InvalidRequest("the start index is too high")

        if not sort_options:
            raise InvalidRequest("expected at least 1 sort option, got 0")


class FeatureType(metaclass=abc.ABCMeta):
    __slots__ = ("values",)

    def __init__(self, *args: str) -> None:
        self.values = set(args)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(values={self.values})"

    @abc.abstractmethod
    def validate(self, inputs: Collection[str]) -> None:
        raise NotImplementedError


class SegmentedFeatureType(metaclass=abc.ABCMeta):
    __slots__ = ("values",)

    def __init__(self, *args: "SetType") -> None:
        self.values = set(args)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(values={self.values})"

    @property
    def every(self) -> set[str]:
        every = set()

        for set_type in self.values:
            every |= set_type.values

        return every

    @abc.abstractmethod
    def validate(self, inputs: Collection[str]) -> None:
        raise NotImplementedError


class MappingFeatureType(metaclass=abc.ABCMeta):
    __slots__ = ("values",)

    def __init__(self, *args: "SetType") -> None:
        self.values = set(args)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(values={self.values})"

    @property
    def every(self) -> set[str]:
        every = set()

        for set_type in self.values:
            every |= set_type.values

        return every

    @abc.abstractmethod
    def validate(self, inputs: dict[str, str]) -> None:
        raise NotImplementedError


class SetType(metaclass=abc.ABCMeta):
    __slots__ = ("expd_keys", "values")

    def __init__(self, *args: str) -> None:
        self.values = set(args)
        self.expd_keys = {v[: v.index("=")] if "==" in v else v for v in self.values}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(values={self.values})"

    @abc.abstractmethod
    def validate_dimensions(self, inputs: set[str]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def validate_filters(self, keys: set[str]) -> None:
        raise NotImplementedError
