# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

"""Warning classes for analytix."""


class AnalytixWarning(Warning):
    """The base warning class for analytix."""


class NotUpdatedWarning(AnalytixWarning):
    """Your client is not updated."""


class InvalidMonthFormatWarning(AnalytixWarning):
    """The months in your request had to be fixed."""


class CityReportWarning(AnalytixWarning):
    """The YouTube API docs are wrong (genuinely)."""
