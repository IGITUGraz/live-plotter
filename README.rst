Realtime Plotter
----------------

This package provides a simple interface to do realtime plotting using matplotlib.


Requirements
************

System dependencies:

* zeromq

Python dependencies are listed in requirements.txt


Installation
************

```
git clone git@github.com:IGITUGraz/RealtimePlotter.git
cd RealtimePlotter
pip install -r requirements.txt
python3 setup.py install
```

Usage
*****

It consists of two parts: a `PlotRecorder` and a `Plotter`.

For any code you have, you can record the values that you want to plot using the `PlotRecorder` as follows:

```
from realtimeplotter.plotrecorder import PlotRecorder
plot_recorder = PlotRecorder()


def simulate():
  ...
  # Your simulation code here
  x = ...
  x_sq = x**2
  plot_recorder.record("x_sq", x_sq)

```

This sends the recorded variable to a ZeroMQ Queue, but otherwise is very low overhead and doesn't affect your
simulation, even if you decide not to do realtime plotting for any particular run.

After the simulation is finished, call `plot_recorder.close('x_sq')` to do a clean shutdown.

To actually do realtime plotting, you would implement a `Plotter` in a different file that inherits from `PlotterBase`
as follows:

```
class YourPlotter(PlotterBase):
    def init(self):
        # Make sure you call the super `init` method. This initializes `self.plt`
        super().init()

        logger.info("First initializing plots in thread %s", self.entity_name)
        # It is necessary to assign the variable `self.fig` in this init function

        self.fig = self.plt.figure()

        # Your initialization code here
        ...
        self.var_list = []

        return self

    def plot_loop(self, var_value, i):
        # Implements the plotting loop. In this case, it just returns the outcome of `plt.imshow`
        logger.debug("Plotting %s in %s", self.var_name, self.entity_name)

        # Plot the variable and return a matplotlib.artist.Artist object

```

and start it with:

```
PlotMandelBrot('x_sq').start()
```

Example
*******

You can find an example in the `example` directory.

To run it, do `cd example; ./run.sh`

It runs the two files `example/simulation.py` and `example/plot.py` and shows the fractal generation in realtime.

The animation will look like this:

.. image:: example/animation.gif