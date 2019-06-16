#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import enum
from mpi4py import MPI
from threading import Thread

class Port:
    '''
    The Port class provides an interface for creating ports
    and connecting them to other ports.
    '''

    def __init__(self, name=None):
        self.set_name(name)
        self.id = None
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.connections = []
        self.data = {}

    def connect(self, port):
        assert isinstance(port, Port), "Connecting port must be of Port type"

        # Maintain two way connection
        if port not in self.connections:
            self.connections.append(port)

        if self not in port.connections:
            port.connections.append(self)

    def send(self, port, data):
        if port in self.connections:
            self.comm.send(data, dest=port.rank, tag=self.id)


    def send_all(self, data):
        for port in self.connections:
            self.send(port, data)

    def recv(self, port):
        if port in self.connections:
            return self.comm.recv(source=port.rank, tag=port.id)

    def recv_all(self):
        data = {}
        for port in self.connections:
            data[port.name] = self.recv(port)
        return data

    def set_name(self, name):
        assert isinstance(name, str), "Port name must be a string"
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Port):
            return self.name == other.name

    def __repr__(self):
        return self.name

if __name__ == "__main__":
    # Create some ports
    p1 = Port("test1")
    p2 = Port("test2")

    # Connect the ports
    p1.connect(p2)

    # View connections
    print(p1)
    print(p2)
    print(p1.connections)
    print(p2.connections)
