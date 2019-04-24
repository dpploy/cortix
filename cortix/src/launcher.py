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
Launcher functionality of the Cortix Class.

Cortix: a program for system-level modules coupling, execution, and analysis.
'''
#*********************************************************************************
import os, sys
import logging
import time
import datetime
from threading import Thread
import importlib
import xml.etree.ElementTree as ElementTree
from cortix.src.utils.xmltree import XMLTree
#*********************************************************************************

class Launcher(Thread):
    '''
    The Launcher class handles the main funcitonality of stepping through the
    simulation time, and monitoring its progress.
    '''

#*********************************************************************************
# Construction 
#*********************************************************************************

    def __init__(self, 
            mod_lib_home_dir, module_name, 
            slot_id,
            input_full_path_file_name,
            manifesto_full_path_file_name,
            work_dir,
            cortix_param_full_path_file_name,
            cortix_comm_full_path_file_name,
            runtime_status_full_path):

        assert mod_lib_home_dir[-1] is not '/', \
                '%r'%mod_lib_home_dir
        assert input_full_path_file_name[-1] is not '/', \
                '%r'%input_full_path_file_name
        assert manifesto_full_path_file_name[-1] is not '/', \
                '%r'%manifesto_full_path_file_name
        assert cortix_param_full_path_file_name[-1] is not '/', \
                '%r'%cortix_param_full_path_file_name
        assert cortix_comm_full_path_file_name[-1] is not '/' \
                '%r'%cortix_comm_full_path_file_name
        assert runtime_status_full_path[-1] is not '/' \
                '%r'%runtime_status_full_path

        cortix_path = os.path.abspath(os.path.join(__file__, '../../..'))

        if '$CORTIX' in mod_lib_home_dir:
            mod_lib_home_dir = mod_lib_home_dir.replace('$CORTIX', cortix_path)

        self.__input_full_path_file_name = input_full_path_file_name

        self.__module_name = module_name
        self.__slot_id = slot_id
        self.__cortix_param_full_path_file_name = cortix_param_full_path_file_name
        self.__cortix_comm_full_path_file_name = cortix_comm_full_path_file_name
        self.__runtime_status_full_path = runtime_status_full_path
        self.__manifesto_full_path_file_name = manifesto_full_path_file_name
        self.__work_dir = work_dir

        # Create logging facility
        self.__create_logging_facility()

        module_cortix_driver = module_name + '.cortix_driver'
        self.__log.info('try importing module driver: %s', module_cortix_driver )

        sys.path.insert(0,os.path.abspath(mod_lib_home_dir))

        # import a guest Cortix module through its driver
        try:
            self.__py_module = importlib.import_module( module_cortix_driver )
        except Exception as error:
            log.error('importlib error: ', error)

        self.__log.info('imported pyModule: %s', str(self.__py_module))

        # Launcher thread initialiation
        super(Launcher, self).__init__()

        return

    def __del__(self):

        self.__log.info('destroyed launcher-%s',
                      self.__module_name + '_' + str(self.__slot_id))

        return

#*********************************************************************************
# Public member functions
#*********************************************************************************

    def run(self):
        '''
        Function used to timestep through the modules.
        Runs the simulation from start to end, and monitors
        its progress at each time step.
        '''

        # log info           
        self.__log.info('entered run() %s', self.__module_name +
                      '_' + str(self.__slot_id) )

        # Verify the module input file name with full path.
        # This input file may be empty or used by this driver and/or the
        # native/wrapped module.
        assert os.path.isfile(self.__input_full_path_file_name), \
            'file %r not available;stop.' % self.__input_full_path_file_name

        # Read the Cortix parameter file: cortix-param.xml
        # cortix_param_full_path_file_name
        assert os.path.isfile(self.__cortix_param_full_path_file_name), \
            'file %r not available;stop.' % self.__cortix_param_full_path_file_name

        # For now Cortix advances in unit of minutes; change this in the future
        cortix_param_xml_tree = XMLTree( xml_tree_file = self.__cortix_param_full_path_file_name)
        node = cortix_param_xml_tree.get_sub_node('start_time')
        cortix_start_time_unit = node.get_node_attribute('unit')
        cortix_start_time = float(node.get_node_content().strip())

        if cortix_start_time_unit == 'minute':
            cortix_start_time *= 1.0
        elif cortix_start_time_unit == 'hour':
            cortix_start_time *= 60.0
        elif cortix_start_time_unit == 'day':
            cortix_start_time *= 24.0 * 60.0
        else:
            assert False, 'time unit invalid: %r' % (cortix_start_time_unit)

        node = cortix_param_xml_tree.get_sub_node('evolve_time')
        evolve_time_unit = node.get_node_attribute('unit')
        evolve_time = float(node.get_node_content().strip())

        if evolve_time_unit == 'minute':
            evolve_time *= 1.0
        elif evolve_time_unit == 'hour':
            evolve_time *= 60.0
        elif evolve_time_unit == 'day':
            evolve_time *= 24.0 * 60.0
        else:
            assert False, 'time unit invalid: %r' % (evolve_time_unit)

        node = cortix_param_xml_tree.get_sub_node('time_step')
        cortix_time_step_unit = node.get_node_attribute('unit')
        cortix_time_step = float(node.get_node_content().strip())

        if cortix_time_step_unit == 'minute':
            cortix_time_step *= 1.0
        elif cortix_time_step_unit == 'hour':
            cortix_time_step *= 60.0
        elif cortix_time_step_unit == 'day':
            cortix_time_step *= 24.0 * 60.0
        elif cortix_time_step_unit == 'second':
            cortix_time_step /= 60.0
        else:
            assert False, 'time unit invalid: %r' % (cortix_time_step_unit)

        node = cortix_param_xml_tree.get_sub_node('real_time')
        real_time = node.get_node_content().strip()

        sleep = 0.0

        if real_time == 'false':
            sleep = 0.0
        else:
            sleep = cortix_time_step * 60.0

        cortix_time_unit = 'minute'

        # collect information from the Cortix communication file for this guest module
        assert os.path.isfile(self.__cortix_comm_full_path_file_name),\
            'file %r not available;stop.' % self.__cortix_comm_full_path_file_name

        cortix_comm_xml_tree = XMLTree( xml_tree_file = self.__cortix_comm_full_path_file_name )

        # Setup ports
        nodes = cortix_comm_xml_tree.get_all_sub_nodes('port')
        ports = list()
        if nodes is not None:
            for node in nodes:
                #port_name = node.get('name')
                #port_type = node.get('type')
                #port_file = node.get('file')
                #port_directory = node.get('directory')
                #port_hardware = node.get('hardware')

                port_name = node.get_attribute('name')
                port_type = node.get_attribute('type')
                port_file = node.get_attribute('file')
                port_directory = node.get_attribute('directory')
                port_hardware = node.get_attribute('hardware')

                if port_file is not None:
                    ports.append((port_name, port_type, port_file))
                elif port_directory is not None:
                    ports.append((port_name, port_type, port_directory))
                elif port_hardware is not None:
                    ports.append((port_name, port_type, port_hardware))
                else:
                    assert False, 'port mode incorrect. fatal.'

        #tree = None
        self.__log.debug('ports: %s', str(ports))

        # Add evolve time to start time  
        cortix_final_time = cortix_start_time + evolve_time

        # Create the guest code driver
        guest_driver = self.__py_module.CortixDriver( self.__slot_id,
                                                      self.__input_full_path_file_name,
                                                      self.__manifesto_full_path_file_name,
                                                      self.__work_dir,
                                                      ports,
                                                      cortix_start_time,
                                                      cortix_final_time,
                                                      cortix_time_step,
                                                      cortix_time_unit
                                                    )

        s = 'guest_driver = CortixDriver( slot_id=' + str(self.__slot_id) + \
            ', input file=' + self.__input_full_path_file_name + \
            ', manifesto file=' + self.__manifesto_full_path_file_name + \
            ', work dir=' + self.__work_dir + \
            ', ports=' + str(ports) + \
            ', cortix_start_time=' + str(cortix_start_time) + \
            ', cortix_final_time=' + str(cortix_final_time) + \
            ', cortix_time_unit=' + cortix_time_unit + \
            ', cortix_time_step=' + str(cortix_time_step) + \
            ', cortix_time_step_unit=', cortix_time_step_unit
        self.__log.info(s)

        # Evolve the module
        self.__set_runtime_status('running')
        self.__log.info("__set_runtime_status(self, 'running')")

        cortix_time = cortix_start_time

        before_final_time = True

        while cortix_time <= cortix_final_time or before_final_time:

            time.sleep( sleep )

            if cortix_time >= cortix_final_time:  # make sure the final time is reached
               before_final_time = False          # or exceeded by a epsilon amount

            s = ''
            self.__log.debug(s)
            s = '**************************************************************' + \
                '**************'
            self.__log.debug(s)
            s = 'CORTIX::LAUNCHER->***->LAUNCHER->***->LAUNCHER->***->' + \
                'LAUNCHER->***->LAUNCHER'
            self.__log.debug(s)
            s = '**************************************************************' + \
                '**************'
            self.__log.debug(s)

            s = 'run(' + str(round(cortix_time, 2)) + '['+cortix_time_unit+']): '
            self.__log.debug(s)
            s = 'run(' + str(round(cortix_time, 2)) + '['+cortix_time_unit+']): '
            self.__log.info(s)

            start_time = time.time()

            # Data exchange at cortix_time (call ports first)
            guest_driver.call_ports( cortix_time )

            # Advance to cortix_time + cortix_time_step (call execute second)
            guest_driver.execute( cortix_time, cortix_time_step )

            end_time = time.time()
            s = 'CPU elapsed time (s): ' + str(round(end_time - start_time, 2))
            self.__log.debug(s)

            cortix_time += cortix_time_step

        self.__set_runtime_status('finished')
        self.__log.info("__set_runtime_status(self, 'finished'")

        return

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

    def __set_runtime_status(self, status):
        """
        Helper function used by the launcher constructor to output status of the
        current run.
        """

        status = status.strip()
        assert status == 'running' or status == 'finished', 'status invalid.'

        fout = open(self.__runtime_status_full_path, 'w')
        fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        fout.write('<!-- Written by Launcher::__set_runtime_status.py -->\n')

        today = datetime.datetime.today()
        fout.write('<!-- ' + str(today) + ' -->\n')
        fout.write('<runtime>\n')
        fout.write('<status>' + status + '</status>\n')
        fout.write('</runtime>\n')

        fout.close()

        return

    def __create_logging_facility(self):
        '''
        A helper function to setup the logging facility used in self.__init__()
        '''

        # Create logger for this launcher and its imported pymodule; Cortix modules
        # should use this for logging
        log = logging.getLogger('launcher-' + self.__module_name + '_' +
                                str(self.__slot_id))
        log.setLevel(logging.DEBUG)

        # Create file handler for logs; same place as the Cortix comm file for module
        i = self.__cortix_comm_full_path_file_name.rfind('/')
        directory = self.__cortix_comm_full_path_file_name[:i]
        full_path_launcher_dir = directory + '/'
        file_handle = logging.FileHandler(full_path_launcher_dir + 'launcher.log')
        file_handle.setLevel(logging.DEBUG)

        # Create console handler with a higher log level
        console_handle = logging.StreamHandler()
        console_handle.setLevel(logging.INFO)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handle.setFormatter(formatter)
        console_handle.setFormatter(formatter)

        # add handles to the logger
        log.addHandler(file_handle)
        log.addHandler(console_handle)

        log.info('created logger')
        log.debug('input file: %s', self.__input_full_path_file_name)
        log.debug('param file: %s', self.__cortix_param_full_path_file_name)
        log.debug('comm file: %s', self.__cortix_comm_full_path_file_name)

        self.__log = log

        return

#======================= end class Launcher: =====================================
