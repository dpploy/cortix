#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

from cortix.src.port import Port

class Module:
    """
    The representation of a Cortix module. This class is to be inherited by every
    Cortix module. It provides facilities for creating and connecting modules within
    the Cortix network.
    """
    def __init__(self):
        # list of ports (must be populated by the module)
        self.ports =  []

    def send(self, data, port):
        """
        Send data through a given provide port
        """
        pass

    def recv(self, port):
        """
        Receive data from a given use port
        """
        pass
