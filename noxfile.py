# Copyright (c) 2021, Ethan Henderson
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

import os
from pathlib import Path

import nox

PROJECT_NAME = "analytix"
LIB_DIR = Path(__file__).parent / PROJECT_NAME
TEST_DIR = Path(__file__).parent / "tests"


def parse_requirements(path):
    with open(path, mode="r", encoding="utf-8") as f:
        deps = (d.strip() for d in f.readlines())
        return [d for d in deps if not d.startswith(("#", "-r"))]


DEPS = {
    dep.split("~=")[0]: dep
    for dep in [
        *parse_requirements("./requirements-dev.txt"),
        *parse_requirements("./requirements-nox.txt"),
    ]
}


@nox.session(reuse_venv=True)
def tests(session):
    session.install("-U", *parse_requirements("./requirements-nox.txt"))
    session.run(
        "coverage",
        "run",
        "--omit",
        "tests/*",
        "-m",
        "pytest",
        "-s",
        "--testdox",
        "--log-level=INFO",
    )


@nox.session(reuse_venv=True)
def check_coverage(session):
    session.install("-U", DEPS["coverage"])

    if not os.path.isfile(Path(__file__).parent / ".coverage"):
        session.skip("No coverage to check")

    session.run("coverage", "report", "-m")


@nox.session(reuse_venv=True)
def check_docs_build(session):
    session.install("-U", DEPS["sphinx"], DEPS["furo"], ".")
    session.cd("./docs")
    session.run("make", "html")


@nox.session(reuse_venv=True)
def check_formatting(session):
    session.install("-U", DEPS["black"])
    session.run("black", ".", "--check")


@nox.session(reuse_venv=True)
def check_imports(session):
    session.install("-U", DEPS["flake8"], DEPS["isort"])
    # flake8 doesn't use the gitignore so we have to be explicit.
    session.run(
        "flake8",
        PROJECT_NAME,
        "tests",
        "--select",
        "F4",
        "--extend-ignore",
        "E,F,W",
        "--extend-exclude",
        "__init__.py",
    )
    session.run("isort", ".", "-cq", "--profile", "black")


@nox.session(reuse_venv=True)
def check_line_lengths(session):
    session.install("-U", DEPS["len8"])
    session.run("len8", PROJECT_NAME, "tests")


@nox.session(reuse_venv=True)
def check_licensing(session):
    missing = []

    for p in [
        *LIB_DIR.rglob("*.py"),
        *TEST_DIR.glob("*.py"),
        Path(__file__),
        Path(__file__).parent / "setup.py",
    ]:
        with open(p) as f:
            if not f.read().startswith("# Copyright (c)"):
                missing.append(p)

    if missing:
        session.error(
            f"\n{len(missing):,} file(s) are missing their licenses:\n"
            + "\n".join(f" - {file}" for file in missing)
        )
