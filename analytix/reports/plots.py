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

"""Plotting inferfaces for analytix."""

from __future__ import annotations

import abc
import datetime as dt
import logging
import math
import typing as t
from functools import cache

import matplotlib.pyplot as plt
import numpy as np

from analytix.errors import PlottingError
from analytix.utils import process_path

if t.TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from analytix.reports.interfaces import ResultTable
    from analytix.types import PathLikeT

_log = logging.getLogger(__name__)


class Plot(metaclass=abc.ABCMeta):
    """An abstract base class for all plot types.

    You should never instantiate this class manually.

    *New in version 4.2.0.*

    Parameters
    ----------
    resource : ResultTable
        The resource to extract the data from.
    title : str
        The title which will be displayed at the top of the plot.
    metrics : t.Collection[str]
        The metrics to plot.
    size : tuple[int, int] | None
        The width and height of the report in inches.

    Attributes
    ----------
    data : dict[str, tuple[int | float, ...]]
        The processed data ready to plot.
    title : str
        The title which will be displayed at the top of the plot.
    metrics : t.Collection[str]
        The metrics to plot.
    size : tuple[int, int] | None
        The width and height of the report in inches.
    figure : Figure object
        The created Matplotlib figure.
    """

    __slots__ = ("data", "title", "metrics", "size", "figure")

    def __init__(
        self,
        resource: ResultTable,
        title: str,
        metrics: t.Collection[str],
        size: tuple[int, int] | None,
    ) -> None:
        self.data = {
            resource.column_headers[i].name: column
            for i, column in enumerate(zip(*resource.rows))
        }
        self.title = title
        self.metrics = metrics
        self.size = size
        self.figure = self.plot()

    @property
    @cache
    def subplots(self) -> tuple[int, int]:
        """The number of rows and columns to use for a given number of
        plots.

        This tends to skew toward squareness over utilisation, meaning,
        for example, if there are 7 metrics to plot, it will select 3x3
        over 4x2.

        *New in version 4.2.0.*

        Returns
        -------
        tuple[int, int]
            The number of rows and columns to use.
        """

        x = len(self.metrics)
        columns = math.ceil(x**0.5)
        return math.ceil(x / columns), columns

    @property
    def dimension(self) -> str:
        """The dimension for the plot.

        *New in version 4.2.0.*

        Returns
        -------
        str
            The dimension for the plot.
        """

        return tuple(self.data.keys())[0]

    def _build_subplots(self) -> tuple[Figure, list[Axes]]:
        fig, axs = plt.subplots(
            *self.subplots, squeeze=False, sharex=True, figsize=self.size
        )
        return fig, [ax for nest in axs for ax in nest]

    @abc.abstractmethod
    def plot(self) -> Figure:
        """Plot the report.

        This method needs to be reimplemented in every child class.

        *New in version 4.2.0.*

        Returns
        -------
        Figure
            The created Matplotlib figure.
        """

        raise NotImplementedError

    def show(self) -> None:
        """Show the plot.

        *New in version 4.2.0.*

        Returns
        -------
        None
        """

        plt.show()

    def save(self, path: PathLikeT, *, overwrite: bool = True) -> None:
        """Save the plot to disk.

        *New in version 4.2.0.*

        Parameters
        ----------
        path : Path object or str
            The path to save the plot to.
        overwrite : bool, optional
            Whether to overwrite an existing file.

        Returns
        -------
        None
        """

        path = process_path(path, "", overwrite)
        self.figure.savefig(path)
        _log.info(f"Saved plot to {path.resolve()}")


class LinearPlot(Plot):
    """A representation of a linear analytics report plot.

    This will be plotted as a line graph.

    *New in version 4.2.0.*
    """

    @property
    @cache
    def _x_axis(self) -> list[t.Any]:
        return list(self.data[self.dimension])

    def plot(self) -> Figure:
        fig, axs = self._build_subplots()
        _log.debug(f"Created figure with {len(axs)} axes")

        for i, metric in enumerate(self.metrics):
            _log.debug(f"Plotting subplot for {metric!r}")

            axs[i].plot(self._x_axis, self.data[metric])
            axs[i].set_xlabel(self.dimension)
            axs[i].set_ylabel(metric)

        fig.suptitle(self.title)
        fig.autofmt_xdate(rotation=45)
        fig.tight_layout()
        return fig


class TimeSeriesPlot(LinearPlot):
    """A representation of a time-series analytics report plot.

    This will be plotted as a line graph.

    *New in version 4.2.0.*
    """

    @property
    @cache
    def _x_axis(self) -> list[t.Any]:
        return [
            dt.datetime.strptime(x, "%Y-%m-%d" if self.dimension == "day" else "%Y-%m")
            for x in self.data[self.dimension]
        ]


class CategoricalPlot(Plot):
    """A representation of a categorical analytics report plot.

    This will be plotted as a pie chart.

    *New in version 4.2.0.*
    """

    def plot(self) -> Figure:
        fig, axs = self._build_subplots()
        _log.debug(f"Created figure with {len(axs)} axes")

        all_labels = np.array(self.data[self.dimension])

        for i, metric in enumerate(self.metrics):
            _log.debug(f"Plotting subplot for {metric!r}")

            if max(self.data[metric]) == 0:
                raise PlottingError(f"no data to plot for {metric!r}")

            values = np.array(self.data[metric])
            n = min(np.count_nonzero(values), 9)
            idxs = np.argsort(values)[::-1][:n]

            sizes = values[idxs].tolist()
            labels = all_labels[idxs].tolist()
            if n == 9:
                sizes.append(sum(values) - sum(values[idxs]))
                labels.append("Others")

            _log.debug(f"Using labels: {labels}")
            axs[i].pie(sizes, labels=labels, autopct="%.0f%%", pctdistance=0.75)
            axs[i].set_title(metric)

        fig.suptitle(self.title)
        fig.tight_layout()
        return fig
