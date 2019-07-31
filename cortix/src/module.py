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
        self.ports = []

    def send(self, data, port):
        '''
        Send data through a given port.
        '''
        if isinstance(port, str):
            matches = [p for p in self.ports if p.name == port]
            assert len(matches) == 1,\
                    'matches= %r port= %r, ports= %r'%(matches,port,self.ports)
            port = matches[0]
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
            matches = [p for p in self.ports if p.name == port]
            assert(len(matches) == 1)
            port = matches[0]
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
            port = Port(name,self.use_mpi)
            self.ports.append(port)

        return port

    def run(self):
        raise NotImplementedError('Modules must implement run()')
