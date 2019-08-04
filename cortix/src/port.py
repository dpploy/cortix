#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

from multiprocessing import Queue

class Port:
    '''
    The Port class provides an interface for creating ports and connecting them to
    other ports for the purpose of data tranfer. Data exchange takes place by
    send and/or receive calls on a given port. The concept of a port is that of a data
    transfer "interaction." This can be one- or two-way with sends and receives.
    A port is connected to only one other port; as two ends of a pipe are connected.
    '''

    def __init__(self, name=None, use_mpi=False):

        self.id = None
        self.name = name
        self.use_mpi = use_mpi

        if self.use_mpi:
            from mpi4py import MPI
            self.comm = MPI.COMM_WORLD
            self.rank = None
        else:
            self.q = Queue()    # only passes picke-able objects

        self.connected_port = None # the `other` port connected to `this` port

    def connect(self, port):
        '''
        Connect the port to another port

        `port`: A Port object that represents the port to connect to.
        '''
        assert isinstance(port, Port), 'Connecting port must be of Port type'

        self.connected_port = port
        port.connected_port = self
        port.use_mpi = self.use_mpi

    def send(self, data, tag=None):
        '''
        Send data to the connected port. If the sending port is not connected do nothing.

        Parameters
        ----------
        data: any pickle-able data

        Returns
        -------
        None
        '''

        if not tag:
            tag = self.id

        if self.connected_port:
            if self.use_mpi:
                # This is an MPI blocking send
                self.comm.send(data, dest=self.connected_port.rank, tag=tag)
            else:
                self.q.put(data)

    def recv(self):
        '''
        Returns the data received from the connected port.
        '''
        if self.connected_port:
            if self.use_mpi:
                # This is an MPI blocking receive
                return self.comm.recv(source=self.connected_port.rank,
                        tag=self.connected_port.id)
            else:
                return self.connected_port.q.get()

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
    print(p1.connected_port)
    print(p2.connected_port)
