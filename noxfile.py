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

from functools import wraps
from pathlib import Path
from typing import Callable, List, Optional

import nox

REPO_DIR = Path(__file__).parent
PROJECT_NAME = REPO_DIR.stem
PROJECT_DIR = REPO_DIR / PROJECT_NAME
TEST_DIR = REPO_DIR / "tests"
EXAMPLES_DIR = REPO_DIR / "examples"
NOX_FILE = REPO_DIR / "noxfile.py"
SETUP_FILE = REPO_DIR / "setup.py"
REQUIREMENTS_FILE = REPO_DIR / "requirements/nox.txt"

SessFT = Callable[[nox.Session], None]


def install(
    *,
    meta: bool = False,
    rfiles: Optional[List[str]] = None,
    libs: Optional[List[str]] = None,
) -> Callable[[SessFT], SessFT]:
    def decorator(func: SessFT) -> SessFT:
        @wraps(func)
        def wrapper(session: nox.Session) -> None:
            deps: list[str] = []
            processing = False

            with open(REQUIREMENTS_FILE) as f:
                for line in f:
                    if line.startswith("#") and line[2:].strip() == func.__name__:
                        processing = True
                        continue

                    if processing:
                        if line == "\n":
                            processing = False
                            break

                        deps.append(line.strip())

            args = ["-U", *deps]
            if meta:
                args.append(".")
            for x in rfiles or []:
                args.extend(["-r", f"requirements/{x}.txt"])
            if libs:
                args.extend(libs)

            session.install(*args)
            func(session)

        return wrapper

    return decorator


def sp(*paths: Path) -> List[str]:
    return [str(p) for p in paths]


@nox.session(reuse_venv=True)
@install(meta=True)
def tests(session: nox.Session) -> None:
    session.run(
        "coverage",
        "run",
        "--source",
        PROJECT_NAME,
        "--omit",
        "tests/*",
        "-m",
        "pytest",
        "--log-level=1",
    )
    session.run("coverage", "report", "-m")


@nox.session(reuse_venv=True)
@install()
def dependencies(session: nox.Session) -> None:
    session.run("deputil", "update", "requirements")


@nox.session(reuse_venv=True)
@install()
def formatting(session: nox.Session) -> None:
    session.run(
        "black",
        "--check",
        *sp(PROJECT_DIR, TEST_DIR, EXAMPLES_DIR, NOX_FILE, SETUP_FILE),
    )


@nox.session(reuse_venv=True)
def licensing(session: nox.Session) -> None:
    expd = "# Copyright (c) 2021-present, Ethan Henderson"
    errors = []

    for path in (
        *PROJECT_DIR.rglob("*.py"),
        *TEST_DIR.rglob("*.py"),
        NOX_FILE,
        SETUP_FILE,
    ):
        with open(path) as f:
            if not f.read().startswith(expd):
                errors.append(path)

    if errors:
        session.error(
            f"\n{len(errors):,} file(s) are missing their licenses:\n"
            + "\n".join(f" - {file}" for file in errors)
        )


@nox.session(reuse_venv=True)
@install()
def linting(session: nox.Session) -> None:
    # TODO: Add examples directory once errors are fixed and add linter-
    # specific error code excludes.
    session.run("ruff", "check", *sp(PROJECT_DIR, NOX_FILE))


@nox.session(reuse_venv=True)
@install(rfiles=["dev"])
def safety(session: nox.Session) -> None:
    session.run("mypy", "--install-types", "--non-interactive")
    session.run("safety", "check", "--full-report")


@nox.session(reuse_venv=True)
@install(meta=True)
def slots(session: nox.Session) -> None:
    session.run("slotscheck", "-m", "analytix")


@nox.session(reuse_venv=True)
@install()
def spelling(session: nox.Session) -> None:
    session.run(
        "codespell",
        *sp(PROJECT_DIR, TEST_DIR, EXAMPLES_DIR, NOX_FILE, SETUP_FILE),
        "-S",
        "**/analytix/reports/data*",
    )


@nox.session(reuse_venv=True)
@install(rfiles=["base"])
def typing(session: nox.Session) -> None:
    session.run(
        "mypy",
        "--install-types",
        "--non-interactive",
        *sp(PROJECT_DIR, EXAMPLES_DIR, SETUP_FILE),
    )
