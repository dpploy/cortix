#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import enum

class PortType(enum.Enum):
    """
    Ports have two types: use & provide
    """
    USE = 0
    PROVIDE = 1

    def __str__(self):
        return self.name

class Port:
    '''
    The Port class provides an interface for creating ports
    and connecting them to other ports.
    '''

    def __init__(self, name=None, type=PortType.USE):
        self.set_name(name)
        self.set_type(type)
        self.connections = []

    def connect(self, port):
        assert isinstance(port, Port), "Connecting port must be of Port type"

        # Maintain two way connection
        if port not in self.connections:
            self.connections.append(port)

        if self not in port.connections:
            port.connections.append(self)

    def set_name(self, name):
        assert isinstance(name, str), "Port name must be a string"
        self.name = name

    def set_type(self, port_type):
        assert isinstance(port_type, PortType), "Port Type must be of type PortType"
        self.type = port_type

    def __eq__(self, other):
        if isinstance(other, Port):
            return self.name == other.name and self.type == other.type

    def __repr__(self):
        return "<{}, {}>".format(self.name, self.type)

if __name__ == "__main__":
    # Create some ports
    p1 = Port("test1", PortType.USE)
    p2 = Port("test2", PortType.PROVIDE)

    # Connect the ports
    p1.connect(p2)

    # View connections
    print(p1)
    print(p2)
    print(p1.connections)
    print(p2.connections)
