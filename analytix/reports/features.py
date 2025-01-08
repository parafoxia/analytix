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

__all__ = (
    "Dimensions",
    "ExactlyOne",
    "Filters",
    "Metrics",
    "OneOrMore",
    "Optional",
    "Required",
    "SortOptions",
    "ZeroOrMore",
    "ZeroOrOne",
)

from typing import Collection
from typing import Dict
from typing import Set

from analytix import abc
from analytix.errors import InvalidRequest
from analytix.reports import data


class _CompareMixin:
    values: Set[str]

    def __eq__(self, other: object) -> bool:
        # sourcery skip: assign-if-exp, reintroduce-else, swap-if-expression
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.values == other.values

    def __ne__(self, other: object) -> bool:
        # sourcery skip: assign-if-exp, reintroduce-else, swap-if-expression
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.values != other.values

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)


class _NestedCompareMixin:
    values: Set[abc.SetType]

    def __eq__(self, other: object) -> bool:
        # sourcery skip: assign-if-exp, reintroduce-else, swap-if-expression
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.values == other.values

    def __ne__(self, other: object) -> bool:
        # sourcery skip: assign-if-exp, reintroduce-else, swap-if-expression
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.values != other.values

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)


class Metrics(abc.FeatureType, _CompareMixin):
    def validate(self, inputs: Collection[str]) -> None:
        if not len(inputs):
            raise InvalidRequest("expected at least 1 metric, got 0")

        if not isinstance(inputs, set):
            inputs = set(inputs)

        if diff := inputs - data.ALL_METRICS:
            raise InvalidRequest.invalid("metric", diff)

        if diff := inputs - self.values:
            raise InvalidRequest.incompatible_metrics(diff)


class SortOptions(abc.FeatureType, _CompareMixin):
    def __init__(self, *args: str, descending_only: bool = False) -> None:
        super().__init__(*args)
        self.descending_only = descending_only

    def validate(self, inputs: Collection[str]) -> None:
        raw_inputs = {i.strip("-") for i in inputs}
        if not isinstance(inputs, set):
            inputs = set(inputs)

        if diff := raw_inputs - data.ALL_METRICS:
            raise InvalidRequest.invalid("sort option", diff)

        if diff := raw_inputs - self.values:
            raise InvalidRequest.incompatible_sort_options(diff)

        if self.descending_only and {i for i in inputs if not i.startswith("-")}:
            raise InvalidRequest(
                "dimensions and filters are incompatible with ascending sort "
                "options (hint: prefix with '-')",
            )


class Dimensions(abc.SegmentedFeatureType, _NestedCompareMixin):
    def validate(self, inputs: Collection[str]) -> None:
        if not isinstance(inputs, set):
            inputs = set(inputs)

        if diff := inputs - data.ALL_DIMENSIONS:
            raise InvalidRequest.invalid("dimension", diff)

        if inputs - self.every:
            raise InvalidRequest.incompatible_dimensions(inputs)

        for set_type in self.values:
            set_type.validate_dimensions(inputs)


class Filters(abc.MappingFeatureType, _NestedCompareMixin):
    @property
    def every_key(self) -> Set[str]:
        return {v[: v.index("=")] if "==" in v else v for v in self.every}

    @property
    def locked(self) -> Dict[str, str]:
        locked = {}

        for set_type in self.values:
            for value in filter(lambda v: "==" in v, set_type.values):
                k, v = value.split("==")
                locked[k] = v

        return locked

    def validate(self, inputs: Dict[str, str]) -> None:
        keys = set(inputs.keys())
        locked = self.locked

        if diff := keys - data.ALL_FILTERS:
            raise InvalidRequest.invalid("filter", diff)

        for k, v in inputs.items():
            valid = data.VALID_FILTER_OPTIONS[k]

            if valid and (v not in valid):
                raise InvalidRequest.invalid_filter_value(k, v)

            if k in locked and v != locked[k]:
                raise InvalidRequest.incompatible_filter_value(k, v)

        if keys - self.every_key:
            raise InvalidRequest.incompatible_filters(keys)

        for set_type in self.values:
            set_type.validate_filters(keys)


class Required(abc.SetType, _CompareMixin):
    def validate_dimensions(self, inputs: Set[str]) -> None:
        if self.values & inputs == self.values:
            return

        raise InvalidRequest.invalid_set(
            "dimension",
            self.values,
            "all",
            len(inputs & self.values),
        )

    def validate_filters(self, keys: Set[str]) -> None:
        if self.expd_keys & keys == self.expd_keys:
            return

        raise InvalidRequest.invalid_set(
            "filter",
            self.values,
            "all",
            len(keys & self.values),
        )


class ExactlyOne(abc.SetType, _CompareMixin):
    def validate_dimensions(self, inputs: Set[str]) -> None:
        if len(self.values & inputs) == 1:
            return

        raise InvalidRequest.invalid_set(
            "dimension",
            self.values,
            "1",
            len(inputs & self.values),
        )

    def validate_filters(self, keys: Set[str]) -> None:
        if len(self.expd_keys & keys) == 1:
            return

        raise InvalidRequest.invalid_set(
            "filter",
            self.values,
            "1",
            len(keys & self.values),
        )


class OneOrMore(abc.SetType, _CompareMixin):
    def validate_dimensions(self, inputs: Set[str]) -> None:
        if len(self.values & inputs) > 0:
            return

        raise InvalidRequest.invalid_set(
            "dimension",
            self.values,
            "at least 1",
            len(inputs & self.values),
        )

    def validate_filters(self, keys: Set[str]) -> None:
        if len(self.expd_keys & keys) > 0:
            return

        raise InvalidRequest.invalid_set(
            "filter",
            self.values,
            "at least 1",
            len(keys & self.values),
        )


class Optional(abc.SetType, _CompareMixin):
    def validate_dimensions(self, _: Set[str]) -> None:
        # No verifiction required.
        ...

    def validate_filters(self, _: Set[str]) -> None:
        # No verifiction required.
        ...


class ZeroOrOne(abc.SetType, _CompareMixin):
    def validate_dimensions(self, inputs: Set[str]) -> None:
        if len(self.values & inputs) < 2:
            return

        raise InvalidRequest.invalid_set(
            "dimension",
            self.values,
            "0 or 1",
            len(inputs & self.values),
        )

    def validate_filters(self, keys: Set[str]) -> None:
        if len(self.expd_keys & keys) < 2:
            return

        raise InvalidRequest.invalid_set(
            "filter",
            self.values,
            "0 or 1",
            len(keys & self.values),
        )


class ZeroOrMore(abc.SetType, _CompareMixin):
    def validate_dimensions(self, _: Set[str]) -> None:
        # No verifiction required.
        ...

    def validate_filters(self, _: Set[str]) -> None:
        # No verifiction required.
        ...
