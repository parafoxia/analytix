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


class InvalidFeatures(InvalidRequest):
    """A helper exception class for `InvalidRequest`. When catching
    exceptions, use `InvalidRequest` instead."""

    def __init__(self, ctx: str, errors: set[str]) -> None:
        err_list = ", ".join(errors)
        super().__init__(f"{ctx}: {err_list}")


class InvalidFeatureSet(InvalidRequest):
    """A helper exception class for `InvalidRequest`. When catching
    exceptions, use `InvalidRequest` instead."""

    def __init__(self, type: str, expd: str, recv: int, values: set[str]) -> None:
        val_list = ", ".join(values)
        super().__init__(f"expected {expd} {type}(s) from [ {val_list} ], got {recv}")
