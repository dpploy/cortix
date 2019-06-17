#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import enum
from multiprocessing import Queue

class Port:
    '''
    The Port class provides an interface for creating ports
    and connecting them to other ports.
    '''

    def __init__(self, name=None):
        self.set_name(name)
        self.id = None
        self.use_mpi = True

        try:
            from mpi4py import MPI
        except ImportError:
            self.use_mpi = False

        if self.use_mpi:
            self.comm = MPI.COMM_WORLD
            self.rank = self.comm.Get_rank()

        self.q = Queue()
        self.connected = None

    def connect(self, port):
        assert isinstance(port, Port), "Connecting port must be of Port type"

        self.connected = port
        port.connected = self
        port.use_mpi = self.use_mpi

    def send(self, data):
        if self.use_mpi:
            self.comm.send(data, dest=self.connected.rank, tag=self.id)
        else:
            self.q.put(data)

    def recv(self):
        if self.use_mpi:
            return self.comm.recv(source=self.connected.rank, tag=self.connected.id)
        else:
            return self.connected.q.get()

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
    print(p1.connected)
    print(p2.connected)
