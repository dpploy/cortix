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
Cortix driver for guest modules.
Module developers must implement the public methods in this driver.
Ideally, this implementation should be minimal.
Developers should use this class to wrap their module (MyModule) implemented in a
file named my_module.py. This file will be placed inside the developer's module
directory which is pointed to in the Cortix config.xml file.
'''
#*************************************************************************
import os
import sys
import io
import time
import datetime
import logging

# uncomment
#from .my_module import MyModule
#*************************************************************************

class CortixDriverTemplate():
    '''
     Cortix driver for guest modules.
    '''

    def __init__(self,
                 slot_id,
                 input_full_path_file_name,
                 manifesto_full_path_file_name,
                 work_dir,
                 ports=list(),
                 cortix_start_time=0.0,
                 cortix_final_time=0.0,
                 cortix_time_step=0.0,
                 cortix_time_unit=None
                 ):

        # Sanity test
        assert isinstance(slot_id, int), '-> slot_id type %r is invalid.' % type(slot_id)
        assert isinstance( ports, list), '-> ports type %r is invalid.' % type(ports)
        assert len(ports) > 0
        assert isinstance(cortix_start_time, float), '-> time type %r is invalid.' % \
               type(cortix_start_time)
        assert isinstance(cortix_final_time, float), '-> time type %r is invalid.' % \
               type(cortix_final_time)
        assert isinstance(cortix_time_step, float), '-> time step type %r is invalid.' % \
               type(cortix_time_step)
        assert isinstance(cortix_time_unit, str), '-> time unit type %r is invalid.' % \
               type(cortix_time_unit)

        # Logging
        self.__log = logging.getLogger( 'launcher-mymodule' + str(slot_id) +
                                        '.cortixdriver')
        self.__log.info('initializing an object of CortixDriver()')

        # Guest library module: MyModule
        # uncomment
        # self.my_module = MyModule( slot_id, 
        #        input_full_path_file_name, manifesto_full_path_file_name, work_dir,
        #        ports,
        #        cortix_start_time, cortix_final_time, cortix_time_step, cortix_time_unit )

        self.__time_stamp = None  # temporary

        return
#---------------------- end def __init__():-------------------------------

    def call_ports(self, cortix_time=0.0):
        '''
        Call all ports at cortix_time
        '''

        self.__log_debug(cortix_time, 'call_ports')

        # uncomment
        # self.my_module.call_ports( cortix_time )

        self.__log_debug(cortix_time, 'call_ports')

        return
#---------------------- end def call_ports():-----------------------------

    def execute(self, cortix_time=0.0, timeStep=0.0):
        '''
        Evolve system from cortix_time to cortix_time + timeStep
        '''

        self.__log_debug(cortix_time, 'execute')

        # uncomment
        # self.my_module.execute( cortix_time, timeStep )

        self.__log_debug(cortix_time, 'execute')

        return
#---------------------- end def execute():--------------------------------

#*************************************************************************
# Private helper functions (internal use: __)

    def __log_debug(self, cortix_time=0.0, caller='null-function-name'):

        if self.__time_stamp is None:
            s = ''
            self.__log.debug(s)
            s = '=========================================================='
            self.__log.debug(s)
            s = 'CORTIX::DRIVER->***->DRIVER->***->DRIVER->***->DRIVER->***'
            self.__log.debug(s)
            s = '=========================================================='
            self.__log.debug(s)

            s = caller + '(' + str(round(cortix_time, 2)) + '[min]):'
            self.__log.debug(s)

            self.__time_stamp = time.time()

        else:

            end_time = time.time()

            s = caller + '(' + str(round(cortix_time, 2)) + '[min]): '
            m = 'CPU elapsed time (s): ' + \
                str(round(end_time - self.__time_stamp, 2))
            self.__log.debug(s + m)

            self.__time_stamp = None
            if caller == 'execute':
                s = ''
                self.__log.debug(s)

        return
#---------------------- end def __log_debug():----------------------------

#====================== end class CortixDriver: ==========================
