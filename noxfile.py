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

import re
import sys
from pathlib import Path

import nox

PROJECT_DIR = Path(__file__).parent
TEST_DIR = PROJECT_DIR / "tests"

PROJECT_NAME = Path(__file__).parent.stem

CHECK_PATHS = (
    str(PROJECT_DIR / PROJECT_NAME),
    str(TEST_DIR),
    str(PROJECT_DIR / "noxfile.py"),
    str(PROJECT_DIR / "setup.py"),
)

DEP_PATTERN = re.compile("([a-zA-Z0-9-_]*)[=~<>,.0-9ab]*")


def fetch_installs(*categories: str) -> list[str]:
    installs = []

    with open(PROJECT_DIR / "requirements/dev.txt") as f:
        in_cat = None

        for line in f:
            if line.startswith("#") and line[2:].strip() in categories:
                in_cat = True
                continue

            if in_cat:
                if line == "\n":
                    in_cat = False
                    continue

                installs.append(line.strip())

    return installs


@nox.session(reuse_venv=True)
def tests(session: nox.Session) -> None:
    session.install(*fetch_installs("Tests"), ".")
    session.run(
        "coverage",
        "run",
        "--omit",
        "tests/*",
        "-m",
        "pytest",
        "--log-level=1",
    )
    session.run("coverage", "report", "-m")


@nox.session(reuse_venv=True)
def check_formatting(session: nox.Session) -> None:
    session.install(*fetch_installs("Formatting"))
    session.run("black", ".", "--check")


@nox.session(reuse_venv=True)
def check_imports(session: nox.Session) -> None:
    session.install(*fetch_installs("Imports"))
    # flake8 doesn't use the gitignore so we have to be explicit.
    session.run(
        "flake8",
        *CHECK_PATHS,
        "--select",
        "F4",
        "--extend-ignore",
        "E,F,W",
        "--extend-exclude",
        "__init__.py",
    )
    session.run("isort", *CHECK_PATHS, "-cq")


@nox.session(reuse_venv=True)
def check_typing(session: nox.Session) -> None:
    session.install(
        *fetch_installs("Typing"),
        "-r",
        "requirements/types.txt",
    )
    session.run("mypy", CHECK_PATHS[0], CHECK_PATHS[3])


@nox.session(reuse_venv=True)
def check_line_lengths(session: nox.Session) -> None:
    check = [p for p in CHECK_PATHS if p != str(TEST_DIR)]

    session.install(*fetch_installs("Line lengths"))
    session.run("len8", *check)


@nox.session(reuse_venv=True)
def check_licensing(session: nox.Session) -> None:
    missing = []

    for p in [
        *(PROJECT_DIR / PROJECT_NAME).rglob("*.py"),
        *TEST_DIR.glob("*.py"),
        *PROJECT_DIR.glob("*.py"),
    ]:
        with open(p) as f:
            if not f.read().startswith("# Copyright (c) 2021-present, Ethan Henderson"):
                missing.append(p)

    if missing:
        session.error(
            f"\n{len(missing):,} file(s) are missing their licenses:\n"
            + "\n".join(f" - {file}" for file in missing)
        )


@nox.session(reuse_venv=True)
def check_spelling(session: nox.Session) -> None:
    session.install(*fetch_installs("Spelling"))
    session.run("codespell", *CHECK_PATHS, "-S", "**/analytix/data.py")


@nox.session(reuse_venv=True)
def check_safety(session: nox.Session) -> None:
    if sys.version_info >= (3, 11):
        session.skip("Safety does not support Python 3.11")

    with open(PROJECT_DIR / "requirements.txt") as f:
        installs = f.read().splitlines()

    for p in list(PROJECT_DIR.glob("requirements/*.txt")):
        installs.extend(["-r", f"{p}"])

    # Needed due to https://github.com/pypa/pip/pull/9827.
    session.install("pip")
    session.install(*installs)
    session.run("safety", "check", "--full-report")


@nox.session(reuse_venv=True)
def check_security(session: nox.Session) -> None:
    session.install(*fetch_installs("Security"))
    session.run("bandit", "-qr", *CHECK_PATHS, "-s", "B101")
