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
from future import standard_library

standard_library.install_aliases()
import logging

from liveplotter.plotter_impls import GeneralImagePlotter

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('mandelbrot')

if __name__ == "__main__":
    # NOTE: The name argument to the constructor HAS to match the string used as `var_name` for recording in `simulation.py`
    GeneralImagePlotter('divtime', plot_frequency=1).start()
