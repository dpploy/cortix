# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/...
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/COPYRIGHT
#
# Licensed under the GNU General Public License v. 3, please see LICENSE file.
# https://www.gnu.org/licenses/gpl-3.0.txt
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
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
    """
    This class defines the implementation of a Task in the Cortix Project.
    A Task is a portion of work done by a simulation.
    """

    def __init__(self, parent_work_dir=None, task_config_node=ConfigTree()):

        assert isinstance(parent_work_dir, str), '-> parent_work_dir invalid.'

        # Inherit a configuration tree
        assert isinstance(task_config_node, ConfigTree), \
        '-> task_config_node not a ConfigTree.'
        self.config_node = task_config_node

        # Read the simulation name
        self.name = self.config_node.get_node_name()

        # Set the work directory (previously created)
        assert os.path.isdir(parent_work_dir), 'work directory not available.'
        self.work_dir = parent_work_dir + 'task_' + self.name + '/'
        os.system('mkdir -p ' + self.work_dir)

        # Create the logging facility for the object
        node = task_config_node.get_sub_node('logger')
        logger_name = self.name
        self.log = logging.getLogger(logger_name)
        self.log.setLevel(logging.NOTSET)

        logger_level = node.get('level').strip()
        self.log = set_logger_level(self.log, logger_name, logger_level)

        file_handle = logging.FileHandler(self.work_dir + 'task.log')
        file_handle.setLevel(logging.NOTSET)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.NOTSET)

        for child in node:
            if child.tag == 'file_handler':
                # file handler
                file_handle_level = child.get('level').strip()
                file_handle = set_logger_level(file_handle, logger_name, \
                                               file_handle_level)
            if child.tag == 'console_handler':
                # console handler
                console_handle_level = child.get('level').strip()
                console_handler = set_logger_level(console_handler,\
                                                   logger_name, console_handle_level)

        # formatter added to handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handle.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # add handlers to logger
        self.log.addHandler(file_handle)
        self.log.addHandler(console_handler)

        self.log.info('created logger: %s', self.name)
        self.log.debug('logger level: %s', logger_level)
        self.log.debug('logger file handler level: %s', file_handle_level)
        self.log.debug('logger console handler level: %s', console_handle_level)

        self.start_time = self.evolve_time = self.time_step = 0.0
        self.start_time_unit = 'null-start_time_unit'
        self.evolve_time_unit = 'null-evolve_time_unit'
        self.time_step_unit = 'null-time_step_unit'
        self.runtime_cortix_param_file = 'null-runtime_cortix_param_file'

        self.log.debug('start __init__()')
        for child in self.config_node.get_node_children():
            (elem, tag, items, text) = child
            if tag == 'start_time':
                for (key, value) in items:
                    if key == 'unit':
                        self.start_time_unit = value
                self.start_time = float(text.strip())

            if tag == 'evolve_time':
                for (key, value) in items:
                    if key == 'unit':
                        self.evolve_time_unit = value
                self.evolve_time = float(text.strip())

            if tag == 'time_step':
                for (key, value) in items:
                    if key == 'unit':
                        self.time_step_unit = value
                self.time_step = float(text.strip())

        if self.start_time_unit == 'null-start_time_unit':
            self.start_time_unit = self.evolve_time_unit
        assert self.evolve_time_unit != 'null-evolve_time_unit', \
        'invalid time unit = %r' %(self.evolve_time_unit)

        self.log.debug('start_time value = %s', str(self.start_time))
        self.log.debug('start_time unit  = %s', str(self.start_time_unit))
        self.log.debug('evolve_time value = %s', str(self.evolve_time))
        self.log.debug('evolve_time unit  = %s', str(self.evolve_time_unit))
        self.log.debug('end __init__()')
        self.log.info('created task: %s', self.name)
#---------------------- end def __init__():---------------------------------------

    def execute(self, application):
        """
        This method is used to execute (accomplish) the given task.
        """
        network = application.get_network(self.name)
        runtime_status_files = dict()
        for slot_name in network.get_slot_names():
            module_name = slot_name.split('_')[0]
            slot_id = int(slot_name.split('_')[1])
            mod = application.get_module(module_name)
            param_file = self.runtime_cortix_param_file
            comm_file = network.get_runtime_cortix_comm_file(slot_name)
            # Run module in the slot
            status_file = mod.execute(slot_id, param_file, comm_file)
            assert status_file is not None, 'module launching failed.'
            runtime_status_files[slot_name] = status_file

        # monitor runtime status
        status = 'running'
        while status == 'running':
            time.sleep(10)  # hard coded; fix me.
            (status, slot_names) = self.__get_runtime_status(runtime_status_files)
            self.log.info('runtime status: %s; module slots running: %s', status, \
                          str(slot_names))
#---------------------- end def execute():---------------------------------------

    def get_name(self):
        """
        Returns the name of the task.
        """

        return self.name
#---------------------- end def get_name():---------------------------------------

    def get_work_dir(self):
        """
        Returns the working directory
        of the task specification.
        """

        return self.work_dir
#---------------------- end def get_work_dir():-----------------------------------

    def get_start_time(self):
        """
        Returns the task's initial time
        """

        return self.start_time
#---------------------- end def get_start_time():---------------------------------

    def get_start_time_unit(self):
        """
        Returns the unit of the task's initial time
        """

        return self.start_time_unit
#---------------------- end def get_start_time_unit():----------------------------

    def get_evolve_time(self):
        """
        Returns the tasks's final time
        """

        return self.evolve_time
#---------------------- end def get_evolve_time():--------------------------------

    def get_evolve_time_unit(self):
        """
        Returns the unit of the task's final time.
        """

        return self.evolve_time_unit
#---------------------- end def get_evolve_time_unit():---------------------------

    def get_time_step(self):
        """
        Returns the magnitude of an incremental step
        in the task's time.
        """

        return self.time_step
#---------------------- end def get_time_step():----------------------------------

    def get_time_step_unit(self):
        """
        Returns the unit of the tasks's time step
        """

        return self.time_step_unit
#---------------------- end def get_time_step_unit():-----------------------------

    def set_runtime_cortix_param_file(self, full_path):
        """
        Sets the task config file to the specified file.
        """

        self.runtime_cortix_param_file = full_path
#---------------------- end def set_runtime_cortix_param_file():------------------

    def get_runtime_cortix_param_file(self):
        """
        Returns the taks's config file.
        """

        return self.runtime_cortix_param_file
#---------------------- end def get_runtime_cortix_param_file():------------------

    def __del__(self):
        self.log.info('destroyed task: %s', self.name)
#---------------------- end def __del__():----------------------------------------

#*********************************************************************************
# Private helper functions (internal use: __)

    def __get_runtime_status(self, runtime_status_files):
        """
        Helper funcion for montioring the status of the task.
        """

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
#---------------------- end def __get_runtime_status():---------------------------


#====================== end class Task: ==========================================

# Unit testing. Usage: -> python task.py
if __name__ == "__main__":
    print('Unit testing for Task')
