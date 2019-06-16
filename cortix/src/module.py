#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

from cortix.src.port import Port

class Module:
    """
    The representation of a Cortix module.
    This class is to be inherited by every Cortix module.
    It provides facilities for creating modules within the Cortix network.
    """

    def __init__(self):
        self.rank = None
        self.ports =  []

    def send(self, data, port):
        """
        Send data through a given provide port
        """
        if isinstance(port, str):
            matches = [p for p in self.ports if p.name == port]
            assert(len(matches) == 1)
            port = matches[0]
        elif isinstance(port, Port):
            assert port in self.ports, "Unknown port!"
        else:
            raise TypeError("port must be of Port or String type")

        port.send(data)

    def recv(self, port):
        """
        Receive data from a given port
        """
        if isinstance(port, str):
            matches = [p for p in self.ports if p.name == port]
            assert(len(matches) == 1)
            port = matches[0]
        elif isinstance(port, Port):
            assert port in self.ports, "Unknown port!"
        else:
            raise TypeError("port must be of Port or String type")
        return port.recv()

    def add_port(self, port):
        """
        Add a port to the module
        """
        assert isinstance(port, Port), "port must be of type Port"
        if port not in self.ports:
            self.ports.append(port)

    def run(self):
        raise NotImplementedError("Modules must implement run()")
