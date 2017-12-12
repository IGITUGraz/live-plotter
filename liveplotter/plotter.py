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
import pickle
from multiprocessing import Process, Event, current_process

import zmq
import matplotlib.animation as animation

from liveplotter import PORT, SENTINEL

plogger = logging.getLogger('liveplotter.plotter')


class PlotterBase(Process):
    """
    This is a ZMQ subscriber.
    To implement your own plotters, use this as your base class and implement functions :meth:`.plot_loop` and
    :meth:`plot_once` as described in their respective documentation

    See provided implementations below in :mod:`liveplotter.plotter_impls`

    :param var_name: The name of the variable this class plots. This should match the variable name recorded by the
     class:`.PlotRecorder` class.
    :param int port: The port number to subscribe to data
    """

    def __init__(self, var_name, port=PORT, **init_kwargs):

        super().__init__()

        self._exit = Event()

        self.var_name = var_name
        self.port = port
        self.entity_name = None
        self.socket = None
        self.fig = None
        self.plt = None
        self.init_kwargs = init_kwargs

    def init(self):
        """
        This method is called after a new process has been created, and should be used to initialize everything that
        needs to be initialized in the new process (i.e. after the fork).
        Override this method to create fig, ax etc. as needed

        **NOTE:** This method SHOULD assign the created figure to the class variable `self.fig`.
        """

        plogger.debug("Calling init of base class")
        import matplotlib.pyplot as plt
        self.plt = plt
        return self

    def run(self):
        """
        Entry point for the live plotting when started as a separate process. This starts the loop
        """
        self.entity_name = current_process().name
        plogger.info("Starting new thread %s", self.entity_name)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)

        self.socket.connect("tcp://localhost:%d" % self.port)
        topic = pickle.dumps(self.var_name, protocol=pickle.HIGHEST_PROTOCOL)

        self.socket.setsockopt(zmq.SUBSCRIBE, topic)
        plogger.info("Subscribed to topic %s on port %d", self.var_name, self.port)

        self.init(**self.init_kwargs)
        # Reference to animation required so that GC doesn't clean it up.
        # WILL NOT work if you remove it!!!!!
        # See: http://matplotlib.org/api/animation_api.html
        ani = animation.FuncAnimation(self.fig, self.loop, interval=100)
        self.plt.show()

    def loop(self, i):
        """
        The function that runs the loop. At each call, it listens for a new message of the appropriate topic/var_name
        (given in the constructor). When it receives the message, it calls :meth:`.plot_loop`

        :param int i: The plot iteration passed in by the matplotlib animation api call
        """
        if not self._exit.is_set():
            plogger.debug("%d", i)
            var_value = pickle.loads(self.socket.recv_multipart()[1])
            plogger.debug("Received value")
            if isinstance(var_value, type(SENTINEL)) and var_value == SENTINEL:
                self._exit.set()
            else:
                return self.plot_loop(var_value, i)

    def plot_loop(self, var_value, i):
        """
        This method is called each time the plot needs to be updated. This should return an iterable of matplotlib
        :class:`matplotlib.artist.Artist`

        **NOTE:** This method should only use the local variables `self.plt` and `self.fig` etc. for plotting. Do not use
        global variables, since this can cause problems due to the multiprocessing being used (and matplotlib's limited
        support for it)

        :param object var_value: The value of the object recorded using the :meth:`.PlotRecorder.record` call.
        :param int i: The iteration number of the plot
        :return: An iterable of :class:`matplotlib.artist.Artist`

        """
        raise NotImplementedError()
