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
from builtins import object

import logging
import pickle

import zmq

from liveplotter import PORT, SENTINEL

rlogger = logging.getLogger('liveplotter.plotrecorder')


class PlotRecorder(object):
    """
    This is a ZMQ publisher

    :param int port: The port number to publish data (and subscribe to data)
    """

    def __init__(self, port=PORT):
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
        assert not isinstance(var_value, type(SENTINEL)) or var_value != SENTINEL, \
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
