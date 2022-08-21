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

"""A module containing analytix's exception classes."""

from __future__ import annotations


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


class AuthenticationError(AnalytixError):
    """Exception thrown when something goes wrong during the OAuth
    authentication process.

    Parameters
    ----------
    error : str
        The error type.
    error_description : str
        A description of the error.
    """

    def __init__(self, error: str, error_description: str) -> None:
        super().__init__(f"Authorisation error ({error}): {error_description}")


class DataFrameConversionError(AnalytixError):
    """Exception thrown when converting a report to a DataFrame
    fails."""


class InvalidRequest(AnalytixError):
    """Exception thrown when a request to be made to the YouTube
    Analytics API is not valid."""


class MissingMetrics(InvalidRequest):
    """Exception thrown when no metrics are provided."""

    def __init__(self) -> None:
        super().__init__("expected at least 1 metric, got 0")


class InvalidMetrics(InvalidRequest):
    """Exception thrown when one or more metrics are not valid.

    Parameters
    ----------
    diff : set of str
        The invalid metrics.
    """

    def __init__(self, diff: set[str]) -> None:
        vals = ", ".join(diff)
        super().__init__(f"invalid metric(s) provided: {vals}")


class UnsupportedMetrics(InvalidRequest):
    """Exception thrown when one or more metrics are valid, but not
    compatible with the report type that has been selected.

    Parameters
    ----------
    diff : set of str
        The unsupported metrics.
    """

    def __init__(self, diff: set[str]) -> None:
        vals = ", ".join(diff)
        super().__init__(f"unsupported metric(s) for selected report type: {vals}")


class MissingSortOptions(InvalidRequest):
    """Exception thrown when no sort options are provided when
    necessary."""

    def __init__(self) -> None:
        super().__init__("expected at least 1 sort option, got 0")


class InvalidSortOptions(InvalidRequest):
    """Exception thrown when one or more sort options are not valid.

    Parameters
    ----------
    diff : set of str
        The invalid sort options.
    """

    def __init__(self, diff: set[str]) -> None:
        vals = ", ".join(diff)
        super().__init__(f"invalid sort option(s) provided: {vals}")


class UnsupportedSortOptions(InvalidRequest):
    """Exception thrown when one or more sort options are valid, but not
    compatible with the report type that has been selected.

    Parameters
    ----------
    diff : set of str
        The unsupported sort options.
    descending_only : bool
        Whether only descending sort options were expected.
    """

    def __init__(self, diff: set[str], *, descending_only: bool = False) -> None:
        vals = ", ".join(diff)

        if descending_only:
            extra = (
                f" -- only descending options are supported (hint: '-{tuple(diff)[0]}')"
            )
        else:
            extra = ""

        super().__init__(
            f"unsupported sort option(s) for selected report type: {vals}{extra}"
        )


class InvalidDimensions(InvalidRequest):
    """Exception thrown when one or more dimensions are not valid.
    Inherits from :obj:`InvalidRequest`.

    Parameters
    ----------
    diff : set of str
        The invalid dimensions.
    depr : set of str
        Dimensions that are deprecated (this will only ever be
        "7DayTotals" and "30DayTotals").
    """

    def __init__(self, diff: set[str], depr: set[str]) -> None:
        vals = ", ".join([*diff - depr, *(f"{d}*" for d in depr)])
        extra = " (*deprecated)" if depr else ""
        super().__init__(f"invalid dimension(s) provided: {vals}{extra}")


class UnsupportedDimensions(InvalidRequest):
    """Exception thrown when one or more dimensions are valid, but not
    compatible with the report type that has been selected.

    Parameters
    ----------
    diff : set of str
        The unsupported dimensions.
    """

    def __init__(self, diff: set[str]) -> None:
        vals = ", ".join(diff)
        super().__init__(f"unsupported dimension(s) for selected report type: {vals}")


class InvalidSetOfDimensions(InvalidRequest):
    """Exception thrown when a set of dimensions contravenes the API
    specification.

    Parameters
    ----------
    expd : str
        The number of dimensions expected from the given set.
    recv : int
        The number of dimensions received from the given set.
    values : set of str
        The full set of possible dimensions in this context.
    """

    def __init__(self, expd: str, recv: int, values: set[str]) -> None:
        vals = ", ".join(values)
        super().__init__(f"expected {expd} dimension(s) from {vals!r}, got {recv}")


class InvalidFilters(InvalidRequest):
    """Exception thrown when one or more filters are not valid.

    Parameters
    ----------
    diff : set of str
        The invalid filters.
    """

    def __init__(self, diff: set[str]) -> None:
        vals = ", ".join(diff)
        super().__init__(f"invalid filter(s) provided: {vals}")


class UnsupportedFilters(InvalidRequest):
    """Exception thrown when one or more filters are valid, but not
    compatible with the report type that has been selected.

    Parameters
    ----------
    diff : set of str
        The unsupported filters.
    """

    def __init__(self, diff: set[str]) -> None:
        vals = ", ".join(diff)
        super().__init__(f"unsupported filter(s) for selected report type: {vals}")


class InvalidSetOfFilters(InvalidRequest):
    """Exception thrown when a set of filters contravenes the API
    specification.

    Parameters
    ----------
    expd : str
        The number of filters expected from the given set.
    recv : int
        The number of filters received from the given set.
    values : set of str
        The full set of possible filters in this context.
    """

    def __init__(self, expd: str, recv: int, values: set[str]) -> None:
        vals = ", ".join(values)
        super().__init__(f"expected {expd} filter(s) from {vals!r}, got {recv}")


class InvalidFilterValue(InvalidRequest):
    """Exception thrown when an invalid value is provided for a filter.

    Parameters
    ----------
    key : str
        The filter key.
    value : str
        The invalid filter value.
    """

    def __init__(self, key: str, value: str) -> None:
        super().__init__(f"invalid value for filter {key!r}: {value!r}")


class UnsupportedFilterValue(InvalidRequest):
    """Exception thrown when a valid value is provided for a filter, but
    cannot be used for the report type that has been selected.

    Parameters
    ----------
    key : str
        The filter key.
    value : str
        The unsupported filter value.
    """

    def __init__(self, key: str, value: str) -> None:
        super().__init__(
            f"unsupported value for filter {key!r} for selected report type: {value!r}"
        )


class InvalidAmountOfResults(InvalidRequest):
    """Exception thrown when the provided maximum number of results is
    not valid.

    Parameters
    ----------
    actual : int
        The input value from the user.
    maximum : int
        The maximum allowed value.
    """

    def __init__(self, actual: int, maximum: int) -> None:
        if actual == 0:
            msg = "expected a maximum number of results"
        else:
            msg = f"expected no more than {maximum} results, got {actual:,}"

        super().__init__(msg)
