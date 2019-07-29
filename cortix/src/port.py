#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import enum
from multiprocessing import Queue

class Port:
    '''
    The Port class provides an interface for creating ports and connecting them to
    other ports for the purpose of data tranfer. Data exchange takes place by
    send and/or receive calls on a given port. The concept of a port is that of a data
    transfer "interaction." This can be one- or two-way with sends and receives.
    '''

    def __init__(self, name=None):
        self.id = None
        self.name = name
        self.use_mpi = True

        # Fall back to multiprocessing if mpi4py is not found
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
        '''
        Connect the port to another port

        `port`: A Port object that represents the port to connect to.
        '''
        assert isinstance(port, Port), "Connecting port must be of Port type"

        self.connected = port
        port.connected = self
        port.use_mpi = self.use_mpi

    def send(self, data):
        '''
        Send data to the connected port

        `data`: Any pickelable form of data
        '''
        if self.connected:
            if self.use_mpi:
                self.comm.send(data, dest=self.connected.rank, tag=self.id)
            else:
                self.q.put(data)

    def recv(self):
        '''
        Returns the data recieved from the connected port.
        NOTE: This function will block until data is received from the connected port
        '''
        if self.connected:
            if self.use_mpi:
                return self.comm.recv(source=self.connected.rank, tag=self.connected.id)
            else:
                return self.connected.q.get()


    def __eq__(self, other):
        '''
        Ports are the same if their names are the same
        '''
        if isinstance(other, Port):
            return self.name == other.name

    def __repr__(self):
        '''
        Port name representation
        '''
        return self.name

if __name__ == '__main__':
    # Create some ports
    p1 = Port('test1')
    p2 = Port('test2')

    # Connect the ports
    p1.connect(p2)

    # View connections
    print(p1)
    print(p2)
    print(p1.connected)
    print(p2.connected)
