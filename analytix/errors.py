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

"""Exception classes for analytix."""

from __future__ import annotations

__all__ = (
    "AnalytixError",
    "MissingOptionalComponents",
    "APIError",
    "AuthorisationError",
    "NotAuthorised",
    "RefreshTokenExpired",
    "DataFrameConversionError",
    "InvalidRequest",
    "InvalidFeatures",
    "InvalidFeatureSet",
)


class AnalytixError(Exception):
    """The base exception class for analytix."""


class MissingOptionalComponents(AnalytixError):
    """Exception thrown when components not installed by analytix by
    default are required for a specific operation, but are not
    installed.

    Parameters
    ----------
    *args : str
        The libraries that need to be installed.
    """

    def __init__(self, *args: str) -> None:
        vals = " ".join(args)
        super().__init__(
            f"some necessary libraries are not installed (hint: pip install {vals})"
        )


class APIError(AnalytixError):
    """Exception thrown when the YouTube Analytics API throws an
    error.

    Parameters
    ----------
    code : str or int
        The error code.
    message : str
        The error message.
    """

    def __init__(self, code: str | int, message: str) -> None:
        super().__init__(f"API returned {code}: {message}")


class AuthorisationError(AnalytixError):
    """Exception thrown when something goes wrong during the
    authorisation process."""


class NotAuthorised(AuthorisationError):
    """Exception thrown when the client does not have sufficient
    authorisation to complete the operation."""


class RefreshTokenExpired(AuthorisationError):
    """Exception thrown when refreshing an access token is not
    possible."""


class DataFrameConversionError(AnalytixError):
    """Exception thrown when converting a report to a DataFrame
    fails."""


class InvalidRequest(AnalytixError):
    """Exception thrown when a request to be made to the YouTube
    Analytics API is not valid."""

    @staticmethod
    def list_of(values: set[str]) -> str:
        items = tuple(f"{v!r}" for v in sorted(values))

        if len(items) > 2:
            return f"{', '.join(items[:-1])}, and {items[-1]}"

        return " and ".join(items)

    @classmethod
    def invalid(cls, key: str, values: set[str]) -> InvalidRequest:
        plural = "s" if len(values) > 1 else ""
        return cls(f"invalid {key}{plural} provided: " + cls.list_of(values))

    @classmethod
    def incompatible_dimensions(cls, values: set[str]) -> InvalidRequest:
        return cls(f"dimensions {cls.list_of(values)} cannot be used together")

    @classmethod
    def incompatible_filters(cls, values: set[str]) -> InvalidRequest:
        return cls(f"filters {cls.list_of(values)} cannot be used together")

    @classmethod
    def invalid_filter_value(cls, key: str, value: str) -> InvalidRequest:
        return cls(f"invalid value {value!r} for filter {key!r}")

    @classmethod
    def incompatible_filter_value(cls, key: str, value: str) -> InvalidRequest:
        return cls(
            f"value {value!r} for filter {key!r} cannot be used with the given "
            "dimensions"
        )

    @classmethod
    def incompatible_metrics(cls, values: set[str]) -> InvalidRequest:
        plural = "s" if len(values) > 1 else ""
        return cls(
            f"metric{plural} {cls.list_of(values)} cannot be used with the given "
            "dimensions and filters"
        )

    @classmethod
    def incompatible_sort_options(cls, values: set[str]) -> InvalidRequest:
        plural = "s" if len(values) > 1 else ""
        return cls(
            f"sort option{plural} {cls.list_of(values)} cannot be used with the given "
            "dimensions and filters"
        )

    @classmethod
    def non_matching_sort_options(cls, values: set[str]) -> InvalidRequest:
        plural = "s" if len(values) > 1 else ""
        isare = "are" if plural else "is"
        return cls(
            f"sort option{plural} {cls.list_of(values)} {isare} not part of the given "
            "metrics"
        )

    @classmethod
    def invalid_set(
        cls, key: str, values: set[str], expd: str, recv: int
    ) -> InvalidRequest:
        plural = "" if expd in ("1", "at least 1") else "s"
        return cls(
            f"expected {expd} {key}{plural} from {cls.list_of(values)}, got {recv}"
        )


class InvalidFeatures(InvalidRequest):
    ...


class InvalidFeatureSet(InvalidRequest):
    ...
