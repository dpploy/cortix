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
# *********************************************************************************
import os
import logging
import time
import datetime
from mpi4py import MPI
from mpi4py.futures import MPIPoolExecutor
import importlib
import xml.etree.ElementTree as ElementTree
# *********************************************************************************


class Launcher():
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

        self.module_name = module_name
        self.slot_id = slot_id
        self.input_full_path_file_name = input_full_path_file_name
        self.cortix_param_full_path_file_name = cortix_param_full_path_file_name
        self.cortix_comm_full_path_file_name = cortix_comm_full_path_file_name
        self.runtime_status_full_path = runtime_status_full_path
        self.exec_full_path_file_name = exec_full_path_file_name
        self.work_dir = work_dir

        # Create logger for this driver and its imported pymodule
        log = logging.getLogger('launcher-' + self.module_name + '_' +
                                str(self.slot_id))
        log.setLevel(logging.DEBUG)

        # create file handler for logs
        full_path_task_dir = self.cortix_comm_full_path_file_name[:self.cortix_comm_full_path_file_name.rfind(
            '/')] + '/'
        file_handle = logging.FileHandler(full_path_task_dir + 'launcher.log')
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

        self.log = log

        log.info('created logger')
        log.debug('input file: %s', self.input_full_path_file_name)
        log.debug('param file: %s', self.cortix_param_full_path_file_name)
        log.debug('comm file: %s', self.cortix_comm_full_path_file_name)

        lib_module_driver = mod_lib_name + '.' + module_name + '.cortix_driver'
        log.info('module driver: %s', lib_module_driver)

        # import and log the python module driver
        self.py_module = importlib.import_module(lib_module_driver)
        log.info('imported pyModule: %s', str(self.py_module))
# ---------------------- end def __init__():------------------------------

    def run(self):
        """
        Function used to timestep through the modules.
        Runs the simulation from start to end, and moinitors
        its progress at each time step.
        """

        # Verify the module input file name with full path.
        # This input file may be empty or used by this driver and/or the
        # native/wrapped module.
        assert os.path.isfile(self.input_full_path_file_name), \
            'file %r not available;stop.' % self.input_full_path_file_name

        # Read the Cortix parameter file: cortix-param.xml
        # cortix_param_full_path_file_name

        assert os.path.isfile(self.cortix_param_full_path_file_name), \
            'file %r not available;stop.' % self.cortix_param_full_path_file_name

        tree = ElementTree.parse(self.cortix_param_full_path_file_name)
        cortix_param_xml_root_node = tree.getroot()
        node = cortix_param_xml_root_node.find('start_time')
        start_time_unit = node.get('unit')
        start_time = float(node.text.strip())

        if start_time_unit == 'minute':
            start_time *= 1.0
        elif start_time_unit == 'hour':
            start_time *= 60.0
        elif start_time_unit == 'day':
            start_time *= 24.0 * 60.0
        else:
            assert False, 'time unit invalid: %r' % (start_time_unit)

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
        else:
            assert False, 'time unit invalid: %r' % (time_step_unit)

        assert os.path.isfile(self.cortix_comm_full_path_file_name),\
            'file %r not available;stop.' % self.cortix_comm_full_path_file_name

        tree = ElementTree.parse(self.cortix_comm_full_path_file_name)
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
        self.log.debug('ports: %s', str(ports))

        # Run module_name
        self.log.info('entered Run %s', self.module_name +
                      '_' + str(self.slot_id) + ' section')
        final_time = start_time + evolve_time

        # Create the guest code driver
        guest_driver = self.py_module.CortixDriver(self.slot_id,
                                                   self.input_full_path_file_name,
                                                   self.exec_full_path_file_name,
                                                   self.work_dir,
                                                   ports, start_time, final_time)

        s = 'guest_driver = CortixDriver( slot_id=' + str(self.slot_id) + \
            ', input file=' + self.input_full_path_file_name + \
            ', exec file=' + self.exec_full_path_file_name + \
            ', work dir=' + self.work_dir + \
            ', ports=' + str(ports) + \
            ', cortix_start_time=' + str(start_time) + \
            ', cortix_final_time=' + str(final_time) + ' )'
        self.log.info(s)

        # Evolve the module
        self.__set_runtime_status('running')
        self.log.info("__set_runtime_status(self, 'running')")

        cortix_time = start_time

        while cortix_time <= final_time:

            s = ''
            self.log.debug(s)
            s = '**************************************************************' + \
                '**************'
            self.log.debug(s)
            s = 'CORTIX::LAUNCHER->***->LAUNCHER->***->LAUNCHER->***->' + \
                'LAUNCHER->***->LAUNCHER'
            self.log.debug(s)
            s = '**************************************************************' + \
                '**************'
            self.log.debug(s)

            s = 'run(' + str(round(cortix_time, 3)) + '[min]): '
            self.log.debug(s)
            start_time = time.time()

            # Data exchange at cortix_time (call ports first)
            guest_driver.call_ports(cortix_time)

            # Advance to cortix_time + time_step (call execute second)
            guest_driver.execute(cortix_time, time_step)

            end_time = time.time()
            s = 'CPU elapsed time (s): ' + str(round(end_time - start_time, 2))
            self.log.debug(s)

            s = 'run(' + str(round(cortix_time, 3)) + '[min]) '
            self.log.info(s)

            cortix_time += time_step

        self.__set_runtime_status('finished')
        self.log.info("__set_runtime_status(self, 'finished'")
# ---------------------- end def run():-----------------------------------

    def __del__(self):

        self.log.info('destroyed launcher-%s',
                      self.module_name + '_' + str(self.slot_id))
# ---------------------- end def __del__():---------------------------

# *********************************************************************************
# Private helper functions (internal use: __)

    def __set_runtime_status(self, status):
        """
        Helper function used by the launcher
        constructor to output status of the
        current run.
        """

        comm = MPI.COMM_WORLD
        # rank = comm.Get_rank()
        # size = comm.Get_size()
        amode = MPI.MODE_WRONLY | MPI.MODE_CREATE

        status = status.strip()
        assert status == 'running' or status == 'finished', 'status invalid.'

        fout = MPI.File.Open(comm, self.runtime_status_full_path, amode)
        fout.Write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        fout.Write(b'<!-- Written by Launcher::__set_runtime_status.py -->\n')

        today = datetime.datetime.today()
        fout.Write("".join('<!-- ' + str(today) + ' -->\n').encode())
        fout.Write(b'<runtime>\n')
        fout.Write("".join('<status>' + status + '</status>\n').encode())
        fout.Write(b'</runtime>\n')

        fout.Close()
# ---------------------- end def __set_runtime_status():------------------

# ====================== end class Launcher: =============================
