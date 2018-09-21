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
Launcher functionality of the Cortix Class.

Cortix: a program for system-level modules coupling, execution, and analysis.
"""
#*********************************************************************************
import os
import logging
import time
import datetime
from threading import Thread
import importlib
import xml.etree.ElementTree as ElementTree
import concurrent.futures
#*********************************************************************************

class Launcher(Thread):
    """
    The Launcher class handles the main funcitonality of stepping through the
    simulation time, and monitoring its progress.
    """

    def __init__(self, mod_lib_name, module_name, slot_id,
                 input_full_path_file_name,
                 exec_full_path_file_name,
                 work_dir,
                 cortix_param_full_path_file_name,
                 cortix_comm_full_path_file_name,
                 runtime_status_full_path):

        assert cortix_param_full_path_file_name[-1] is not '/', \
               '%r'%cortix_param_full_path_file_name
        assert cortix_comm_full_path_file_name[-1] is not '/' \
               '%r'%cortix_comm_full_path_file_name

        cortix_path = os.path.abspath(os.path.join(__file__, "../../.."))


        if "$CORTIX" in input_full_path_file_name:
            self.__input_full_path_file_name = input_full_path_file_name.replace("$CORTIX", cortix_path)
        else:
            self.__input_full_path_file_name = input_full_path_file_name

        self.__module_name = module_name
        self.__slot_id = slot_id
        self.__cortix_param_full_path_file_name = cortix_param_full_path_file_name
        self.__cortix_comm_full_path_file_name = cortix_comm_full_path_file_name
        self.__runtime_status_full_path = runtime_status_full_path
        self.__exec_full_path_file_name = exec_full_path_file_name
        self.__work_dir = work_dir

        # Create logger for this driver and its imported pymodule
        log = logging.getLogger('launcher-' + self.__module_name + '_' +
                                str(self.__slot_id))
        log.setLevel(logging.DEBUG)

        # create file handler for logs
        i = self.__cortix_comm_full_path_file_name.rfind('/') 
        directory = self.__cortix_comm_full_path_file_name[:i]
        full_path_launcher_dir = directory + '/'
        file_handle = logging.FileHandler(full_path_launcher_dir + 'launcher.log')
        file_handle.setLevel(logging.DEBUG)

        # create console handler with a higher log level
        console_handle = logging.StreamHandler()
        console_handle.setLevel(logging.INFO)

        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handle.setFormatter(formatter)
        console_handle.setFormatter(formatter)

        # add handles to the logger
        log.addHandler(file_handle)
        log.addHandler(console_handle)

        self.__log = log

        log.info('created logger')
        log.debug('input file: %s', self.__input_full_path_file_name)
        log.debug('param file: %s', self.__cortix_param_full_path_file_name)
        log.debug('comm file: %s', self.__cortix_comm_full_path_file_name)

        lib_module_driver = mod_lib_name + '.' + module_name + '.cortix_driver'
        log.info('import module driver: %s', lib_module_driver)

        # import a guest Cortix module through its driver
        try:
         self.__py_module = importlib.import_module( lib_module_driver )
        except Exception as error:
         log.error('importlib error: ', error)

        log.info('imported pyModule: %s', str(self.__py_module))

        super(Launcher, self).__init__()
#----------------------- end def __init__():--------------------------------------

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
        tree = ElementTree.parse(self.__cortix_param_full_path_file_name)
        cortix_param_xml_root_node = tree.getroot()
        node = cortix_param_xml_root_node.find('start_time')
        cortix_start_time_unit = node.get('unit')
        cortix_start_time = float(node.text.strip())

        if cortix_start_time_unit == 'minute':
            cortix_start_time *= 1.0
        elif cortix_start_time_unit == 'hour':
            cortix_start_time *= 60.0
        elif cortix_start_time_unit == 'day':
            cortix_start_time *= 24.0 * 60.0
        else:
            assert False, 'time unit invalid: %r' % (cortix_start_time_unit)

        node = cortix_param_xml_root_node.find('evolve_time')
        evolve_time_unit = node.get('unit')
        evolve_time = float(node.text.strip())

        if evolve_time_unit == 'minute':
            evolve_time *= 1.0
        elif evolve_time_unit == 'hour':
            evolve_time *= 60.0
        elif evolve_time_unit == 'day':
            evolve_time *= 24.0 * 60.0
        else:
            assert False, 'time unit invalid: %r' % (evolve_time_unit)

        node = cortix_param_xml_root_node.find('time_step')
        time_step_unit = node.get('unit')
        time_step = float(node.text.strip())

        if time_step_unit == 'minute':
            time_step *= 1.0
        elif time_step_unit == 'hour':
            time_step *= 60.0
        elif time_step_unit == 'day':
            time_step *= 24.0 * 60.0
        elif time_step_unit == 'second':
            time_step /= 60.0 
        else:
            assert False, 'time unit invalid: %r' % (time_step_unit)

        time_unit = 'minute'

        # collect information from the Cortix communication file for this guest module
        assert os.path.isfile(self.__cortix_comm_full_path_file_name),\
            'file %r not available;stop.' % self.__cortix_comm_full_path_file_name

        tree = ElementTree.parse(self.__cortix_comm_full_path_file_name)
        cortix_comm_xml_root_node = tree.getroot()

        # setup ports
        nodes = cortix_comm_xml_root_node.findall('port')
        ports = list()
        if nodes is not None:
            for node in nodes:
                port_name = node.get('name')
                port_type = node.get('type')
                port_file = node.get('file')
                port_directory = node.get('directory')

                if port_file is not None:
                    ports.append((port_name, port_type, port_file))
                elif port_directory is not None:
                    ports.append((port_name, port_type, port_directory))
                else:
                    assert False, 'port mode incorrect. fatal.'

        tree = None
        self.__log.debug('ports: %s', str(ports))

        # Add evolve time to start time  
        cortix_final_time = cortix_start_time + evolve_time

        # Create the guest code driver
        guest_driver = self.__py_module.CortixDriver( self.__slot_id,
                                                      self.__input_full_path_file_name,
                                                      self.__exec_full_path_file_name,
                                                      self.__work_dir,
                                                      ports, 
                                                      cortix_start_time, 
                                                      cortix_final_time,
                                                      time_unit )

        s = 'guest_driver = CortixDriver( slot_id=' + str(self.__slot_id) + \
            ', input file=' + self.__input_full_path_file_name + \
            ', exec file=' + self.__exec_full_path_file_name + \
            ', work dir=' + self.__work_dir + \
            ', ports=' + str(ports) + \
            ', cortix_start_time=' + str(cortix_start_time) + \
            ', cortix_final_time=' + str(cortix_final_time) + \
            ', time unit=minute )'
        self.__log.info(s)

        # Evolve the module
        self.__set_runtime_status('running')
        self.__log.info("__set_runtime_status(self, 'running')")

        cortix_time = cortix_start_time

        before_final_time = True

        while cortix_time <= cortix_final_time or before_final_time:

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

            s = 'run(' + str(round(cortix_time, 3)) + '[min]): ' # todo: change time unit
            self.__log.debug(s)
            s = 'run(' + str(round(cortix_time, 3)) + '[min]) ' # todo: change time unit
            self.__log.info(s)

            start_time = time.time()

            # Data exchange at cortix_time (call ports first)
            guest_driver.call_ports( cortix_time )

            # Advance to cortix_time + time_step (call execute second)
            guest_driver.execute( cortix_time, time_step )

            end_time = time.time()
            s = 'CPU elapsed time (s): ' + str(round(end_time - start_time, 2))
            self.__log.debug(s)

            cortix_time += time_step

        self.__set_runtime_status('finished')
        self.__log.info("__set_runtime_status(self, 'finished'")
#----------------------- end def run():-------------------------------------------

    def __del__(self):

        self.__log.info('destroyed launcher-%s',
                      self.__module_name + '_' + str(self.__slot_id))
#----------------------- end def __del__():---------------------------------------

#*********************************************************************************
# Private helper functions (internal use: __)

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
#----------------------- end def __set_runtime_status():--------------------------

#======================= end class Launcher: =====================================
