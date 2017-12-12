# -*- coding: utf-8 -*-

# This file is part of live-plotter.
#
# live-plotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# live-plotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with live-plotter.  If not, see <http://www.gnu.org/licenses/>.
#
# For more information see: https://github.com/anandtrex/live-plotter

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import super
from future import standard_library

standard_library.install_aliases()

import logging

import numpy as np
from liveplotter.plotter import PlotterBase
from matplotlib.ticker import FixedLocator

logger = logging.getLogger('liveplotter.plotter_impls')


class GeneralPlotter(PlotterBase):
    """
    This does a live plot of a line of one (and only one) variable. Look at :class:`~.GeneralArrayPlotter` if you want
    to plot multiple variables.

    NOTE: None of its function should be called directly. These functions are indirectly called by :class:`~.PlotterBase` and :class:`~.PlotRecorder`
    """

    def init(self, title=None, xlabel=None, ylabel=None, plot_frequency=10, **plot_kwargs):
        """
        The init function that is called once at the beginning.

        :param title: Plot title
        :param xlabel: Plot xlabel
        :param ylabel: Plot y label
        :param plot_frequency: How often should the plot be updated? In the intermediate time steps the data is stored,
         but the plot itself is not updated
        :param plot_kwargs: Any other arguments to be passed to the matplotlib plot function.
        :return: self
        """
        super().init()

        self.plot_frequency = plot_frequency

        logger.info("First initializing plots in thread %s", self.entity_name)

        self.fig, self.ax = self.plt.subplots()
        if title is not None:
            self.ax.set_title(title)
        if xlabel is not None:
            self.ax.set_xlabel(xlabel)
        if ylabel is not None:
            self.ax.set_ylabel(ylabel)

        self.ax.set_autoscale_on(True)  # enable autoscale
        self.ax.autoscale_view(True, True, True)

        self.variable_list = []
        self.xs = []

        self.l, = self.ax.plot([], [], **plot_kwargs)  # Plot blank data

        return self

    def plot_loop(self, data, it):
        """
        The actual function that updates the data in the plot initialized in :meth:`~.init`

        :param data: The data that is recorded with :class:`~.PlotRecorder`. It can be a just a scalar (in which case
         the iteration number is used on the x axis) OR a 2-D tuple with the first value containing the scalar to plot
         and the second value containing the corresponding x value.
        :param it: The iteration number (independent of the actual x value)
        :return:
        """
        logger.debug("Plotting %s in %s", self.var_name, self.entity_name)

        if not isinstance(data, tuple):
            var = data
            x = it
        elif len(data) == 2 and isinstance(data, tuple):
            var, x = data
        else:
            logger.error("Data is %s", data)
            raise RuntimeError()

        assert len(var) == 0, "The passed in variable should be a scalar"

        self.variable_list.append(var)
        self.xs.append(x)

        if it % self.plot_frequency == 0:
            self.l.set_data(self.xs, self.variable_list)

            self.ax.relim()
            self.ax.autoscale_view(True, True, True)


class GeneralArrayPlotter(PlotterBase):
    """
    This does a live plot of lines for multiple variables variable. Look at :class:`~GeneralPlotter` if you want
    to plot only a single variable.

    NOTE: None of its function should be called directly. These functions are indirectly called by :class:`~.PlotterBase` and :class:`~.PlotRecorder`
    """

    def init(self, title=None, xlabel=None, ylabel=None, plot_frequency=10, **plot_kwargs):
        """
        The init function that is called once at the beginning.

        :param title: Plot title
        :param xlabel: Plot xlabel
        :param ylabel: Plot y label
        :param plot_frequency: How often should the plot be updated? In the intermediate time steps the data is stored,
         but the plot itself is not updated
        :param plot_kwargs: Any other arguments to be passed to the matplotlib plot function.
        :return: self
        """

        super().init()

        logger.info("First initializing plots in thread %s", self.entity_name)
        self.plot_frequency = plot_frequency
        self.plot_kwargs = plot_kwargs

        self.fig, self.ax = self.plt.subplots()
        if title is not None:
            self.ax.set_title(title)
        if xlabel is not None:
            self.ax.set_xlabel(xlabel)
        if ylabel is not None:
            self.ax.set_ylabel(ylabel)

        self.ax.set_autoscale_on(True)  # enable autoscale
        self.ax.autoscale_view(True, True, True)

        self.var_list = []
        self.xs = []

        self.lines = []

        return self

    def plot_loop(self, data, it):
        """
        The actual function that updates the data in the plot initialized in :meth:`~.init`

        :param data: The data that is recorded with :class:`~.PlotRecorder`. It can be a just a vector with one value
         for every variable/line you want to plot (in which case the iteration number is used on the x axis)
         OR a 2-D tuple with the first value containing the vector to plot as above and the second value containing
         the corresponding x value.
        :param it: The iteration number (independent of the actual x value)
        :return:
        """

        if not isinstance(data, tuple):
            var = data
            x = it
        elif len(data) == 2 and isinstance(data, tuple):
            var, x = data
        else:
            logger.error("Data is %s", data)
            raise RuntimeError()

        logger.debug("Plotting %s in %s", self.var_name, self.entity_name)

        assert len(var.shape) == 1, "The passed in variable should be a vector, with one value for every variable"

        self.var_list.append(var)
        self.xs.append(x)

        if it == 0 and self.lines == []:
            n_y = len(var)

            for _ in range(n_y):
                l, = self.ax.plot([], [], **self.plot_kwargs)  # Plot blank data
                self.lines.append(l)

        if it > 0 and it % self.plot_frequency == 0:
            var_list_arr = np.array(self.var_list)

            for j, l in enumerate(self.lines):
                l.set_data(self.xs, var_list_arr[:, j])

            self.ax.relim()
            self.ax.autoscale_view(True, True, True)  # NOTE: Fairly important here


class GeneralImagePlotter(PlotterBase):
    """
    This does a live plot of a 2-D image using matplotlib's imshow

    NOTE: None of its function should be called directly. These functions are indirectly called by :class:`~.PlotterBase` and :class:`~.PlotRecorder`
    """

    def init(self, title=None, plot_frequency=10, **imshow_kwargs):
        """
        The init function that is called once at the beginning.

        :param title: Plot title
        :param plot_frequency: How often should the plot be updated? In the intermediate time steps the data is dropped.
        :param imshow_kwargs: Any other arguments to be passed to the matplotlib imshow function.
        :return: self
        """
        super().init()

        self.plot_frequency = plot_frequency
        self.imshow_kwargs = imshow_kwargs

        logger.info("First initializing plots in thread %s", self.entity_name)

        self.fig, self.ax = self.plt.subplots()

        if title is not None:
            self.ax.set(title=title)
        self.ax.axis('off')

        return self

    def plot_loop(self, image, it):
        """
        The actual function that updates the data in the plot initialized in :meth:`~.init`

        :param image: The image that is recorded with :class:`~.PlotRecorder`. It should be a 2-D numpy array
        :param it: The iteration number (independent of the actual x value)
        :return:
        """
        logger.debug("Plotting %s in %s", self.var_name, self.entity_name)

        assert isinstance(image, np.ndarray), "The passed in image should by a numpy array"
        assert len(image.shape) == 2, "The image to be shown should be 2-dimensional"

        if it == 0:
            self.im = self.ax.imshow(image, **self.imshow_kwargs)

        else:
            if it % self.plot_frequency == 0:
                self.im.set_array(image)


class SpikePlotter(PlotterBase):
    """
    This is specifically for plotting "spikes" i.e. binary arrays of 0s and 1s, where the index denotes the spike source

    NOTE: None of its function should be called directly. These functions are indirectly called by :class:`~.PlotterBase` and :class:`~.PlotRecorder`
    """

    def init(self, title=None, xlabel=None, ylabel=None, plot_frequency=10, **plot_kwargs):
        """
        The init function that is called once at the beginning.

        :param title: Plot title
        :param xlabel: Plot xlabel
        :param ylabel: Plot y label
        :param plot_frequency: How often should the plot be updated? In the intermediate time steps the data is stored,
         but the plot itself is not updated
        :param plot_kwargs: Any other arguments to be passed to the matplotlib plot function.
        :return: self
        """

        super().init()

        logger.info("First initializing plots in thread %s", self.entity_name)

        self.plot_frequency = plot_frequency
        self.plot_kwargs = plot_kwargs

        self.fig, self.ax = self.plt.subplots()
        if title is not None:
            self.ax.set_title(title)
        if xlabel is not None:
            self.ax.set_xlabel(xlabel)
        if ylabel is not None:
            self.ax.set_ylabel(ylabel)

        self.ax.set_autoscale_on(True)  # enable autoscale
        self.ax.autoscale_view(True, True, True)

        self.lines = []
        self.xs = []
        self.spikes_list = []

        return self

    def plot_loop(self, data, it):
        """
        The actual function that updates the data in the plot initialized in :meth:`~.init`

        :param data: The data that is recorded with :class:`~.PlotRecorder`. It can be a just a vector with one binary
         value (0 or 1) for every spike source you want to plot (in which case the iteration number is used on the x axis)
         OR a 2-D tuple with the first value containing the vector of spikes to plot as above and the second value
         containing the corresponding x value.
        :param it: The iteration number (independent of the actual x value)
        :return:
        """
        if not isinstance(data, tuple):
            spikes = data
            x = it
        elif len(data) == 2 and isinstance(data, tuple):
            spikes, x = data
        else:
            logger.error("Data is a tuple with too many values (should be at most 2): data: %s", data)
            raise RuntimeError()

        logger.debug("Plotting %s in %s", self.var_name, self.entity_name)
        assert len(spikes.shape) == 1, "The spikes variable should be a vector, one for each source." \
                                       "But its shape is {} at {}".format(spikes.shape, x)
        assert np.logical_or(spikes == 0, spikes == 1).all(), "Spike data should be either or 1"

        sps = spikes * (np.arange(len(spikes)) + 1)
        sps[sps == 0.] = -10
        self.spikes_list.append(sps)
        self.xs.append(x)

        if it == 0 and self.lines == []:
            n_y = len(spikes)
            for _ in range(n_y):
                l, = self.ax.plot([], [], linestyle='.', **self.plot_kwargs)
                self.lines.append(l)
            self.ax.set_ylim(1, len(spikes) + 1)
            self.ax.yaxis.set_major_locator(FixedLocator([0, len(spikes) + 1]))

        if it > 0 and it % self.plot_frequency == 0:
            spike_list_arr = np.array(self.spikes_list)
            for j, l in enumerate(self.lines):
                l.set_data(self.xs, spike_list_arr[:, j])

            self.ax.set_xlim(self.xs[-1] - 100, self.xs[-1])

            self.ax.relim()
