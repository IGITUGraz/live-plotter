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
from builtins import range
from future import standard_library
standard_library.install_aliases()
import logging
import numpy as np

from liveplotter.plotrecorder import PlotRecorder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mandelbrot')
recorder = PlotRecorder()


def mandelbrot(h, w, maxit):
    """
    Returns an image of the Mandelbrot fractal of size (h,w).
    """
    y, x = np.ogrid[-1.4:1.4:h * 1j, -2:0.8:w * 1j]
    c = x + y * 1j
    z = c
    divtime = maxit + np.zeros(z.shape, dtype=int)

    for i in range(maxit):
        z = z ** 2 + c
        diverge = z * np.conj(z) > 2 ** 2
        div_now = diverge & (divtime == maxit)
        divtime[div_now] = i + 100
        z[diverge] = 2
        logger.debug("Updating divtime")
        recorder.record('divtime', divtime)

    return divtime


def main():
    mandelbrot(1000, 1000, 40)
    recorder.close('divtime')


if __name__ == '__main__':
    main()
