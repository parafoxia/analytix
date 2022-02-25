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


class AnalytixError(Exception):
    ...


class NotAvailable(AnalytixError):
    ...


class InvalidRequest(AnalytixError):
    ...


class MissingMetrics(InvalidRequest):
    def __init__(sel) -> None:
        super().__init__("expected at least 1 metric, got 0")


class MissingSortOptions(InvalidRequest):
    def __init__(self) -> None:
        super().__init__("expected at least 1 sort option, got 0")


class InvalidMetrics(InvalidRequest):
    def __init__(self, diff: set[str]) -> None:
        vals = ", ".join(diff)
        super().__init__(f"invalid metric(s) provided: {vals}")


class UnsupportedMetrics(InvalidRequest):
    def __init__(self, diff: set[str]) -> None:
        vals = ", ".join(diff)
        super().__init__(f"unsupported metric(s) for selected report type: {vals}")


class InvalidSortOptions(InvalidRequest):
    def __init__(self, diff: set[str]) -> None:
        vals = ", ".join(diff)
        super().__init__(f"invalid sort option(s) provided: {vals}")


class UnsupportedSortOptions(InvalidRequest):
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
    def __init__(self, diff: set[str]) -> None:
        vals = ", ".join(diff)
        super().__init__(f"invalid dimension(s) provided: {vals}")


class UnsupportedDimensions(InvalidRequest):
    def __init__(self, diff: set[str]) -> None:
        vals = ", ".join(diff)
        super().__init__(f"unsupported dimension(s) for selected report type: {vals}")


class InvalidSetOfDimensions(InvalidRequest):
    def __init__(self, expd: str, recv: int, values: set[str]) -> None:
        vals = ", ".join(values)
        super().__init__(f"expected {expd} dimension(s) from {vals}, got {recv}")


class InvalidFilters(InvalidRequest):
    def __init__(self, diff: set[str]) -> None:
        vals = ", ".join(diff)
        super().__init__(f"invalid filter(s) provided: {vals}")


class UnsupportedFilters(InvalidRequest):
    def __init__(self, diff: set[str]) -> None:
        vals = ", ".join(diff)
        super().__init__(f"unsupported filter(s) for selected report type: {vals}")


class InvalidSetOfFilters(InvalidRequest):
    def __init__(self, expd: str, recv: int, values: set[str]) -> None:
        vals = ", ".join(values)
        super().__init__(f"expected {expd} filter(s) from {vals}, got {recv}")


class InvalidFilterValue(InvalidRequest):
    def __init__(self, key: str, value: str) -> None:
        super().__init__(f"invalid value for filter {key!r}: {value!r}")


class UnsupportedFilterValue(InvalidRequest):
    def __init__(self, key: str, value: str) -> None:
        super().__init__(
            f"unsupported value for filter {key!r} for selected report type: {value!r}"
        )


class InvalidAmountOfResults(InvalidRequest):
    def __init__(self, actual: int, maximum: int) -> None:
        if actual == 0:
            msg = "expected a maximum number of results"
        else:
            msg = f"expected no more than {maximum} results, got {actual:,}"

        super().__init__(msg)
