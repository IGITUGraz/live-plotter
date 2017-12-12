Live Plotter
------------

.. contents::  Table of Contents



This package provides a simple interface to do live plotting using matplotlib.

Detailed documentation here:
https://anandtrex.github.io/live-plotter/

Supports Python 2.7+ and Python 3.2+

Requirements
************

System dependencies:

* zeromq

Python dependencies are listed in requirements.txt

Installation
************

.. code:: bash

    git clone git@github.com:IGITUGraz/live-plotter.git
    cd live-plotter
    # Use pip3 and python3 to use Python 3.x
    pip install -r requirements.txt
    python setup.py install

You can also do:

.. code:: bash

    pip install --process-dependency-links git+https://github.com/anandtrex/live-plotter.git


Notes about backends
********************

This package has been tested with the *TkAgg* backend on linux and *Gtk3Agg* backend on macOS, but none of the other
combinations.

To set the default backend on linux, edit :code:`$HOME/.config/matplotlib/matplotlibrc` and add the following line:

.. code::

    backend : tkagg

This backend requires tkinter to be installed -- the :code:`python-tk` ( :code:`python3-tk`) package on Ubuntu/Debian



To set the default backend on macOS, edit :code:`$HOME/.matplotlib/matplotlibrc` and add the following line:

.. code::

    backend : gtk3agg

This backend requires the pygobject package to be installed -- the :code:`py27-gobject3` ( :code:`py36-gobject3` --
replace py36 with your python3 version) package on MacPorts.


See [#]_ and [#]_ for more information

.. [#] http://matplotlib.org/faq/usage_faq.html#what-is-a-backend
.. [#] http://matplotlib.org/faq/virtualenv_faq.html


Usage
*****

Record data to be plotted
~~~~~~~~~~~~~~~~~~~~~~~~~

It consists of two parts: a :code:`PlotRecorder` and a :code:`Plotter`.

For any code you have, you can record the values that you want to plot using the :code:`PlotRecorder` as follows:

.. code:: python

    from liveplotter.plotrecorder import PlotRecorder
    plot_recorder = PlotRecorder()


    def simulate():
      ...
      # Your simulation code here
      x = ...
      x_sq = x**2
      plot_recorder.record("x_sq", x_sq)



This sends the recorded variable to a ZeroMQ Queue, but otherwise is very low overhead and doesn't affect your
simulation, even if you decide not to do live plotting for any particular run.

After the simulation is finished, call :code:`plot_recorder.close('x_sq')` to do a clean shutdown.


Set up live plotting
~~~~~~~~~~~~~~~~~~~~

To actually do live plotting, you can do one of two things:

Use one of the existing live plot classes
+++++++++++++++++++++++++++++++++++++++++

There are plotting methods available for single lines, multiple lines, images and spikes. Look at the documentation
in the classes in :code:`liveplotter.plotter_impls.py` in the `documentation <https://anandtrex.github.io/live-plotter/liveplotter.html>`_

Write your own live plot class
++++++++++++++++++++++++++++++


would implement a :code:`Plotter` in a different file that inherits from :code:`PlotterBase`
as follows:

.. code:: python

    from liveplotter.plotrecorder import PlotterBase
    
    class YourPlotter(PlotterBase):
        def init(self):
            # Make sure you call the super `init` method. This initializes `self.plt`
            super().init()

            logger.info("First initializing plots in thread %s", self.entity_name)
            # It is necessary to assign the variable `self.fig` in this init function

            self.fig, self.ax = self.plt.subplots()

            # Your initialization code here
            ...

            return self

        def plot_loop(self, var_value, i):
            # Implements the plotting loop.
            logger.debug("Plotting %s in %s", self.var_name, self.entity_name)

            # Plot the variable and return a matplotlib.artist.Artist object



And start it with:

.. code:: python

    YourPlotter('x_sq').start()


Example
*******

You can find an example in the :code:`example` directory.

To run it, do :code:`cd example; ./run.sh`

It runs the two files :code:`example/simulation.py` and :code:`example/plot.py` and shows the fractal generation live.

The animation will look like this:

.. image:: _static/animation.gif

Building documentation locally
******************************

After cloning the repository, go to the doc directory and first install the documentation requirements with

.. code:: bash

    cd doc
    pip install -r requirements.txt  # use pip3 for python3

Then run:

.. code:: bash

    make html

and open the documentation at :code:`doc/build/html/index.html`