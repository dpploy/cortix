#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import os
import shutil
import logging
from mpi4py import MPI
from cortix.src.module import Module
from cortix.src.utils.cortix_units import Units
from cortix.src.utils.cortix_time import CortixTime

class Cortix:
    '''
    The main Cortix class definition.
    '''

    def __init__(self, work_dir="/tmp/"):
        self.work_dir = os.path.join(work_dir, 'cortix-wrk/')
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.size

        if self.rank == 0:
            # Create the work directory
            shutil.rmtree(self.work_dir, ignore_errors=True)
            os.mkdir(self.work_dir)

        # Setup the global logger
        self.__create_logger()

        # Simulation time parameters 
        self.start_time = CortixTime()
        self.evolve_time = CortixTime()
        self.time_step = CortixTime()

        self.modules = []

        self.log.info('Created Cortix object')

    def add_module(self, m):
        assert isinstance(m, Module), "m must be a module"
        if m not in self.modules:
            self.modules.append(m)
            m.rank = len(self.modules)

    def run(self):
        '''
        Run the Cortix simulation
        '''
        # Check for correct number of ranks
        assert self.size == len(self.modules) + 1, "Incorrect nprocs"

        # Run each module on its own rank 
        for mod in self.modules:
            if self.rank == mod.rank:
                self.log.info("Launching Module {} on rank {}".format(mod, self.rank))
                mod.run()

    def __create_logger(self):
        '''
        A helper function to setup the logging facility used in constructor
        '''
        self.log = logging.getLogger("cortix")
        self.log.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(self.work_dir + 'cortix.log')
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Formatter added to handlers
        fs = '[{}] %(asctime)s - %(name)s - %(levelname)s - %(message)s'.format(self.rank)
        formatter = logging.Formatter(fs)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # add handlers to logger
        self.log.addHandler(file_handler)
        self.log.addHandler(console_handler)

if __name__ == "__main__":
    c = Cortix()
