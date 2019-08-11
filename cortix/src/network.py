#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

from cortix.src.module import Module
from cortix.src.port import Port

class Network:
    '''Cortix network.

    '''

    def __init__(self, n_modules=None):
        '''Module super class constructor.

       '''
        self.n_modules = n_modules
        self.modules = list()

    def module(self, name):
        '''Add a module.

        '''

    def connect(self, module_port, module_port):
        '''Connect two modules using either their ports directly or inferred ports.

        Parameters
        ----------
        module_port: {Module,Port} or Module

        '''

    def connect(self, port_name_or_module, to_other_port=None):
        '''Connect two modules using either their ports directly or inferred ports.

        Parameters
        ----------
        port_name_or_module: str, Module
            Either a `port` name or a `Module` can be given. In the latter case
            the `name` attribute of the module will be used to get the `port`
            of the module passed. This port will be connected to the corresponding
            port of the calling object.
        to_other_port: Port
            A `port` object to connect to. This must be `None` or absent if the
            first argument is a `Module`.

        '''

        # Infer from types what to do with the intended module
        if isinstance(port_name_or_module, Module):
            assert to_other_port is None, 'Illegal syntax; only one argument needed.'
            other_module = port_name_or_module
            other_module_name = other_module.name
            if not other_module.name:
                other_module_name = other_module.__class__.__name__.lower()
            my_port = self.get_port(other_module_name)
            my_name = self.name
            if not my_name:
                my_name = self.__class__.__name__.lower()
            other_port = other_module.get_port(my_name)
            my_port.connect(other_port)

        if isinstance(port_name_or_module, str):
            assert isinstance(to_other_port, Port), 'Other port must be of Port type'
            port_name = port_name_or_module
            my_port = self.get_port(port_name)
            my_port.connect(to_other_port)

    def draw(self):
        pass
