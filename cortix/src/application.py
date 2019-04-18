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
Application class for Cortix.

Cortix: a program for system-level modules coupling, execution, and analysis.
'''
#*********************************************************************************
import os
import sys
import logging
from cortix.src.utils.xmltree import XMLTree
from cortix.src.utils.set_logger_level import set_logger_level

from cortix.src.module  import Module
from cortix.src.network import Network
#*********************************************************************************

class Application:
    r'''
    An Application is a singleton class composed of Module objects, and Network
    objects; the latter involve Module objects in various combinations. Each
    combination is assigned to a Network object.
    '''

#*********************************************************************************
# Construction 
#*********************************************************************************

    def __init__(self, app_work_dir, config_xml_tree):

        assert isinstance(app_work_dir, str), '-> app_work_dir is invalid'
        assert os.path.isdir(app_work_dir), 'Work directory not available.'

        assert isinstance(config_xml_tree, XMLTree), '-> config_xml_tree invalid'
        assert config_xml_tree.get_node_tag() == 'application'

        # Read the application name
        self.__name = config_xml_tree.get_node_attribute('name')

        # Set the work directory (previously created)
        self.__work_dir = app_work_dir

        # Set the module library for the whole application
        node = config_xml_tree.get_sub_node('module_library')
        assert node.get_node_tag() == 'module_library', 'FATAL.'

        for child in node.get_node_children():
            (elem, tag, attributes, text) = child
            if tag == 'home_dir':
                self.__module_lib_full_home_dir = text.strip()

        if self.__module_lib_full_home_dir[-1] == '/':
            self.__module_lib_full_home_dir.strip('/')

        # Add library full path to python module search
        sys.path.insert(1, self.__module_lib_full_home_dir)

        # Create logging facility
        self.__create_logging_facility( config_xml_tree )

        #==============
        # Setup modules
        #==============
        self.__modules = list()

        self.__setup_modules(config_xml_tree)

        #===============
        # Setup networks 
        #===============
        self.__networks = list()

        self.__setup_networks(config_xml_tree)

        self.__log.info('Created application: %s', self.__name)

        return

    def __del__(self):

        self.__log.info('destroyed application: %s', self.__name)

#*********************************************************************************
# Public member functions
#*********************************************************************************

    def __get_networks(self):
        '''
        `list(str)`:List of names of network objects
        '''

        return self.__networks

    networks = property(__get_networks, None, None, None)

    def get_network(self, name):
        '''
        Returns a network with a given name. None if the name doesn't exist.

        Parameters
        ----------
        name: str

        Returns
        -------
        net: cortix.network or None
           Default: None
        '''

        for net in self.__networks:
            if net.name == name:
                return net

        return None

    def __get_modules(self):
        '''
        `list(str)`:List of names of Cortix module objects
        '''

        return self.__modules

    modules = property(__get_modules, None, None, None)

    def get_module(self, name):
        """
        Returns a module with a given name.  None if the name doesn't exist.
        """
        for mod in self.__modules:
            if mod.name == name:
                return mod
        return None

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

    def __create_logging_facility(self, config_xml_tree):
        '''
        A helper function to setup the logging facility used in self.__init__().
        '''

        assert config_xml_tree.get_node_tag() == 'application'

        # Create the logging facility for the singleton object
        node = config_xml_tree.get_sub_node('logger')

        logger_name = 'app:'+self.__name # prefix to avoid clash of loggers
        self.__log = logging.getLogger(logger_name)
        self.__log.setLevel(logging.NOTSET)

        logger_level = node.get_node_attribute('level')
        self.__log = set_logger_level(self.__log, logger_name, logger_level)

        file_handler = logging.FileHandler(self.__work_dir + 'app.log')
        file_handler.setLevel(logging.NOTSET)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.NOTSET)

        for child in node.get_node_children():
            (elem,tag,attributes,text) = child
            elem = XMLTree( elem )
            if tag == 'file_handler':
                file_handler_level = elem.get_node_attribute('level')
                file_handler = set_logger_level(file_handler, logger_name,
                                                file_handler_level)
            if tag == 'console_handler':
                console_handler_level = elem.get_node_attribute('level')
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
        self.__log.info('created Application logger: %s', self.__name)
        self.__log.debug('logger level: %s', logger_level)
        self.__log.debug('logger file handler level: %s', file_handler_level)
        self.__log.debug('logger console handler level: %s', console_handler_level)

        return

    def __setup_modules( self, config_xml_tree ):
        '''
        A helper function used by the Application constructor to setup the modules
        portion of the Application. What this does is to go into the Cortix config file
        and read all modules that part of the module tag whether they are used in a
        given task or not.
        '''

        self.__log.debug('Start __setup_modules()')

        for mod_config_xml_node in config_xml_tree.get_all_sub_nodes('module'):

            assert mod_config_xml_node.get_node_tag() == 'module'

            # Modules log into the Application logger because they may or may not be 
            # used in a task. Running tasks will effectively tell what modules are used.
            new_module = Module( self.__log,
                                 self.__module_lib_full_home_dir,
                                 mod_config_xml_node )

            # check for a duplicate module before appending a new one
            for module in self.__modules:
                mod_lib_dir_name   = module.library_home_dir

                if new_module.name == module.name:
                    assert new_module.library_home_dir != mod_lib_dir_name,\
                            ' duplicate module; ABORT.'

            # add module to list
            self.__modules.append( new_module )

            self.__log.debug('appended module %s',
                    mod_config_xml_node.get_node_attribute('name'))

        self.__log.debug('end __setup_modules()')

        return

    def __setup_networks( self, config_xml_tree ):
        '''
        A helper function used by the Application constructor to setup the networks
        portion of the Application.
        '''

        self.__log.debug('start __setup_networks()')

        for net_config_xml_node in config_xml_tree.get_all_sub_nodes('network'):

            assert net_config_xml_node.get_node_tag() == 'network'

            network = Network( net_config_xml_node )

            self.__networks.append(network)

            self.__log.debug('appended network %s',
                    net_config_xml_node.get_node_attribute('name'))

        self.__log.debug('end __setup_networks()')

        return

#======================= end class Application: ==================================
