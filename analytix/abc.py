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

__all__ = (
    "ReportType",
    "DetailedReportType",
    "FeatureType",
    "SegmentedFeatureType",
    "MappingFeatureType",
    "SetType",
)

import abc
import typing as t
from dataclasses import dataclass

from analytix.errors import InvalidRequest

if t.TYPE_CHECKING:
    from analytix.reports.features import Dimensions, Filters, Metrics, SortOptions


@dataclass()
class ReportType(metaclass=abc.ABCMeta):
    __slots__ = ("name", "dimensions", "filters", "metrics", "sort_options")

    name: str
    dimensions: Dimensions
    filters: Filters
    metrics: Metrics
    sort_options: SortOptions

    def __str__(self) -> str:
        return self.name

    def validate(
        self,
        dimensions: t.Collection[str],
        filters: dict[str, str],
        metrics: t.Collection[str],
        sort_options: t.Collection[str],
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
        dimensions: t.Collection[str],
        filters: dict[str, str],
        metrics: t.Collection[str],
        sort_options: t.Collection[str],
        max_results: int = 0,
        start_index: int = 1,
    ) -> None:
        super().validate(dimensions, filters, metrics, sort_options)

        if not max_results or max_results > self.max_results:
            if max_results == 0:
                raise InvalidRequest("expected a maximum number of results")
            raise InvalidRequest(
                f"expected no more than {self.max_results} results, got {max_results:,}"
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
    def validate(self, inputs: t.Collection[str]) -> None:
        raise NotImplementedError


class SegmentedFeatureType(metaclass=abc.ABCMeta):
    __slots__ = ("values",)

    def __init__(self, *args: SetType) -> None:
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
    def validate(self, inputs: t.Collection[str]) -> None:
        raise NotImplementedError


class MappingFeatureType(metaclass=abc.ABCMeta):
    __slots__ = ("values",)

    def __init__(self, *args: SetType) -> None:
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
    __slots__ = ("values", "expd_keys")

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
