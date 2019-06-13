#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/cortix/blob/master/COPYRIGHT.txt
#
# Licensed under the University of Massachusetts Lowell LICENSE:
# https://github.com/dpploy/cortix/blob/master/LICENSE.txt

'''
The Cortix class definition.

Cortix: a program for system-level modules coupling, execution, and analysis.
'''
#*********************************************************************************
import os
import shutil
import logging
from cortix.src.utils.cortix_time import CortixTime
from cortix.src.utils.cortix_units import Units
from cortix.src.utils.set_logger_level import set_logger_level
#*********************************************************************************

class Cortix():
    '''
    The main Cortix class definition. This class encapsulates the
    concepts of simulations, tasks, and modules, for a given application providing
    the user with an interface to the simulations.
    '''

#*********************************************************************************
# Construction 
#*********************************************************************************

    def __init__(self, name, work_dir="/tmp/"):
        self.__name = name
        self.__work_dir = work_dir + self.__name + '-wrk/'

        # Create the work directory
        shutil.rmtree(self.__work_dir, ignore_errors=True)
        os.mkdir(self.__work_dir)

        # Setup the global logger
        self.__create_logger()

        # Simulation time parameters 
        self.start_time = CortixTime()
        self.evolve_time = CortixTime()
        self.time_step = CortixTime()

        self.__modules = list()

        self.__log.info('Created Cortix object %s %s', self.__name)
        self.__log.info(self.__get_splash(begin=True))

    def __del__(self):
        self.__log.info("Destroyed Cortix object: %s %s", self.__name, self.__get_splash(begin=False))

#*********************************************************************************
# Public member functions
#*********************************************************************************

    def add_module(self, m):
        assert(isinstance(s, Module), "m must be a module")
        self.__modules.append(m)

    def run(self, task_name=None):
        '''
        This method runs every simulation defined by the Cortix object. At the
        moment this is done one simulation at a time.
        '''
        pass
        return

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

    def __create_logging(self):
        '''
        A helper function to setup the logging facility used in self.__init__()
        '''

        self.__log = logging.getLogger("cortix")
        self.__log.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(self.__work_dir + 'cortix.log')
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)


        # Formatter added to handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # add handlers to logger
        self.__log.addHandler(file_handler)
        self.__log.addHandler(console_handler)
        self.__log.info('Created Cortix logger: %s', self.__name)
        self.__log.debug('Logger level: %s', logger_level)
        self.__log.debug('Logger file handler level: %s', file_handler_level)
        self.__log.debug('Logger console handler level: %s', console_handler_level)

        return

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

#======================= end class Cortix: =======================================
