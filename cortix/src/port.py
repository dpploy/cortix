#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

from multiprocessing import Pipe

class Port:
    """Provides a method of communication between modules.

    The Port class provides an interface for creating ports and connecting them to
    other ports for the purpose of data transfer. Data exchange takes place by
    send and/or receive calls on a given port. The concept of a port is that of a data
    transfer "interaction." This can be one- or two-way with sends and receives.
    A port is connected to only one other port; as two ends of a pipe are connected.
    """

    def __init__(self, name=None, use_mpi=False):
        '''Constructs a Port object

        Parameters
        ----------
        name: str
          The name of the Port object
        use_mpi: bool
          True for MPI, False for Multiprocessing

        Attributes
        ----------
            id: int
            name: string
            use_mpi: bool

        '''

        self.id = None
        self.name = name
        self.use_mpi = use_mpi

        if self.use_mpi:
            from mpi4py import MPI
            self.comm = MPI.COMM_WORLD
            self.rank = None
        else:
            self.pipe = None

        self.connected_port = None

    def connect(self, port):
        '''Connect this port to another port

        Ports must be connected for data to flow between them.

        Parameters
        ----------
        port: Port
           A Port object to connect to.

        Returns
        -------
        None

        '''

        assert isinstance(port, Port), 'Connecting port must be of Port type'

        self.connected_port = port
        port.connected_port = self
        port.use_mpi = self.use_mpi

        if not port.use_mpi:
            (self.pipe, port.pipe) = Pipe()

    def send(self, data, tag=None):
        '''
        Send data to the connected port.

        If the sending port is not connected do nothing.

        Parameters
        ----------
        data: any
           This data must be pickleable.
        tag: int, optional
           MPI tag used in sending data.

        '''

        if not tag:
            tag = self.id

        if self.connected_port:
            if self.use_mpi:
                # This is an MPI blocking send
                self.comm.send(data, dest=self.connected_port.rank, tag=tag)
            else:
                self.pipe.send(data)

        return

    def __is_connected(self):
        '''
        Check for a connected port.

        Parameters
        ----------
        None

        Returs
        ------
        False or True: boolean
        Default False.

        '''
        if self.connected_port:
            return True
        else:
            return False
    is_connected = property(__is_connected, None, None, None)

    def recv(self):
        '''
        Receive data from the connected port.

        Warning
        -------
        This function will block if no data has been sent yet.

        Returns
        --------
        data: any

        '''
        if self.connected_port:
            if self.use_mpi:
                # This is an MPI blocking receive
                return self.comm.recv(source=self.connected_port.rank,
                        tag=self.connected_port.id)
            else:
                return self.pipe.recv()

        return

    def __eq__(self, other):
        '''Check for port equality'''

        return self.name == other.name

    def __repr__(self):
        '''Port name representation'''

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
