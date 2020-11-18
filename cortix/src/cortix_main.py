#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import os
import shutil
import logging
import time
import datetime

from cortix.src.network import Network

class Cortix:
    """Cortix main class definition.

    The typical Cortix run file workflow:

    1. Create the `Cortix` object
    2. Create tne (nested) network of modules
    3. Run and close `Cortix`

    """

    def __init__(self, use_mpi=False, splash=False, log_filename='cortix'):
        """Construct a Cortix simulation object.

        Parameters
        ----------
        use_mpi: bool
            True for MPI, False for multiprocessing.
        splash: bool
            Show the Cortix splash image.

        Attributes
        ----------
        network: Network
             A network of modules and their connectivity.
        use_mpi: bool
            `True` for MPI, `False` for Multiprocessing.
        use_multiprocessing: bool
            `False` for MPI, `True` for Multiprocessing.
        splash: bool
            Show the Cortix splash image.
        comm: mpi4py.MPI.Intracomm
            MPI.COMM_WORLD (if using MPI else None).
        rank: int
            The current MPI rank (if using MPI else None).
        size: int
            size of the group associated with MPI.COMM_WORLD.

        """
        self.use_mpi = use_mpi
        self.use_multiprocessing = not use_mpi
        self.comm = None
        self.rank = None
        self.size = None

        self.splash = splash

        self.__network = None
        self.log_filename = log_filename
        # Fall back to multiprocessing if mpi4py is not available
        if self.use_mpi:
            try:
                from mpi4py import MPI
                self.comm = MPI.COMM_WORLD
                self.rank = self.comm.Get_rank()
                self.size = self.comm.size
            except ImportError:
                self.use_mpi = False

        # Setup the global logger
        self.__create_logger()

        # Done
        if self.rank == 0 or self.use_multiprocessing:

            if self.splash:
                self.log.info('Created Cortix object %s', self.__get_splash(begin=True))
            else:
                self.log.info('Created Cortix object')

            # Initialize all date and timings
            self.wall_clock_time_start = time.time()
            self.wall_clock_time_end = self.wall_clock_time_start
            self.end_run_date = datetime.datetime.today().strftime('%d%b%y %H:%M:%S')

            shutil.rmtree('.ctx-saved', ignore_errors=True)

    def __set_network(self, n):
        assert isinstance(n, Network)
        n.use_mpi = self.use_mpi
        n.use_multiprocessing = self.use_multiprocessing
        n.rank = self.rank
        n.size = self.size
        n.comm = self.comm
        self.__network = n
    def __get_network(self):
        return self.__network
    network = property(__get_network, __set_network, None, None)

    def run(self, save=False):
        """Run the Cortix network simulation.
        """

        self.__network._Network__run(save)

        if self.rank == 0 or self.use_multiprocessing:
            self.wall_clock_time_end = time.time()
            self.log.info('run()::Elapsed wall clock time [s]: '+
                          str(round(self.wall_clock_time_end-self.wall_clock_time_start, 2)))

    def close(self):
        """Closes the cortix object properly before destruction.

        User is strongly advised to call this method at the end of the run file otherwise
        timings will not be recorded.

        """
        # Sync here before close
        if self.use_mpi:
            self.comm.Barrier()

        if self.rank == 0 or self.use_multiprocessing:

            if self.splash:
                self.log.info('Closed Cortix object.'+self.__get_splash(end=True))
            else:
                self.log.info('Closed Cortix object.')

            self.wall_clock_time_end = time.time()

            self.log.info('close()::Elapsed wall clock time [s]: '+
                          str(round(self.wall_clock_time_end-self.wall_clock_time_start, 2)))
        return

    def __create_logger(self):
        """A helper function to setup the logging facility."""

        # File removal
        if self.rank == 0 or self.use_multiprocessing:
            if os.path.isfile('cortix.log'):
                os.remove('cortix.log')

        # Sync here to allow for file removal
        if self.use_mpi:
            self.comm.Barrier()

        self.log = logging.getLogger(self.log_filename)

        self.log.setLevel(logging.DEBUG)
        #10/8/19 Added check to see if log hander exsists before creating new ones
        if not self.log.hasHandlers():
            file_handler = logging.FileHandler(self.log_filename+'.log')
            file_handler.setLevel(logging.DEBUG)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)

            # Formatter added to handlers
            if self.use_mpi:
                fs = '[rank:{}] %(asctime)s - %(name)s - %(levelname)s - %(message)s'.format(self.rank)
            else:

                fs = "[{}] %(asctime)s - %(name)s - %(levelname)s - %(message)s".format(os.getpid())

            formatter = logging.Formatter(fs)
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Add handlers to logger
            self.log.addHandler(file_handler)
            self.log.addHandler(console_handler)

        return

    def __get_splash(self, begin=None, end=None):
        '''Returns the Cortix splash logo.

        Note
        ----
        Call this internal method with one argument only. Either `begin=True` or
        `end=True`.

        Parameters
        ----------
        begin: bool
            True for the beginning message, false for the ending.

        Returns
        -------
        splash: str
            The Cortix splash logo.

        '''

        assert begin is None or end is None
        if begin:
            end = False
        elif end:
            begin = False


        splash = \
        '_____________________________________________________________________________\n'+\
        '      ...                                        s       .     (TAAG Fraktur)\n'+\
        '   xH88"`~ .x8X                                 :8      @88>\n'+\
        ' :8888   .f"8888Hf        u.      .u    .      .88      %8P      uL   ..\n'+\
        ':8888>  X8L  ^""`   ...ue888b   .d88B :@8c    :888ooo    .     .@88b  @88R\n'+\
        'X8888  X888h        888R Y888r ="8888f8888r -*8888888  .@88u  ""Y888k/"*P\n'+\
        '88888  !88888.      888R I888>   4888>"88"    8888    ''888E`    Y888L\n'+\
        '88888   %88888      888R I888>   4888> "      8888      888E      8888\n'+\
        '88888 `> `8888>     888R I888>   4888>        8888      888E      `888N\n'+\
        '`8888L %  ?888   ! u8888cJ888   .d888L .+    .8888Lu=   888E   .u./"888&\n'+\
        ' `8888  `-*""   /   "*888*P"    ^"8888*"     ^%888*     888&  d888" Y888*"\n'+\
        '   "888.      :"      "Y"          "Y"         "Y"      R888" ` "Y   Y"\n'+\
        '     `""***~"`                                           ""\n'+\
        '                             https://cortix.org                              \n'+\
        '_____________________________________________________________________________'

        if begin:
            message = \
            '\n_____________________________________________________________________________\n'+\
            '                             L A U N C H I N G                               \n'

        else:
            message = \
            '\n_____________________________________________________________________________\n'+\
            '                           T E R M I N A T I N G                             \n'

        return message + splash

    def __del__(self):
        """Destructs a Cortix simulation object.

        Warning
        -------
        By the time the body of this function is executed, the machinery of
        variables may have been deleted already. For example, `logging` is no longer
        there; do the least amount of work here.

        """

        pass

if __name__ == '__main__':
    c = Cortix()
