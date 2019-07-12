#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import os
import shutil
import logging
import datetime

from multiprocessing import Process
from cortix.src.module import Module
from cortix.src.utils.cortix_units import Units
from cortix.src.utils.cortix_time import CortixTime

class Cortix:
    '''
    The main Cortix class definition.
    '''

    def __init__(self, use_mpi=False):
        self.use_mpi = use_mpi

        if self.use_mpi:
            from mpi4py import MPI
            self.comm = MPI.COMM_WORLD
            self.rank = self.comm.Get_rank()
            self.size = self.comm.size

        # Setup the global logger
        self.__create_logger()

        # Modules storage
        self.modules = list()

        # Done
        if (self.use_mpi and self.rank == 0) or not self.use_mpi:
            self.log.info('Created Cortix object %s', self.__get_splash(begin=True))

        return

    def __del__(self):

        if self.use_mpi and self.rank == 0 or not self.use_mpi:
                print('\n'+self.end_of_run_date+': Destroyed Cortix object '+
                        self.__get_splash(begin=False))

        return

    def add_module(self, m):
        assert isinstance(m, Module), "m must be a module"
        if m not in self.modules:
            self.modules.append(m)
            if self.use_mpi:
                m.rank = len(self.modules)
                for port in m.ports:
                    port.rank = m.rank

    def run(self):
        '''
        Run the Cortix simulation
        '''
        if self.use_mpi:
            assert self.size == len(self.modules) + 1, "Incorrect number of \
            processes (Required {}, got {})".format(len(self.modules) + 1, self.size)

        # Set port ids
        i = 0
        for mod in self.modules:
            for port in mod.ports:
                port.use_mpi = self.use_mpi
                port.id = i
                i += 1

        for mod in self.modules:
            if not self.use_mpi:
                processes = list()
                self.log.info('Launching Module {}'.format(mod))
                p = Process(target=mod.run)
                processes.append(p)
                p.start()
            elif self.rank == mod.rank:
                self.log.info('Launching Module {} on rank {}'.format(mod, self.rank))
                mod.run()

        if self.use_mpi:
            self.comm.barrier()
        else:
            [p.join() for p in processes]

        self.end_of_run_date = datetime.datetime.today().strftime("%d%b%y %H:%M:%S")

    def __create_logger(self):
        '''
        A helper function to setup the logging facility used in the constructor.
        '''

        self.log = logging.getLogger('cortix')
        self.log.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler('cortix.log')
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Formatter added to handlers
        if self.use_mpi:
            fs = '[rank:{}] %(asctime)s - %(name)s - %(levelname)s - %(message)s'.format(self.rank)
        else:
            fs = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        formatter = logging.Formatter(fs)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        self.log.addHandler(file_handler)
        self.log.addHandler(console_handler)

    def __get_splash(self, begin=True):

        splash = \
        '_____________________________________________________________________________\n'+\
        '      ...                                        s       .\n'+\
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
        '                             https://cortix.org                (TAAG Fraktur)\n'+\
        '_____________________________________________________________________________'

        if begin == True:
            message = \
            '\n_____________________________________________________________________________\n'+\
            '                             L A U N C H I N G                               \n'

        else:
            message = \
            '\n_____________________________________________________________________________\n'+\
            '                           T E R M I N A T I N G                             \n'

        return message+splash

if __name__ == '__main__':
    c = Cortix()
