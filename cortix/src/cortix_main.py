#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
# Licensed under the University of Massachusetts Lowell LICENSE:
# https://github.com/dpploy/cortix/blob/master/LICENSE.txt

import os
import shutil
import logging
from cortix.src.module import Module
from cortix.src.utils.cortix_units import Units
from cortix.src.utils.cortix_time import CortixTime

class Cortix:
    '''
    The main Cortix class definition.
    '''

    def __init__(self, work_dir="/tmp/"):
        self.work_dir = os.path.join(work_dir, 'cortix-wrk/')

        # Create the work directory
        shutil.rmtree(self.work_dir, ignore_errors=True)
        os.mkdir(self.work_dir)

        # Setup the global logger
        self.__create_logger()

        # Simulation time parameters 
        self.start_time = CortixTime()
        self.evolve_time = CortixTime()
        self.time_step = CortixTime()

        self.modules = list()

        self.log.info('Created Cortix object')

    def add_module(self, m):
        assert isinstance(m, Module), "m must be a module"
        if m not in self.modules:
            self.modules.append(m)

    def run(self):
        '''
        Run the simulation
        '''
        pass

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
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # add handlers to logger
        self.log.addHandler(file_handler)
        self.log.addHandler(console_handler)

if __name__ == "__main__":
    c = Cortix("test")
