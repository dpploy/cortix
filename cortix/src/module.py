#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

from cortix.src.port import Port

class Module:
    '''Cortix module super class.

    This class provides facilities for creating modules within the Cortix network.
    Cortix will map one object of this class to either a Multiprocessing or MPI
    process depending on the user's configuration.

    Note
    ----
    This class is to be inherited by every Cortix module.
    In order to execute, modules *must* override the `run` method, which will be
    executed during the simulation

    Attributes
    ----------
    name: str
        A name given to the instance. Default is `None`.
    port_names_expected: list(str), None
        A list of names of ports expected in the module. This will be compared
        to port names during runtime to check against the intended use of the
        module.
    state: any
        Any `pickle-able` data structure to be passed in a `multiprocessing.Queue`
        to the parent process or to be gathered in the root MPI process.
        Default is `None`.
    use_mpi: bool
        True for MPI, false for Multiprocessing
    ports: list(Port)
        A list of ports contained by the module

    '''

    def __init__(self):
        '''Module super class constructor

        This must be called in the constructor of every Cortix module like so:

        >> super()__init__()

       '''
        self.name = None
        self.port_names_expected = None
        self.state = None
        self.use_mpi = False
        self.ports = []

    def send(self, data, port):
        '''Send data through a given port.

        Parameters
        ----------
        data: any
            The data being sent out - must be pickleable
        port: Port, str
            A Port object to send the data through, or its string name

        '''

        if isinstance(port, str):
            port = self.get_port(port)
        elif isinstance(port, Port):
            assert port in self.ports, "Unknown port!"
        else:
            raise TypeError("port must be of Port or String type")

        port.send(data)

    def recv(self, port):
        '''Receive data from a given port

        Warning
        -------
        This function will block until data is available

        Parameters
        ----------
        port: Port, str
            A Port object to send the data through, or its string name

        Returns
        -------
        data: any
            The data received through the port

        '''

        if isinstance(port, str):
            port = self.get_port(port)
        elif isinstance(port, Port):
            assert port in self.ports, "Unknown port!"
        else:
            raise TypeError("port must be of Port or String type")

        return port.recv()

    def get_port(self, name):
        '''Get port by name; if it does not exist, create one.

        Parameters
        ----------
        name: str
            The name of the port to get

        Returns
        -------
        port: Port
            The port object with the corresponding name

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

    def connect(self, port_name_or_module, to_other_port=None):
        '''Connect two modules using ports corresponding to their name

        Parameters
        ----------
        port_name_or_module: str, Module
            Either a `port` name or a `Module` can be given. In the latter case
            the `name` attribute of the module will be used to get the `port`
            of the module passed. This port will be connected to the port of the
            calling object.
        to_other_port: Port
            A `port` object to connect to. This must be `None` or absent if the
            first argument is a `Module`.
        '''

        # Infer from types what to do with the intended module
        if isinstance(port_name_or_module, Module):
            assert to_other_port is None, 'Illegal syntax.'
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

    def run(self, *args):
        '''Module run function

        Run method with an option to pass data back to the parent process when running
        in Python multiprocessing mode. If the user does not want to share data with
        the parent process, this function can be overriden with `run(self)`
        or `run(self, *args)` as long as `self.state = None`.
        If `self.state` points to anything but `None`, the user must use
        `run(self, *args).

        Notes
        -----
        When in multiprocessing, `*args` has two elements: `comm_idx` and `comm_state`.
        To pass back the state of the module, the user should insert the provided
        index `comm_idx` and the `state` into the queue as follows:

            if not self.use_mpi:
                try:
                    pickle.dumps(self.state)
                except pickle.PicklingError:
                    args[1].put((arg[0],None))
                else:
                    args[1].put((arg[0],self.state))

        at the bottom of the user defined run() function.

        Warning
        -------
        This function must be overridden by all Cortix modules

        Parameters
        ----------
        comm_idx: int
            Index of the state in the communication queue.

        comm_state: multiprocessing.Queue
            When using the Python `multiprocessing` library `state_comm` must have
            the module's `self.state` in it. That is, `state_comm.put((idx_comm,self.state))`
            must be the last command in the method before `return`. In addition, self.state must be `pickle-able`.
        '''
        raise NotImplementedError('Module must implement run()')
