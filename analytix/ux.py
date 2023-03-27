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

"""User experience utilities for analytix."""

from __future__ import annotations

__all__ = ("display_splash", "enable_logging")

import json
import logging
import os
import platform
import sys
import typing as t
import warnings
from importlib.util import find_spec
from urllib import request

import analytix

BANNER = r"""
{r}            {o}             {y}            {g}88  {b}             {i}         {v}88
{r}            {o}             {y}            {g}88  {b}             {i}  ,d     {v}""
{r}            {o}             {y}            {g}88  {b}             {i}  88
{r},adPPYYba,  {o}8b,dPPYba,   {y},adPPYYba,  {g}88  {b}8b       d8  {i}MM88MMM  {v}88  {l}8b,     ,d8
{r}""     `Y8  {o}88P'   `"8a  {y}""     `Y8  {g}88  {b}`8b     d8'  {i}  88     {v}88  {l} `Y8, ,8P'
{r},adPPPPP88  {o}88       88  {y},adPPPPP88  {g}88  {b} `8b   d8'   {i}  88     {v}88  {l}   )888(
{r}88,    ,88  {o}88       88  {y}88,    ,88  {g}88  {b}  `8b,d8'    {i}  88,    {v}88  {l} ,d8" "8b,
{r}`"8bbdP"Y8  {o}88       88  {y}`"8bbdP"Y8  {g}88  {b}    Y88'     {i}  "Y888  {v}88  {l}8P'     `Y8
{r}            {o}             {y}            {g}    {b}    d8'
{r}            {o}             {y}            {g}    {b}   d8' {x}
""".format(  # noqa: E501
    r="\33[38;5;1m",
    o="\33[38;5;208m",
    y="\33[38;5;3m",
    g="\33[38;5;2m",
    b="\33[38;5;4m",
    i="\33[38;5;135m",
    v="\33[38;5;213m",
    l="\33[38;5;219m",
    x="\33[0m",
)


def _install_location() -> str:
    spec = find_spec("analytix")

    if spec and spec.submodule_search_locations:
        return spec.submodule_search_locations[0]

    return "unknown"


def display_splash() -> None:
    r = "\33[38;5;1m"
    o = "\33[38;5;208m"
    y = "\33[38;5;3m"
    g = "\33[38;5;2m"
    b = "\33[38;5;4m"
    l = "\33[38;5;219m"  # noqa: E741

    resp = request.urlopen(analytix.UPDATE_CHECK_URL)  # noqa: S310
    if resp.status == 200:
        data = json.loads(resp.read().decode("utf-8"))
        latest = data["info"]["version"]
        linfo = (
            f"{g}latest\33[0m"
            if latest == analytix.__version__
            else f"{y}latest is {latest}\33[0m"
        )
    else:
        linfo = f"{o}latest N/A\33[0m"

    print(  # noqa: T201
        BANNER + "\n"
        "\33[3mA simple yet powerful wrapper for the YouTube Analytics API.\33[0m\n\n"
        f"You're using version \33[1m{r}{analytix.__version__}\33[0m ({linfo}).\n\n"
        f"\33[1m{b}Information:\33[0m\n"
        f" • Python version: {platform.python_version()} "
        f"({platform.python_implementation()})\n"
        f" • Operating system: {platform.system()} ({platform.release()})\n"
        f" • Installed in: {_install_location()}\n\n"
        f"\33[1m{g}Useful links:\33[0m\n"
        f" • Documentation: \33[4m{analytix.__docs__}\33[0m\n"
        f" • Source: \33[4m{analytix.__url__}\33[0m\n"
        f" • Changelog: \33[4m{analytix.__changelog__}\33[0m\n\n"
        f"\33[1m{l}Thanks for using analytix!\33[0m"
    )


def enable_logging(level: int = logging.INFO) -> logging.StreamHandler[t.TextIO]:
    """Enable analytix's preconfigured logger.

    Parameters
    ----------
    level : int
        The log level to use.

    Returns
    -------
    StreamHandler object
        The created log handler.

    ??? example
        ```py
        analytix.enable_logging(logging.DEBUG)
        ```
    """

    fmt = "{relativeCreated:>7,.0f}ms [ {levelname:<7} ] {name}: {message}"
    formats = {
        logging.DEBUG: f"\33[38;5;244m{fmt}\33[0m",
        logging.INFO: f"\33[38;5;248m{fmt}\33[0m",
        logging.WARNING: f"\33[1m\33[38;5;178m{fmt}\33[0m",
        logging.ERROR: f"\33[1m\33[38;5;196m{fmt}\33[0m",
        logging.CRITICAL: f"\33[1m\33[48;5;196m{fmt}\33[0m",
    }

    class CustomFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_fmt = formats[record.levelno]
            formatter = logging.Formatter(log_fmt, style="{")
            return formatter.format(record)

    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    logging.basicConfig(level=level, handlers=[handler])
    logging._srcfile = None
    logging.logThreads = False
    logging.logProcesses = False
    logging.logMultiprocessing = False

    def showwarning(
        message: Warning | str,
        category: type[Warning],
        filename: str,
        lineno: int,
        file: t.TextIO | None = None,
        line: str | None = None,
    ) -> None:
        for _module_name, module in sys.modules.items():
            module_path = getattr(module, "__file__", None)
            if module_path and os.path.samefile(module_path, filename):
                break
        else:
            _module_name = os.path.splitext(os.path.split(filename)[1])[0]
        log = logging.getLogger(_module_name)
        log.warning(message)

    warnings.simplefilter("always", DeprecationWarning)
    warnings.showwarning = showwarning

    return handler
