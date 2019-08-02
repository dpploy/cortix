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
    '''

    def __init__(self):

        self.use_mpi = False

        self.state = None

        self.ports = []

    def send(self, data, port):
        '''
        Send data through a given port.
        '''

        if isinstance(port, str):
            port = self.get_port(port)
            #matches = [p for p in self.ports if p.name == port]
            #assert len(matches) == 1,\
            #        'matches= %r port= %r, ports= %r'%(matches,port,self.ports)
            #port = matches[0]
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
            #matches = [p for p in self.ports if p.name == port]
            #assert(len(matches) == 1)
            #port = matches[0]
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
            reserved_port_names = self._get_reserved_port_names()
            if reserved_port_names is not None:
                assert name in reserved_port_names,\
                        'port name: {}, not allowed by module: {}'.format(name,self)
            port = Port(name,self.use_mpi)
            self.ports.append(port)

        return port

    def connect(self, port_name, connected_port):
        '''
        A simpler interface to create module connectivity. Connect the module port
        with `port_name` to a given `connected_port`.
        '''

        my_port = self.get_port(port_name)
        assert isinstance(connected_port, Port), "Connecting port must be of Port type"
        my_port.connect(connected_port)

    def run(self, state_comm=None, idx_comm=None):
        '''
        Run method.

        Parameters
        ----------
        state_comm: multiprocessing.Queue
            When using the Python `multiprocessing` library `state_comm` must have
            the module's `self.state` in it. That is, `state_comm.put(self.state)`
            must be the last command in the method before `return`.

        idx: index of the state in the communication queue.
        '''
        raise NotImplementedError('Module must implement run()')

    def _get_reserved_port_names(self):
        '''
        This is a helper function to check for reserved names of ports in the module.
        If there is no reservation on names or no checking of reserved names wanted,
        this function is the default function and nothing needs to be done on the
        developer side of the module child class.
        Otherwise this function must be overriden and an iterable container of strings
        must be returned.
        '''

        return None
