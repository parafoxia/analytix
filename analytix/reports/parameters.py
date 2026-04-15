# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

import abc
from collections.abc import Collection
from typing import Any
from typing import overload

from analytix.errors import ParameterError
from analytix.errors import ValidationError
from analytix.reports.constants import VALID_FILTER_OPTIONS

from .constraints import Constraint
from .constraints import ConstraintTarget


class Parameter(abc.ABC):
    def __init__(self, *constraints: Constraint) -> None:
        self.constraints = constraints

    @property
    def all_fields(self) -> set[str]:
        return {field for constraint in self.constraints for field in constraint.fields}

    @property
    def all_keys(self) -> set[str]:
        return {key for constraint in self.constraints for key in constraint.keys}

    @overload
    def validate(self, inputs: Collection[str]) -> list[ValidationError]: ...

    @overload
    def validate(self, inputs: dict[str, str]) -> list[ValidationError]: ...

    @abc.abstractmethod
    def validate(
        self,
        inputs: Collection[str] | dict[str, str],
        **kwargs: Any,
    ) -> list[ValidationError]:
        raise NotImplementedError


class Dimensions(Parameter):
    def validate(self, inputs: Collection[str]) -> list[ValidationError]:
        errors = []
        inputs = set(inputs)

        if diff := inputs - self.all_keys:
            errors.append(
                ParameterError.format(
                    "unsupported dimensions: {diff}",
                    diff=diff,
                ),
            )

        for constraint in self.constraints:
            errors.extend(constraint.validate(inputs, ConstraintTarget.DIMENSIONS))

        return errors


class Filters(Parameter):
    def _locked_filters(self) -> dict[str, str]:
        locked = {}

        for constraint in self.constraints:
            for value in filter(lambda v: "==" in v, constraint.fields):
                k, v = value.split("==")
                locked[k] = v

        return locked

    def validate(self, inputs: dict[str, str]) -> list[ValidationError]:
        errors = []
        locked = self._locked_filters()
        input_keys = set(inputs.keys())

        if diff := input_keys - self.all_keys:
            errors.append(
                ParameterError.format(
                    "unsupported filters: {diff}",
                    diff=diff,
                ),
            )

        for constraint in self.constraints:
            errors.extend(constraint.validate(input_keys, ConstraintTarget.FILTERS))

        for k, v in inputs.items():
            valid = VALID_FILTER_OPTIONS.get(k)

            if valid and (v not in valid):
                errors.append(
                    ParameterError.format(
                        "invalid value for filter '{k}': {v}",
                        k=k,
                        v=v,
                    ),
                )

            if k in locked and v != locked[k]:
                errors.append(
                    ParameterError.format(
                        "expected filter '{k}' to be '{expected}', got '{actual}'",
                        k=k,
                        expected=locked[k],
                        actual=v,
                    ),
                )

        return errors


class Metrics(Parameter):
    def validate(self, inputs: Collection[str]) -> list[ValidationError]:
        errors = []
        inputs = set(inputs)

        if diff := inputs - self.all_keys:
            errors.append(
                ParameterError.format(
                    "unsupported metrics: {diff}",
                    diff=diff,
                ),
            )

        return errors


class SortOptions(Parameter):
    def __init__(
        self,
        *constraints: Constraint,
        descending_only: bool = False,
    ) -> None:
        super().__init__(*constraints)
        self.descending_only = descending_only

    def validate(self, inputs: Collection[str]) -> list[ValidationError]:
        errors = []
        inputs = set(inputs)

        if diff := inputs - {k.lstrip("-") for k in self.all_keys}:
            errors.append(
                ParameterError.format(
                    "unsupported sort options: {diff}",
                    diff=diff,
                ),
            )

        for constraint in self.constraints:
            errors.extend(constraint.validate(inputs, ConstraintTarget.SORT_OPTIONS))

        return errors
