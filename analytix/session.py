# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

__all__ = ("Session",)

from dataclasses import dataclass

from analytix.auth.scopes import Scopes


@dataclass(frozen=True)
class Session:
    key: str
    access_token: str
    scopes: Scopes
