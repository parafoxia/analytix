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
    "Metrics",
    "SortOptions",
    "Dimensions",
    "Filters",
    "Required",
    "ExactlyOne",
    "OneOrMore",
    "Optional",
    "ZeroOrOne",
    "ZeroOrMore",
)

import typing as t

from analytix import abc
from analytix.errors import InvalidRequest
from analytix.reports import data


class _CompareMixin:
    values: set[str]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.values == other.values

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.values != other.values

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)


class _NestedCompareMixin:
    values: set[abc.SetType]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.values == other.values

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.values != other.values

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)


class Metrics(abc.FeatureType, _CompareMixin):
    def validate(self, inputs: t.Collection[str]) -> None:
        if not len(inputs):
            raise InvalidRequest("expected at least 1 metric, got 0")

        if not isinstance(inputs, set):
            inputs = set(inputs)

        diff = inputs - data.ALL_METRICS
        if diff:
            raise InvalidRequest.invalid("metric", diff)

        diff = inputs - self.values
        if diff:
            raise InvalidRequest.incompatible_metrics(diff)


class SortOptions(abc.FeatureType, _CompareMixin):
    def __init__(self, *args: str, descending_only: bool = False) -> None:
        super().__init__(*args)
        self.descending_only = descending_only

    def validate(self, inputs: t.Collection[str]) -> None:
        raw_inputs = set(i.strip("-") for i in inputs)
        if not isinstance(inputs, set):
            inputs = set(inputs)

        diff = raw_inputs - data.ALL_METRICS
        if diff:
            raise InvalidRequest.invalid("sort option", diff)

        diff = raw_inputs - self.values
        if diff:
            raise InvalidRequest.incompatible_sort_options(diff)

        if self.descending_only:
            diff = {i for i in inputs if not i.startswith("-")}
            if diff:
                raise InvalidRequest(
                    "dimensions and filters are incompatible with ascending sort "
                    "options (hint: prefix with '-')"
                )


class Dimensions(abc.SegmentedFeatureType, _NestedCompareMixin):
    def validate(self, inputs: t.Collection[str]) -> None:
        if not isinstance(inputs, set):
            inputs = set(inputs)

        diff = inputs - data.ALL_DIMENSIONS
        if diff:
            raise InvalidRequest.invalid("dimension", diff)

        if inputs - self.every:
            raise InvalidRequest.incompatible_dimensions(inputs)

        for set_type in self.values:
            set_type.validate_dimensions(inputs)


class Filters(abc.MappingFeatureType, _NestedCompareMixin):
    @property
    def every_key(self) -> set[str]:
        return {v[: v.index("=")] if "==" in v else v for v in self.every}

    @property
    def locked(self) -> dict[str, str]:
        locked = {}

        for set_type in self.values:
            for value in filter(lambda v: "==" in v, set_type.values):
                k, v = value.split("==")
                locked.update({k: v})

        return locked

    def validate(self, inputs: dict[str, str]) -> None:
        keys = set(inputs.keys())
        locked = self.locked

        diff = keys - data.ALL_FILTERS
        if diff:
            raise InvalidRequest.invalid("filter", diff)

        for k, v in inputs.items():
            valid = data.VALID_FILTER_OPTIONS[k]

            if valid and (v not in valid):
                raise InvalidRequest.invalid_filter_value(k, v)

            if k in locked.keys():
                if v != locked[k]:
                    raise InvalidRequest.incompatible_filter_value(k, v)

        if keys - self.every_key:
            raise InvalidRequest.incompatible_filters(keys)

        for set_type in self.values:
            set_type.validate_filters(keys)


class Required(abc.SetType, _CompareMixin):
    def validate_dimensions(self, inputs: set[str]) -> None:
        if self.values & inputs == self.values:
            return

        raise InvalidRequest.invalid_set(
            "dimension", self.values, "all", len(inputs & self.values)
        )

    def validate_filters(self, keys: set[str]) -> None:
        if self.expd_keys & keys == self.expd_keys:
            return

        raise InvalidRequest.invalid_set(
            "filter", self.values, "all", len(keys & self.values)
        )


class ExactlyOne(abc.SetType, _CompareMixin):
    def validate_dimensions(self, inputs: set[str]) -> None:
        if len(self.values & inputs) == 1:
            return

        raise InvalidRequest.invalid_set(
            "dimension", self.values, "1", len(inputs & self.values)
        )

    def validate_filters(self, keys: set[str]) -> None:
        if len(self.expd_keys & keys) == 1:
            return

        raise InvalidRequest.invalid_set(
            "filter", self.values, "1", len(keys & self.values)
        )


class OneOrMore(abc.SetType, _CompareMixin):
    def validate_dimensions(self, inputs: set[str]) -> None:
        if len(self.values & inputs) > 0:
            return

        raise InvalidRequest.invalid_set(
            "dimension", self.values, "at least 1", len(inputs & self.values)
        )

    def validate_filters(self, keys: set[str]) -> None:
        if len(self.expd_keys & keys) > 0:
            return

        raise InvalidRequest.invalid_set(
            "filter", self.values, "at least 1", len(keys & self.values)
        )


class Optional(abc.SetType, _CompareMixin):
    def validate_dimensions(self, _: set[str]) -> None:
        # No verifiction required.
        ...

    def validate_filters(self, _: set[str]) -> None:
        # No verifiction required.
        ...


class ZeroOrOne(abc.SetType, _CompareMixin):
    def validate_dimensions(self, inputs: set[str]) -> None:
        if len(self.values & inputs) < 2:
            return

        raise InvalidRequest.invalid_set(
            "dimension", self.values, "0 or 1", len(inputs & self.values)
        )

    def validate_filters(self, keys: set[str]) -> None:
        if len(self.expd_keys & keys) < 2:
            return

        raise InvalidRequest.invalid_set(
            "filter", self.values, "0 or 1", len(keys & self.values)
        )


class ZeroOrMore(abc.SetType, _CompareMixin):
    def validate_dimensions(self, _: set[str]) -> None:
        # No verifiction required.
        ...

    def validate_filters(self, _: set[str]) -> None:
        # No verifiction required.
        ...
