# -*- coding: utf-8 -*-

# This file is part of RealtimePlotter.
#
# RealtimePlotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RealtimePlotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RealtimePlotter.  If not, see <http://www.gnu.org/licenses/>.
#
# For more information see: https://github.com/anandtrex/RealtimePlotter

import logging
import pickle
from multiprocessing import Process, Event, current_process

import matplotlib.animation as animation

import zmq

rlogger = logging.getLogger('Recorder')
plogger = logging.getLogger('PlotterBase')

PORT = 5155
SENTINEL = 'SENTINEL'


class PlotRecorder:
    def __init__(self, port=PORT):
        """
        This is a ZMQ publisher

        :param int port: The port number to publish data (and subscribe to data)
        """

        context = zmq.Context()
        self.port = port
        self.socket = context.socket(zmq.PUB)
        self.socket.bind("tcp://*:%d" % self.port)

        rlogger.info("Listening on port %d", self.port)

    def record(self, var_name, var_value):
        """
        Call this method each time you want to record a variable with name `var_name` and value `var_value`.
        Usually, there is one plot for each `var_name`.

        :param var_name: Name of variable to record
        :param var_value: Value of variable to record
        """
        assert not isinstance(var_value, type(SENTINEL)) or var_value != SENTINEL,\
                "You cannot record a value {} since this conflicts with the internal SENTINEL string"
        topic = pickle.dumps(var_name, protocol=pickle.HIGHEST_PROTOCOL)
        messagedata = pickle.dumps(var_value, protocol=pickle.HIGHEST_PROTOCOL)
        self.socket.send_multipart([topic, messagedata])
        rlogger.debug("Sent message to topic %s", var_name)

    def close(self, var_name):
        """
        Call this method for each variable name `var_name` to clean up the plotting process

        :param var_name: Name of variable to clean up.
        """
        topic = pickle.dumps(var_name, protocol=pickle.HIGHEST_PROTOCOL)
        messagedata = pickle.dumps(SENTINEL, protocol=pickle.HIGHEST_PROTOCOL)
        self.socket.send_multipart([topic, messagedata])
        rlogger.debug("Sent close message to topic %s", var_name)


class PlotterBase(Process):
    def __init__(self, var_name, port=PORT):
        """
        This is a ZMQ subscriber.
        All plotter classes should inherit from this class and implement functions :meth:`.plot_loop` and
        :meth:`plot_once` as described in their respective documentation

        :param var_name: The name of the variable this class plots. This should match the variable name recorded by the
        class:`.PlotRecorder` class.
        :param int port: The port number to subscribe to data

        """

        super().__init__()

        self._exit = Event()

        self.var_name = var_name
        self.port = port
        self.entity_name = None
        self.socket = None
        self.fig = None
        self.plt = None

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
        Entry point for the realtime plotting when started as a separate process. This starts the loop
        """
        self.entity_name = current_process().name
        plogger.info("Starting new thread %s", self.entity_name)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)

        self.socket.connect("tcp://localhost:%d" % self.port)
        topic = pickle.dumps(self.var_name, protocol=pickle.HIGHEST_PROTOCOL)

        self.socket.setsockopt(zmq.SUBSCRIBE, topic)
        plogger.info("Subscribed to topic %s on port %d", self.var_name, self.port)

        self.init()
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
