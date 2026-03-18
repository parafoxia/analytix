# SPDX-FileCopyrightText: 2021-2026 Ethan Henderson
# SPDX-License-Identifier: BSD-3-Clause

__all__ = ("can_use", "process_path")

from importlib import metadata
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from analytix.types import PathLike


def can_use(*packages: str) -> bool:
    try:
        for package in packages:
            metadata.distribution(package)
    except metadata.PackageNotFoundError:
        return False
    return True


def process_path(path: "PathLike", extension: str, *, overwrite: bool) -> Path:
    if not isinstance(path, Path):
        path = Path(path)

    if path.suffix != extension:
        path = Path(path.name + extension)

    if not overwrite and path.is_file():
        raise FileExistsError("file already exists and `overwrite` is set to False")

    return path
