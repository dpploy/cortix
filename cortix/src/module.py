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
Cortix Module class defintion.

Cortix: a program for system-level modules coupling, execution, and analysis.
'''
#**********************************************************************************
import os
import logging

from cortix.src.utils.xmltree import XMLTree
from cortix.src.launcher import Launcher
#**********************************************************************************

class Module:
    '''
    The Module class encapsulates a computational module of some scientific domain.
    '''

#*********************************************************************************
# Construction 
#*********************************************************************************

    def __init__( self, 
            logger,
            library_home_dir, 
            config_xml_tree ):

        assert isinstance(logger, logging.Logger),'ctx::mod: logger is invalid.'
        assert isinstance(library_home_dir, str),'ctx:mod: library_home is invalid.'

        assert isinstance(config_xml_tree, XMLTree),'ctx:mod: config_xml_tree is invalid.'
        assert config_xml_tree.get_node_tag() == 'module','ctx:mod:invalid module xml tree.'
        # Read the module name and type
        self.__mod_name = config_xml_tree.get_node_attribute('name') # e.g. wind

        # Specify module library with upstream information
        self.__library_home_dir = library_home_dir

        self.__input_file_name = 'null-input_file_name'
        self.__input_file_path = 'null-input_file_path'

        # Get config data  
        for child in config_xml_tree.get_node_children():

            (elem, tag, attributes, text) = child
            text = text.strip()

            if tag == 'input_file_name':
                self.__input_file_name = text

            if tag == 'input_file_path':
                if text[-1] != '/':
                    text += '/'
                self.__input_file_path = text

            if tag == 'library':
                assert len(attributes) == 0, 'no attributes allowed.'

                node = XMLTree( elem ) # fixme: remove this wrapper
                sub_node = node.get_sub_node('home_dir')

                # override home_dir
                # fixme: no root node needed
                self.__library_home_dir = sub_node.get_root_node().text.strip()

                if self.__library_home_dir[-1] == '/':
                    self.__library_home_dir.strip('/')

        logger.debug(self.__mod_name+': read module config info')

        # Take care of a few full path issue
        cortix_path = os.path.abspath(os.path.join(__file__, '../../..'))

        self.__manifesto_full_path_file_name = self.__library_home_dir + '/' + \
                self.__mod_name + '/manifesto.xml'

        if '$CORTIX' in self.__input_file_path:
            self.__input_file_path = \
                    self.__input_file_path.replace('$CORTIX', cortix_path)

        if '$CORTIX' in self.__manifesto_full_path_file_name:
            self.__manifesto_full_path_file_name = \
                    self.__manifesto_full_path_file_name.replace('$CORTIX', cortix_path)

        # Read the module's manifesto
        self.__read_manifesto()

        logger.debug(self.__mod_name+': read manifesto ports\n %s'%self.__diagram)

        return

#*********************************************************************************
# Public member functions
#*********************************************************************************

    def __get_name(self):
        '''
        `str`:Module name
        '''

        return self.__mod_name

    name = property(__get_name, None, None, None)

    def __get_library_home_dir(self):
        '''
        `str`:Library home directory
        '''

        return self.__library_home_dir

    library_home_dir = property(__get_library_home_dir, None, None, None)

    def __get_ports(self):
        '''
       `list(tuple)`: Module's ports
        '''

        return self.__ports

    ports = property(__get_ports, None, None, None)

    def get_port_type(self, port_name):
        '''
        Returns the port type specified by port_name
        '''

        port_type = None
        for port in self.__ports:
            if port[0] == port_name:
                port_type = port[1]

        return port_type

    def get_port_mode(self, port_name):
        '''
        Returns the port mode specified by port_name
        '''

        port_mode = None
        for port in self.__ports:
            if port[0] == port_name:
                port_mode = port[2]

        return port_mode

    def __get_port_names(self):
        '''
        `list(tuple)`:List of names of module's ports
        '''

        port_names = list()
        for port in self.__ports:
            port_names.append(port[0])
        return port_names

    port_names = property(__get_port_names, None, None, None)

    def has_port_name(self, port_name):
        '''
        Returns true if a port with the name
        port_name is available in the module.
        '''

        for port in self.__ports:
            if port[0] == port_name:
                return True

        return False

    def __get_diagram(self):
        '''
        Return the diagram string from the module manifesto or a null place holder.
        '''

        return self.__diagram

    diagram = property(__get_diagram, None, None, None)

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

        library_home_dir = self.__library_home_dir
        mod_name     = self.__mod_name

        # provide a wrk/ for each modules for additional work IO data
        assert os.path.isdir(full_path_comm_dir), \
               'module directory %r not available.' % full_path_comm_dir

        mod_work_dir = full_path_comm_dir + 'wrk/'

        os.system('mkdir -p ' + mod_work_dir)

        assert os.path.isdir(mod_work_dir), \
               'module work directory %r not available.' % mod_work_dir

        manifesto_name = self.__manifesto_full_path_file_name

        # the laucher "loads" the module dynamically and provides the method for
        # threading
        launch = Launcher( library_home_dir, mod_name,
                           slot_id,
                           module_input,
                           manifesto_name,
                           mod_work_dir,
                           param, comm, status )

        # run module on its own process (file IO communication will take place
        # between modules)
        launch.start() # this start a thread and runs the run() method of launch

        return runtime_module_status_file

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

    def __read_manifesto( self ):
        '''
        Get ports
        '''

        assert isinstance(self.__manifesto_full_path_file_name, str)

        # Read the manifesto 
        xml_tree = XMLTree( xml_tree_file=self.__manifesto_full_path_file_name )

        assert xml_tree.get_node_tag() == 'module_manifesto'

        assert xml_tree.get_node_attribute('name') == self.__mod_name,\
                "xml_tree.get_node_attribute('name') is %r and self.__mod_name is %r"%\
                (xml_tree.get_node_attribute('name'),self.__mod_name)

        # List of (port_name, port_type, port_mode, port_multiplicity)
        self.__ports = list()

        self.__diagram = 'null-module-diagram'

        # Get config data  
        for child in xml_tree.get_node_children():
            (elem, tag, attributes, text) = child

            if tag == 'port':

                text = text.strip()

                assert len(attributes) == 3, "only <= 3 attributes allowed."

                tmp = dict()  # store port name and three attributes

                for attribute in attributes:
                    key = attribute[0].strip()
                    val = attribute[1].strip()

                    if key == 'type':
                        assert val == 'use' or val == 'provide' or val == 'input' or\
                            val == 'output', 'port attribute value invalid.'
                        tmp['port_name'] = text  # port_name
                        tmp['port_type'] = val   # port_type
                    elif key == 'mode':
                        file_value = val.split('.')[0]
                        assert file_value == 'file' or file_value == 'directory' or\
                                file_value == 'hardware', 'port attribute value invalid.'
                        tmp['port_mode'] = val
                    elif key == 'multiplicity':
                        tmp['port_multiplicity'] = int(val)  # port_multiplicity
                    else:
                        assert False, 'invalid port attribute: %r=%r. fatal.'%\
                                (key,val)

                assert len(tmp) == 4
                store = (tmp['port_name'], tmp['port_type'], tmp['port_mode'],
                         tmp['port_multiplicity'])

                # (port_name, port_type, port_mode, port_multiplicity)
                self.__ports.append(store)

                # clear
                tmp   = None
                store = None

            if tag == 'diagram':

                self.__diagram = text


        return

#======================= end class Module: =======================================
