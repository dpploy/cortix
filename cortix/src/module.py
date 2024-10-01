#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import os
import pickle
import logging
from cortix.src.port import Port

class Module:
    """Cortix module super class.

    This class provides facilities for creating modules within the Cortix network.
    Cortix will map one object of this class to either a Multiprocessing or MPI
    process depending on the user's configuration.

    Note
    ----
    This class is to be inherited by every Cortix module.
    In order to execute, modules *must* override the `run` method, which will be
    executed during the simulation.

    """

    def __init__(self):
        """Module super class constructor.

        Note
        ----
        This constructor must be called explicitly in the constructor of every
        Cortix module like so:

            super().__init__()

        Attributes
        ----------
        name: str
            A name given to the instance. Default is the derived class name.
        port_names_expected: list(str), None
            A list of names of ports expected in the module. This will be compared
            to port names during runtime to check against the intended use of the
            module.
        state: any
            Any `pickle-able` data structure to be passed in a `multiprocessing.Queue`
            to the parent process or to be gathered in the root MPI process.
            Default is `None`.
        use_mpi: bool
            `True` for MPI, `False` for Multiprocessing
        use_multiprocessing: bool
            `False` for MPI, `True` for Multiprocessing
        ports: list(Port)
            A list of ports contained by the module
        id: int
            An integer set by the external network once a module is added to it.
            The `id` is the position of the module in the network list.
            Default: None.
        __network: Network
            An internal network inherited by the derived module for nested networks.

       """

        self.name = self.__class__.__name__
        self.port_names_expected = None
        self.state = None
        self.use_mpi = False
        self.use_multiprocessing = True
        self.ports = list()
        self.log = logging.getLogger('cortix')
        self.save = False

        self.id = None

        self.__network = None

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
            assert port in self.ports, 'Unknown port!'
        else:
            raise TypeError('port must be of Port or String type')

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

        for pti in self.ports:
            if pti.name == name:
                port = pti
                break

        if port is None:
            if self.port_names_expected:
                assert name in self.port_names_expected,\
                        'port name: {}, not expected by module: {}'.format(name, self)
            port = Port(name, self.use_mpi)
            self.ports.append(port)

        return port

    def __set_network(self, n):
        # Must be here to avoid infinite import loop
        from cortix.src.network import Network
        assert isinstance(n, Network)
        n.use_mpi = self.use_mpi
        n.use_multiprocessing = self.use_multiprocessing
        self.__network = n
    def __get_network(self):
        return self.__network
    network = property(__get_network, __set_network, None, None)

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

            if self.use_multiprocessing:
                try:
                    pickle.dumps(self.state)
                except pickle.PicklingError:
                    args[1].put((arg[0],None))
                else:
                    args[1].put((arg[0],self.state))

        at the bottom of the user defined `run()` function.

        Warning
        -------
        This function must be overridden by all Cortix modules

        Parameters
        ----------
        arg[0]: int
            Index of the state in the communication queue.

        arg[1]: multiprocessing.Queue
            When using the Python `multiprocessing` library `state_comm` must have
            the module's `self.state` in it. That is,
            `state_comm.put((idx_comm,self.state))` must be the last command in the
            method before `return`. In addition, self.state must be `pickle-able`.

        '''
        raise NotImplementedError('Module must implement run()')

    def run_and_save(self):

        self.run()

        if self.save:
            file_name = os.path.join('.ctx-saved', '{}_'.format(self.__class__.__name__))
            # Import where needed for no broken dependencies
            if self.use_mpi:
                from mpi4py import MPI
                file_name += str(MPI.COMM_WORLD.rank)
            else:
                file_name += str(os.getpid())
            file_name += '.pkl'

            self.ports = list() # reset ports since they can't be pickled
            self.log = None

            try:
                with open(file_name, 'wb') as fout:
                    pickle.dump(self, fout)
            except pickle.PicklingError:
                print('Unable to pickle {}!'.format(file_name))
