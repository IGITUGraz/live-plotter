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

import logging

from liveplotter.plotrecorder import PlotterBase

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('mandelbrot')


class PlotMandelBrot(PlotterBase):
    def __init__(self, name):
        super().__init__(name)
        self.ax = None
        self.im = None

    def init(self):
        # Make sure you call the super `init` method. This initializes `self.plt`
        super().init()

        logger.info("First initializing plots in thread %s", self.entity_name)
        # It is necessary to assign the variable `self.fig` in this init function

        self.fig, self.ax = self.plt.subplots()
        self.ax.axis('off')

        return self

    def plot_loop(self, divtime, i):
        # Implements the plotting loop. In this case, it just returns the outcome of `plt.imshow`
        logger.debug("Plotting %s in %s", self.var_name, self.entity_name)

        if i == 0:
            self.im = self.ax.imshow(divtime, interpolation='none')

        else:
            self.im.set_array(divtime)

        return self.im,


def main():
    # NOTE: The name argument to the constructor HAS to match the string used as `var_name` for recording in `simulation.py`
    PlotMandelBrot('divtime').start()


if __name__ == "__main__":
    main()
