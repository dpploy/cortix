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
Simulation class of Cortix.

Cortix: a program for system-level modules coupling, execution, and analysis.
"""
#*********************************************************************************
import os
import logging
from cortix.src.utils.configtree       import ConfigTree
from cortix.src.utils.set_logger_level import set_logger_level

from cortix.src.task        import Task
from cortix.src.application import Application
#*********************************************************************************

class Simulation:
    '''
    Cortix Simulation element as defined in the Cortix config.
    '''

    def __init__(self, parent_work_dir=None, sim_config_node=ConfigTree()):
        assert isinstance(parent_work_dir, str), '-> parentWorkDir invalid.'

        # Inherit a configuration tree
        assert isinstance(
            sim_config_node, ConfigTree), '-> sim_config_node invalid.'
        self.__config_node = sim_config_node

        # Read the simulation name
        self.__name = sim_config_node.get_node_name()

        # Create the cortix/simulation work directory
        self.__work_dir = parent_work_dir + 'sim_' + self.__name + '/'

        os.system('mkdir -p ' + self.__work_dir)

        # Create the logging facility for each object
        node = sim_config_node.get_sub_node("logger")
        logger_name = 'sim:' + self.__name 
        self.__log = logging.getLogger(logger_name)
        self.__log.setLevel(logging.NOTSET)

        logger_level = node.get('level').strip()
        self.__log = set_logger_level(self.__log, logger_name, logger_level)

        file_handler = logging.FileHandler(self.__work_dir + 'sim.log')
        file_handler.setLevel(logging.NOTSET)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.NOTSET)

        for child in node:
            if child.tag == "file_handler":
                file_handler_level = child.get("level").strip()
                file_handler = set_logger_level(file_handler, logger_name,
                                                file_handler_level)

            if child.tag == 'console_handler':
                console_handler_level = child.get('level').strip()
                console_handler = set_logger_level(console_handler, logger_name,
                                                   console_handler_level)

        # formatter added to handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # add handlers to logger
        self.__log.addHandler(file_handler)
        self.__log.addHandler(console_handler)

        self.__log.info("created Simulation logger: %s", self.__name)
        self.__log.debug("'logger level: %s", logger_level)
        self.__log.debug("logger file handler level: %s", file_handler_level)
        self.__log.debug(
            "logger console handler level: %s",
            console_handler_level)

        for app_node in self.__config_node.get_all_sub_nodes("application"):
            app_config_node = ConfigTree(app_node)
            assert app_config_node.get_node_name() == app_node.get("name"), \
                "check failed"

            # Create the application for this simulation
            self.__application = Application(self.__work_dir, app_config_node)

            self.__log.debug("created application: %s", app_node.get('name'))

        # Stores the task(s) created by the execute method
        self.__tasks = list()
        self.__log.info("created simulation: %s", self.__name)
#----------------------- end def __init__():--------------------------------------

    def execute(self, task_name=None):
        '''
        This method allows for the execution of a simulation by executing each
        task, if any. Execution proceeds one task at a time.
        '''
        self.__log.debug("prepare to execute(%s)", task_name)

        if task_name is not None:

            # Create the task object for each task in this simulation
            self.__setup_task(task_name)

            for task in self.__tasks:

                if task.name == task_name:

                    self.__log.debug("call execute(%s)", task_name)

                    task.execute(self.__application)

                    self.__log.debug(
                        'called task.execute() on task %s', task_name)

        self.__log.debug("end execute(%s)", task_name)
#----------------------- end def execute():---------------------------------------

    def __del__(self):

        self.__log.info("destroyed simulation: %s", self.__name)
#----------------------- end def __del__():---------------------------------------

#*********************************************************************************
# Private helper functions (internal use: __)

    def __setup_task(self, task_name):
        '''
        This is a helper function used by the execute() method.
        It sets up the set of tasks defined in the Cortix config for a simulation.
        '''

        self.__log.debug('start __setup_task(%s)', task_name)
        task = None

        for task_node in self.__config_node.get_all_sub_nodes('task'):
            if task_node.get('name') != task_name:
                continue

            task_config_node = ConfigTree(task_node)

            # create task
            task = Task(self.__work_dir, task_config_node)

            self.__tasks.append(task)

            self.__log.debug("appended task: %s", task_node.get("name"))

        if task is None:
            self.__log.debug('no task to exectute; done here.')
            self.__log.debug('end __setup_task(%s)', task_name)
            return

        networks = self.__application.networks

        # create subdirectory with task name
        task_name = task.name
        task_work_dir = task.work_dir
        assert os.path.isdir(task_work_dir), "directory %r invalid." % task_work_dir

        # set the parameters for the task in the cortix param file
        task_file = task_work_dir + 'cortix-param.xml'

        fout = open(task_file, 'w')
        fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        fout.write('<!-- Written by Simulation::__setup_task() -->\n')
        fout.write('<cortix_param>\n')

        start_time = task.start_time
        start_time_unit = task.start_time_unit
        fout.write('<start_time unit="' + start_time_unit + '"' + '>' +
                           str(start_time) + '</start_time>\n')

        evolve_time = task.evolve_time
        evolve_time_unit = task.evolve_time_unit
        fout.write('<evolve_time unit="' + evolve_time_unit + '"' + '>' +
                           str(evolve_time) + '</evolve_time>\n')

        time_step = task.time_step
        time_step_unit = task.time_step_unit
        fout.write('<time_step unit="' + time_step_unit + '"' + '>' +
                           str(time_step) + '</time_step>\n')

        fout.write('</cortix_param>')
        fout.close()

        task.set_runtime_cortix_param_file(task_file)

        # Using the tasks and network create the runtime module directories and comm
        # files
        for net in networks:
  
            if net.name.strip() != task_name.strip():
                s = '__setup_task():: net name: ' + \
                    net.name + ' not equal to task name: ' + task_name + '; ignored.'
                self.__log.warn(s)

            if net.name.strip() == task_name.strip():  # net and task names must match

                connect = net.connectivity
                to_module_to_port_visited = dict()

                for con in connect:
                    # Start with the ports that will function as a provide port or
                    # input port
                    to_module_slot = con['toModuleSlot']
                    to_port = con['toPort']

                    if to_module_slot not in to_module_to_port_visited.keys():
                        to_module_to_port_visited[to_module_slot] = list()

                    to_module_name = '_'.join( to_module_slot.split('_')[:-1] )
                    to_module = self.__application.get_module(to_module_name)

                    assert to_module is not None, \
                        'module %r does not exist in application' % to_module_name

                    assert to_module.has_port_name(to_port), \
                        'module %r has no port %r.' % (
                            to_module.name, to_port)

                    assert to_module.get_port_type(to_port) is not None,\
                        'network name: %r, module name: %r, to_port: %r port type \
                    invalid %r' % (net.name, to_module.name, to_port,
                                   type(to_module.get_port_type(to_port)))

                    to_module_slot_work_dir = task_work_dir + to_module_slot + '/'

                    if to_module.get_port_type(to_port) != 'input':
                        assert to_module.get_port_type(to_port) == 'provide', \
                            'port type %r invalid. Module %r, port %r' \
                            % (to_module.get_port_type(to_port), to_module.name,
                               to_port)

                    # "to" is who receives the "call", hence the provider
                    to_module_slot_comm_file = to_module_slot_work_dir + \
                        'cortix-comm.xml'

                    if not os.path.isdir(to_module_slot_work_dir):
                        os.system('mkdir -p ' + to_module_slot_work_dir)

                    if not os.path.isfile(to_module_slot_comm_file):
                        fout = open(to_module_slot_comm_file,'w')
                        fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                        fout.write('<!-- Written by Simulation::__setup_task() -->\n')
                        fout.write('<cortix_comm>\n')

                    if to_port not in to_module_to_port_visited[to_module_slot]:
                        fout = open(to_module_slot_comm_file,'a')
                        # this is the cortix info for modules providing data
                        to_port_mode = to_module.get_port_mode(to_port)
                        if to_port_mode.split('.')[0] == 'file':
                            ext = to_port_mode.split('.')[1]
                            log_str = '<port name="' + to_port + '" type="provide" file="'\
                                      + to_module_slot_work_dir + to_port + '.' + ext + '"/>\n'
                        elif to_port_mode == 'directory':
                            log_str = '<port name="' + to_port +\
                                      '" type="provide" directory="' +\
                                      to_module_slot_work_dir + to_port + '"/>\n'
                        else:
                            assert False, 'invalid port mode. fatal.'

                        fout.write(log_str)
                        fout.close()
                        to_module_to_port_visited[to_module_slot].append(
                            to_port)

                    debug_str = '__setup_task():: comm module: ' + to_module_slot + \
                                '; network: ' + task_name + ' ' + log_str
                    self.__log.debug(debug_str)

                    # register the cortix-comm file for the network
                    net.set_runtime_cortix_comm_file(to_module_slot,
                                                     to_module_slot_comm_file)

                    # Now do the ports that will function as use ports or
                    # output ports
                    from_module_slot = con['fromModuleSlot']
                    from_port = con['fromPort']
                    from_module_name = '_'.join( from_module_slot.split('_')[:-1] )
                    from_module = self.__application.get_module(from_module_name)

                    assert from_module.has_port_name(from_port), \
                        'module %r has no port %r' % (
                            from_module_name, from_port)

                    assert from_module.get_port_type(from_port) is not None, \
                        'network name: %r, module name: %r, from_port: %r port type invalid %r'\
                        % (net.name, from_module.name, from_port,
                           type(from_module.get_port_type(from_port)))

                    from_module_slot_work_dir = task_work_dir + from_module_slot + '/'

                    if from_module.get_port_type(from_port) != 'output':
                        assert from_module.get_port_type(from_port) == 'use', \
                            'port type %r invalid. Module %r, port %r' % \
                            (from_module.get_port_type(from_port),
                             from_module.name, from_port)

                        # "from" is who makes the "call", hence the user
                        from_module_slot_comm_file = from_module_slot_work_dir + \
                            'cortix-comm.xml'

                        if not os.path.isdir(from_module_slot_work_dir):
                            os.system('mkdir -p ' + from_module_slot_work_dir)

                        if not os.path.isfile(from_module_slot_comm_file):
                            fout = open(from_module_slot_comm_file,'w')
                            fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                            fout.write('<!-- Written by Simulation::__setup_task() -->\n')
                            fout.write('<cortix_comm>\n')
                            fout.close() # is this right?

                        fout = open(from_module_slot_comm_file,'a')

                        # this is the cortix info for modules using data
                        assert from_module.get_port_type(from_port) == 'use', \
                            'from_port must be use type.'

                        to_port_mode = to_module.get_port_mode(to_port)
                        if to_port_mode.split('.')[0] == 'file':
                            ext = to_port_mode.split('.')[1]
                            log_str = '<port name="' + from_port + \
                                      '" type="use" file="' + \
                                      to_module_slot_work_dir + to_port + '.' + ext + \
                                      '"/>\n'
                        elif to_port_mode == 'directory':
                            log_str = '<port name="' + from_port + \
                                      '" type="use" directory="' + \
                                      to_module_slot_work_dir + to_port + '"/>\n'
                        else:
                            assert False, 'invalid port mode. fatal.'

                        fout.write(log_str)
                        fout.close()

                        debug_str = '__setup_task():: comm module: ' + \
                                    from_module_slot + '; network: ' + task_name + \
                                    ' ' + log_str
                        self.__log.debug(debug_str)

                # register the cortix-comm file for the network
                net.set_runtime_cortix_comm_file( from_module_slot,
                                                  from_module_slot_comm_file )

        # finish forming the XML documents for port types
        for net in networks:
            for slot_name in net.slot_names:
                comm_file = net.get_runtime_cortix_comm_file(slot_name)
                if comm_file == 'null-runtime_cortix_comm_file':
                    if net.name != task_name:
                       s = '__setup_task():: comm file for ' + slot_name + \
                           ' in network ' + net.name + ' is ' + comm_file
                       self.__log.warn(s)
                       continue
                    else: 
                       assert False, 'FATAL ERROR building the comm file for module %r'%\
                                    slot_name
                fout = open(comm_file, 'a')
                fout.write('</cortix_comm>')
                fout.close()

        self.__log.debug('end __setup_task(%s)', task_name)
#----------------------- end def __setup_task():----------------------------------

#======================= end class Simulation: ===================================
