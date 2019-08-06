#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

from cortix.src.port import Port

class Module:
    '''
    The representation of a Cortix module.
    This class is to be inherited by every Cortix module.
    It provides facilities for creating modules within the Cortix network.
    In addition Cortix will map one object of this class to a Python
    multiprocessing child process, or one executable object of this class to
    one MPI process.
    '''

    def __init__(self):
        '''
        Attributes
        ----------
        port_names_expected: list(str) or None
            A list of names of ports expected in the module. This will be compared
            to port names during runtime to check against the intended use of the
            module.
        state: any
            Any `pickle-able` data structure to be passed in a `multiprocessing.Queue`
            to the parent process.
        '''

        self.use_mpi = False

        self.state = None  # state data passed to parent process if any

        self.port_names_expected = None  # list of expected port names

        self.ports = []

    def send(self, data, port):
        '''
        Send data through a given port.
        '''

        if isinstance(port, str):
            port = self.get_port(port)
        elif isinstance(port, Port):
            assert port in self.ports, "Unknown port!"
        else:
            raise TypeError("port must be of Port or String type")

        port.send(data)

    def recv(self, port):
        '''
        Receive data from a given port
        '''

        if isinstance(port, str):
            port = self.get_port(port)
        elif isinstance(port, Port):
            assert port in self.ports, "Unknown port!"
        else:
            raise TypeError("port must be of Port or String type")

        return port.recv()

    def get_port(self, name):
        '''
        Get port by name; if it does not exist, create one.
        '''

        assert isinstance(name, str), 'port name must be of type str'
        port = None

        for p in self.ports:
            if p.name == name:
                port = p
                break

        if port is None:
            if self.port_names_expected:
                assert name in self.port_names_expected,\
                        'port name: {}, not expected by module: {}'.format(name,self)
            port = Port(name,self.use_mpi)
            self.ports.append(port)

        return port

    def connect(self, port_name, other_port):
        '''
        A simpler interface to create module connectivity. Connect the module port
        with `my_port_name` to a given `other_port`.
        '''

        my_port = self.get_port(port_name)
        assert isinstance(other_port, Port), "Other port must be of Port type"
        my_port.connect(other_port)

    def run(self, state_comm=None, idx_comm=None):
        '''
        Run method with an option to pass data back to the parent process when running
        Python multiprocessing mode.

        Notes
        -----
        For now, add this command: `state_comm.put((idx_comm,self.state))`
        to the bottom of your method. If you are not using `self.state`, then the
        command can be issued anywhere in the body of the function.

        Parameters
        ----------
        state_comm: multiprocessing.Queue
            When using the Python `multiprocessing` library `state_comm` must have
            the module's `self.state` in it. That is,
            `state_comm.put((idx_comm,self.state))` must be the last command in the
            method before `return`. In addition, self.state must be `pickle-able`.

        idx_comm: int
            Index of the state in the communication queue.
        '''
        raise NotImplementedError('Module must implement run()')
