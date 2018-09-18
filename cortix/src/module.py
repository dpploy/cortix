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
Cortix Module class defintion.

Cortix: a program for system-level modules coupling, execution, and analysis.
"""
#**********************************************************************************
import os
from cortix.src.utils.configtree import ConfigTree

from cortix.src.launcher import Launcher
#**********************************************************************************

class Module:
    '''
    The Module class encapsulates a computational module of some scientific domain.
    '''

    def __init__(self, parent_work_dir=None, library_name=None,
                 library_parent_dir=None, mod_config_node=ConfigTree()):

        assert isinstance(
            parent_work_dir, str), "-> parent_work_dir is invalid."

        # Inherit a configuration tree
        assert isinstance(mod_config_node, ConfigTree), \
               "-> mod_config_node is invalid."
        self.__config_node = mod_config_node

        # Read the module name and type
        self.__mod_name = self.__config_node.get_node_name()
        self.__mod_type = self.__config_node.get_node_type()

        # Specify module library with upstream information
        self.__library_parent_dir = library_parent_dir
        self.__library_name = library_name

        self.__executable_name = 'null-executable_name'
        self.__executable_path = 'null-executable_path'
        self.__input_file_name = 'null-input_file_name'
        self.__input_file_path = 'null-input_file_path'

        self.__ports = list()  # list of (port_name, port_type, port_multiplicity)

        # Save config data
        for child in self.__config_node.get_node_children():
            (elem, tag, attributes, text) = child
            text = text.strip()

            if self.__mod_type != 'native':
                if tag == 'executable_name':
                    self.__executable_name = text

            if tag == 'executable_path':
                if text[-1] != '/':
                    text += '/'
                self.__executable_path = text

            if tag == 'input_file_name':
                self.__input_file_name = text

            if tag == 'input_file_path':
                if text[-1] != '/':
                    text += '/'
                self.__input_file_path = text

            if tag == 'library':
                assert len(attributes) == 1, 'only name of library allowed.'
                key = attributes[0][0]
                assert key == 'name', 'invalid attribute.'
                val = attributes[0][1].strip()
                self.__library_name = val

                node = ConfigTree(elem)
                sub_node = node.get_sub_node('parent_dir')
                assert sub_node is not None, 'missing parent_dir.'

                self.__library_parent_dir = sub_node.text.strip()

                if self.__library_parent_dir[-1] == '/':
                    self.__library_parent_dir.strip('/')

            if tag == 'port':
                assert len(attributes) == 3, "only <= 3 attributes allowed."

                tmp = dict()  # store port name and three attributes

                for attribute in attributes:
                    key = attribute[0]
                    val = attribute[1].strip()

                    if key == 'type':
                        assert val == 'use' or val == 'provide' or val == 'input' or \
                            val == 'output', 'port attribute value invalid.'
                        tmp['port_name'] = text  # port_name
                        tmp['port_type'] = val   # port_type
                    elif key == 'mode':
                        file_value = val.split('.')[0]
                        assert file_value == 'file' or file_value == 'directory',\
                            'port attribute value invalid.'
                        tmp['port_mode'] = val
                    elif key == 'multiplicity':
                        tmp['port_multiplicity'] = int(val)  # port_multiplicity
                    else:
                        assert False, 'invalid port attribute. fatal.'

                assert len(tmp) == 4
                store = (tmp['port_name'], tmp['port_type'], tmp['port_mode'],
                         tmp['port_multiplicity'])
                self.__ports.append(store)  # (port_name, port_type, port_mode,
                #  port_multiplicity)
                tmp = None
                store = None
#----------------------- end def __init__():--------------------------------------

    def __get_name(self):
        '''
        `str`:Module name
        '''

        return self.__mod_name
    name = property(__get_name, None, None, None)
#----------------------- end def __get_name():------------------------------------

    def __get_library_name(self):
        '''
        `str`:Module library name
        '''

        return self.__library_name
    library_name = property(__get_library_name, None, None, None)
#----------------------- end def get_library_name():------------------------------

    def __get_library_parent_dir(self):
        '''
        `str`:Library parent directory
        '''

        return self.__library_parent_dir
    library_parent_dir = property(__get_library_parent_dir, None, None, None)
#----------------------- end def __get_library_parent_dir():----------------------

    def __get_ports(self):
        '''
       `list(tuple)`: Module's ports
        '''

        return self.__ports
    ports = property(__get_ports, None, None, None)
#----------------------- end def get_ports():-------------------------------------

    def get_port_type(self, port_name):
        '''
        Returns the port type specified by port_name
        '''

        port_type = None
        for port in self.__ports:
            if port[0] == port_name:
                port_type = port[1]
        return port_type
#----------------------- end def get_port_type():---------------------------------

    def get_port_mode(self, port_name):
        '''
        Returns the port mode specified by port_name
        '''

        port_mode = None
        for port in self.__ports:
            if port[0] == port_name:
                port_mode = port[2]
        return port_mode
#----------------------- end def get_port_mode():---------------------------------

    def __get_port_names(self):
        '''
        `list(tuple)`:List of names of module's ports
        '''

        port_names = list()
        for port in self.__ports:
            port_names.append(port[0])
        return port_names
    port_names = property(__get_port_names, None, None, None)
#----------------------- end def get_port_names():--------------------------------

    def has_port_name(self, port_name):
        '''
        Returns true if a port with the name
        port_name is available in the module.
        '''

        for port in self.__ports:
            if port[0] == port_name:
                return True
        return False
#----------------------- end def has_port_name():---------------------------------

    def execute( self, slot_id, 
                 runtime_cortix_param_file,
                 runtime_cortix_comm_file    ):
        '''
        Spawns a worker process to execute the module.
        '''
        assert runtime_cortix_param_file[-1] is not '/'
        assert runtime_cortix_comm_file[-1] is not '/'

        module_input = self.__input_file_path + self.__input_file_name
        param = runtime_cortix_param_file
        comm  = runtime_cortix_comm_file

        full_path_comm_dir = comm[:comm.rfind('/')] + '/' # extract directory name
        runtime_module_status_file = full_path_comm_dir + 'runtime-status.xml'

        status = runtime_module_status_file

        library_name = self.__library_name
        mod_name = self.__mod_name

        # provide for all modules for additional work IO data
        assert os.path.isdir(full_path_comm_dir), \
               'module directory %r not available.' % full_path_comm_dir

        mod_work_dir = full_path_comm_dir + 'wrk/'

        os.system('mkdir -p ' + mod_work_dir)

        assert os.path.isdir(mod_work_dir), \
               'module work directory %r not available.' % mod_work_dir

        # only for wrapped modules (deprecated; remove in the future)
        mod_exec_name = self.__executable_path + self.__executable_name

        # the laucher "loads" the module dynamically and provides the method for
        # threading
        launch = Launcher( library_name, mod_name,
                           slot_id,
                           module_input,
                           mod_exec_name,
                           mod_work_dir,
                           param, comm, status )

        # run module on its own process (file IO communication will take place
        # between modules)
        launch.start() # this start a thread and runs the run() method of launch

        return runtime_module_status_file
#----------------------- end def execute():---------------------------------------

#======================= end class Module: =======================================
