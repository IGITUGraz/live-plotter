import logging
import numpy as np

from realtimeplotter.plotrecorder import PlotRecorder

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
