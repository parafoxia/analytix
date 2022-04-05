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

import sys
from collections import defaultdict

if sys.version_info < (3, 7, 0):
    print(
        "analytix only supports Python versions 3.7.0 or greater.",
        file=sys.stderr,
    )
    sys.exit(1)

import setuptools


def parse_requirements(path: str) -> list[str]:
    with open(path) as f:
        deps = (d.strip() for d in f.readlines())
        return [d for d in deps if not d.startswith(("#", "-e", "-r"))]


with open("./analytix/__init__.py") as f:
    attrs = defaultdict(str)

    for line in f:
        if not line.startswith("__"):
            continue

        k, v = line.split(" = ")
        if k == "__all__":
            continue

        attrs[k[2:-2]] = v.strip().replace('"', "")


with open("./README.md") as f:
    long_description = f.read()

setuptools.setup(
    name=attrs["productname"],
    version=attrs["version"],
    description=attrs["description"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=attrs["url"],
    author=attrs["author"],
    author_email=attrs["author_email"],
    license=attrs["license"],
    classifiers=[
        # "Development Status :: 1 - Planning",
        # "Development Status :: 2 - Pre-Alpha",
        # "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    project_urls={
        "Documentation": attrs["docs"],
        "Source": attrs["url"],
        "Bug Tracker": attrs["bugtracker"],
        "CI": attrs["ci"],
        "Changelog": attrs["changelog"],
    },
    install_requires=parse_requirements("./requirements/base.txt"),
    extras_require={
        "arrow": parse_requirements("./requirements/arrow.txt"),
        "dev": parse_requirements("./requirements/dev.txt"),
        "df": parse_requirements("./requirements/df.txt"),
        "excel": parse_requirements("./requirements/excel.txt"),
        "modin": parse_requirements("./requirements/modin.txt"),
        "pandas": parse_requirements("./requirements/df.txt"),
        "types": parse_requirements("./requirements/types.txt"),
    },
    python_requires=">=3.7.0,<3.12",
    packages=setuptools.find_packages(),
    package_data={"analytix": ["py.typed"]},
)
