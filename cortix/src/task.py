#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/cortix
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/cortix/blob/master/COPYRIGHT.txt
#
# Licensed under the GNU General Public License v. 3, please see LICENSE file.
# https://www.gnu.org/licenses/gpl-3.0.txt
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules coupling, execution, and analysis.
"""
#*********************************************************************************
import os
import time
import logging
from xml.etree.cElementTree import ElementTree
from cortix.src.utils.configtree import ConfigTree
from cortix.src.utils.set_logger_level import set_logger_level
#*********************************************************************************

class Task:
    '''
    A Task is work done by a Simulation handled by Cortix.
    A Task will use a given Application.
    '''

    def __init__(self, parent_work_dir=None, task_config_node=ConfigTree()):

        assert isinstance(parent_work_dir, str), '-> parent_work_dir invalid.'

        # Inherit a configuration tree
        assert isinstance(task_config_node, ConfigTree), \
            '-> task_config_node not a ConfigTree: %r.' % type(task_config_node)
        self.__config_node = task_config_node

        # Read the task name
        self.__name = self.__config_node.get_node_name()

        # Set the work directory (previously created)
        assert os.path.isdir(parent_work_dir), 'work directory not available.'
        self.__work_dir = parent_work_dir + 'task_' + self.__name + '/'
        os.system('mkdir -p ' + self.__work_dir)

        # Create the logging facility for the object
        node = task_config_node.get_sub_node('logger')
        logger_name = 'task:'+self.__name
        self.__log = logging.getLogger(logger_name)
        self.__log.setLevel(logging.NOTSET)

        logger_level = node.get('level').strip()
        self.__log = set_logger_level(self.__log, logger_name, logger_level)

        file_handle = logging.FileHandler(self.__work_dir + 'task.log')
        file_handle.setLevel(logging.NOTSET)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.NOTSET)

        for child in node:
            if child.tag == 'file_handler':
                # file handler
                file_handle_level = child.get('level').strip()
                file_handle = set_logger_level(file_handle, logger_name,
                                               file_handle_level)
            if child.tag == 'console_handler':
                # console handler
                console_handle_level = child.get('level').strip()
                console_handler = set_logger_level(console_handler,
                                                   logger_name, console_handle_level)

        # formatter added to handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handle.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # add handlers to logger
        self.__log.addHandler(file_handle)
        self.__log.addHandler(console_handler)

        self.__log.info('created logger: %s', self.__name)
        self.__log.debug('logger level: %s', logger_level)
        self.__log.debug('logger file handler level: %s', file_handle_level)
        self.__log.debug(
            'logger console handler level: %s',
            console_handle_level)

        self.__start_time = self.__evolve_time = self.__time_step = 0.0
        self.__start_time_unit = 'null-start_time_unit'
        self.__evolve_time_unit = 'null-evolve_time_unit'
        self.__time_step_unit = 'null-time_step_unit'
        self.__runtime_cortix_param_file = 'null-runtime_cortix_param_file'

        self.__log.debug('start __init__()')
        for child in self.__config_node.get_node_children():
            (elem, tag, items, text) = child
            if tag == 'start_time':
                for (key, value) in items:
                    if key == 'unit':
                        self.__start_time_unit = value
                self.__start_time = float(text.strip())

            if tag == 'evolve_time':
                for (key, value) in items:
                    if key == 'unit':
                        self.__evolve_time_unit = value
                self.__evolve_time = float(text.strip())

            if tag == 'time_step':
                for (key, value) in items:
                    if key == 'unit':
                        self.__time_step_unit = value
                self.__time_step = float(text.strip())

        if self.__start_time_unit == 'null-start_time_unit':
            self.__start_time_unit = self.__evolve_time_unit
        assert self.__evolve_time_unit != 'null-evolve_time_unit', \
            'invalid time unit = %r' % (self.__evolve_time_unit)

        self.__log.debug('start_time value = %s', str(self.__start_time))
        self.__log.debug('start_time unit  = %s', str(self.__start_time_unit))
        self.__log.debug('evolve_time value = %s', str(self.__evolve_time))
        self.__log.debug('evolve_time unit  = %s', str(self.__evolve_time_unit))
        self.__log.debug('end __init__()')
        self.__log.info('created task: %s', self.__name)
#----------------------- end def __init__():--------------------------------------

    def execute(self, application):
        '''
        This method is used to execute (accomplish) the given task.
        '''
        network = application.get_network(self.__name)
        runtime_status_files = dict()

        for slot_name in network.slot_names:

            module_name = '_'.join( slot_name.split('_')[:-1] )
            slot_id = int(slot_name.split('_')[-1])

            module     = application.get_module(module_name)
            param_file = self.__runtime_cortix_param_file
            comm_file  = network.get_runtime_cortix_comm_file(slot_name)

            # Run module in the slot
            self.__log.info('call execute on module: %s:%s',module_name,slot_id)

            status_file = module.execute(slot_id, param_file, comm_file)

            assert status_file is not None, \
                   'module launching failed; module name: %r' % module_name

            runtime_status_files[slot_name] = status_file

        # monitor runtime status
        status = 'running'
        while status == 'running':
            time.sleep(5)  # hard coded; fix me.
            (status, slot_names) = self.__get_runtime_status(runtime_status_files)
            self.__log.info('runtime status: %s; module slots running: %s', status,
                          str(slot_names))
#----------------------- end def execute():---------------------------------------

    def __get_name(self):
        '''
        `str`:Task name
        '''

        return self.__name
    name = property(__get_name, None, None, None)
#----------------------- end def get_name():--------------------------------------

    def __get_work_dir(self):
        '''
        `str`:Working directory of task specification
        '''

        return self.__work_dir
    work_dir = property(__get_work_dir, None, None, None)
#----------------------- end def get_work_dir():----------------------------------

    def __get_start_time(self):
        '''
        `float`:Task initial time
        '''

        return self.__start_time
    start_time = property(__get_start_time, None, None, None)
#----------------------- end def get_start_time():--------------------------------

    def __get_start_time_unit(self):
        '''
        `str`:Task initial time unit
        '''

        return self.__start_time_unit
    start_time_unit = property(__get_start_time_unit, None, None, None)
#----------------------- end def get_start_time_unit():---------------------------

    def __get_evolve_time(self):
        '''
        `float`:Task final time
        '''

        return self.__evolve_time
    evolve_time = property(__get_evolve_time, None, None, None)
#----------------------- end def get_evolve_time():-------------------------------

    def __get_evolve_time_unit(self):
        '''
        `str`:Task final time unit
        '''

        return self.__evolve_time_unit
    evolve_time_unit = property(__get_evolve_time_unit, None, None, None)
#----------------------- end def get_evolve_time_unit():--------------------------

    def __get_time_step(self):
        '''
        `float`:Magnitude of incremental step in the task's time
        '''

        return self.__time_step
    time_step = property(__get_time_step, None, None, None)
#----------------------- end def get_time_step():---------------------------------

    def __get_time_step_unit(self):
        '''
        `str`:Time step unit
        '''

        return self.__time_step_unit
    time_step_unit = property(__get_time_step_unit, None, None, None)
#----------------------- end def get_time_step_unit():----------------------------

    def set_runtime_cortix_param_file(self, full_path):
        '''
        Sets the task config file to the specified file.
        '''

        self.__runtime_cortix_param_file = full_path
#----------------------- end def set_runtime_cortix_param_file():-----------------

    def __get_runtime_cortix_param_file(self):
        '''
        `str`:Task's config file
        '''

        return self.__runtime_cortix_param_file
    runtime_cortix_param_file = property(__get_runtime_cortix_param_file, set_runtime_cortix_param_file, None, None)
#----------------------- end def get_runtime_cortix_param_file():-----------------

    def __del__(self):
        self.__log.info('destroyed task: %s', self.__name)
#----------------------- end def __del__():---------------------------------------

#*********************************************************************************
# Private helper functions (internal use: __)

    def __get_runtime_status(self, runtime_status_files):
        '''
        Helper funcion for montioring the status of the task.
        It reads the status files of all modules and reports which ones are still
        running.
        '''

        task_status = 'finished'
        running_module_slots = list()

        for (slot_name, status_file) in runtime_status_files.items():
            if not os.path.isfile(status_file):
                time.sleep(0.1)

            assert os.path.isfile(status_file), 'runtime status file %r not found.' \
                % status_file

            tree = ElementTree()
            tree.parse(status_file)
            status_file_xml_root_node = tree.getroot()
            node = status_file_xml_root_node.find('status')

            status = node.text.strip()

            if status == 'running':
                task_status = 'running'
                running_module_slots.append(slot_name)

        return (task_status, running_module_slots)
#----------------------- end def __get_runtime_status():--------------------------


#======================= end class Task: =========================================
