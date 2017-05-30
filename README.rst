Realtime Plotter
----------------

.. contents::  Table of Contents



This package provides a simple interface to do realtime plotting using matplotlib.

Detailed documentation here: 
https://anandtrex.github.io/RealtimePlotter/


Requirements
************

System dependencies:

* zeromq

Python dependencies are listed in requirements.txt


Installation
************

.. code:: bash

    git clone git@github.com:IGITUGraz/RealtimePlotter.git
    cd RealtimePlotter
    pip install -r requirements.txt
    python3 setup.py install


Notes about backends
********************

This package has been tested with the *TkAgg* backend on linux and *Gtk3Agg* backend on macOS, but none of the other
combinations.

To set the default backend on linux, edit :code:`$HOME/.config/matplotlib/matplotlibrc` and add the following line:

.. code::

    backend : tkagg

This backend Requires tkinter to be installed -- the :code:`python3-tk` package on Ubuntu/Debian



To set the default backend on macOS, edit :code:`$HOME/.matplotlib/matplotlibrc` and add the following line:

.. code::

    backend : gtk3agg

This backed requires the pygobject package to be installed -- the :code:`py36-gobject3` package on MacPorts. (Repalce
py36 with your python3 version)


See [#]_ and [#]_ for more information

.. [#] http://matplotlib.org/faq/usage_faq.html#what-is-a-backend
.. [#] http://matplotlib.org/faq/virtualenv_faq.html


Usage
*****

It consists of two parts: a :code:`PlotRecorder` and a :code:`Plotter`.

For any code you have, you can record the values that you want to plot using the :code:`PlotRecorder` as follows:

.. code:: python

    from realtimeplotter.plotrecorder import PlotRecorder
    plot_recorder = PlotRecorder()


    def simulate():
      ...
      # Your simulation code here
      x = ...
      x_sq = x**2
      plot_recorder.record("x_sq", x_sq)



This sends the recorded variable to a ZeroMQ Queue, but otherwise is very low overhead and doesn't affect your
simulation, even if you decide not to do realtime plotting for any particular run.

After the simulation is finished, call :code:`plot_recorder.close('x_sq')` to do a clean shutdown.

To actually do realtime plotting, you would implement a :code:`Plotter` in a different file that inherits from :code:`PlotterBase`
as follows:

.. code:: python

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



and start it with:

.. code:: python

    PlotMandelBrot('x_sq').start()


Example
*******

You can find an example in the :code:`example` directory.

To run it, do :code:`cd example; ./run.sh`

It runs the two files :code:`example/simulation.py` and :code:`example/plot.py` and shows the fractal generation in realtime.

The animation will look like this:

.. image:: _static/animation.gif

