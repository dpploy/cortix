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
from cortix.src.utils.configtree import ConfigTree
from cortix.src.utils.set_logger_level import set_logger_level

from cortix.src.module  import Module
from cortix.src.network import Network
#*********************************************************************************

class Application:
    r"""
    An Application is a singleton class composed of Module objects, and Network
    objects; the latter involve Module objects in various combinations. Each
    combination is assigned to a Network object.
    """

    def __init__(self, app_work_dir, app_config_node):

        assert isinstance(app_work_dir, str), '-> app_work_dir is invalid'
        assert isinstance(app_config_node, ConfigTree), '-> app_config_node invalid'

        # Inherit configuration XML tree
        #self.__config_node = app_config_node

        # Read the application name
        self.__name = app_config_node.get_node_name()

        # Set the work directory (previously created)
        self.__work_dir = app_work_dir
        assert os.path.isdir(app_work_dir), "Work directory not available."

        # Set the module library for the whole application
        node = app_config_node.get_sub_node('module_library')
        sub_node = ConfigTree(node)
        assert sub_node.get_node_tag() == 'module_library', 'FATAL.'

        self.__module_lib_name = sub_node.get_node_name()

        for child in sub_node.get_node_children():
            (elem, tag, attributes, text) = child
            if tag == 'parent_dir':
                self.__module_lib_full_parent_dir = text.strip()

        if self.__module_lib_full_parent_dir[-1] == '/':
            self.__module_lib_full_parent_dir.strip('/')

        # Add library full path to python module search
        sys.path.insert(1, self.__module_lib_full_parent_dir)

        # Create logging facility
        self.__create_logging_facility( app_config_node )

        #==============
        # Setup modules
        #==============
        self.__modules = list()
        self.__setup_modules(app_config_node)

        #===============
        # Setup networks 
        #===============
        self.__networks = list()
        self.__setup_networks(app_config_node)

        self.__log.info('Created application: %s', self.__name)

        return
#----------------------- end def __init__():--------------------------------------

#*********************************************************************************
# Public functions 

    def __get_networks(self):
        '''
        `list(str)`:List of names of network objects
        '''

        return self.__networks
#----------------------- end def __get_networks():--------------------------------

    networks = property(__get_networks, None, None, None)

    def get_network(self, name):
        '''
        Returns a network with a given name.  None if the name doesn't exist.
        '''

        for net in self.__networks:
            if net.name == name:
                return net

        return None
#----------------------- end def get_network():-----------------------------------

    def __get_modules(self):
        '''
        `list(str)`:List of names of Cortix module objects
        '''

        return self.__modules
#----------------------- end def __get_modules():---------------------------------

    modules = property(__get_modules, None, None, None)

    def get_module(self, name):
        """
        Returns a module with a given name.  None if the name doesn't exist.
        """
        for mod in self.__modules:
            if mod.name == name:
                return mod
        return None
#----------------------- end def get_module():------------------------------------

    def __del__(self):

        self.__log.info('destroyed application: %s', self.__name)
#----------------------- end def __del__():---------------------------------------

#*********************************************************************************
# Private helper functions (internal use: __)

    def __create_logging_facility(self, app_config_node):
        '''
        A helper function to setup the logging facility used in self.__init__().
        '''

        # Create the logging facility for the singleton object
        node = app_config_node.get_sub_node("logger")
        logger_name = 'app:'+self.__name # prefix to avoid clash of loggers
        self.__log = logging.getLogger(logger_name)
        self.__log.setLevel(logging.NOTSET)

        logger_level = node.get('level').strip()
        self.__log = set_logger_level(self.__log, logger_name, logger_level)

        file_handler = logging.FileHandler(self.__work_dir + 'app.log')
        file_handler.setLevel(logging.NOTSET)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.NOTSET)

        for child in node:
            if child.tag == 'file_handler':
                # file handler
                file_handler_level = child.get('level').strip()
                file_handler = set_logger_level(file_handler, logger_name,
                                                file_handler_level)
            if child.tag == 'console_handler':
                # console handler
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
        self.__log.info('Created Application logger: %s', self.__name)
        self.__log.debug('logger level: %s', logger_level)
        self.__log.debug('logger file handler level: %s', file_handler_level)
        self.__log.debug(
            'logger console handler level: %s',
            console_handler_level)

        return
#----------------------- end def __create_loggin_facility():----------------------

    def __setup_modules( self, app_config_node ):
        '''
        A helper function used by the Application constructor to setup the modules
        portion of the Application.
        '''

        self.__log.debug('Start __setup_modules()')

        for mod_node in app_config_node.get_all_sub_nodes('module'):

            config_xml_tree = ConfigTree( mod_node )

            assert config_xml_tree.get_node_tag() == 'module'

            new_module = Module( self.__work_dir, self.__module_lib_name,
                                 self.__module_lib_full_parent_dir,
                                 config_xml_tree )

            # check for a duplicate module before appending a new one
            for module in self.__modules:
                mod_lib_dir_name = module.library_parent_dir
                mod_lib_name     = module.library_name

                if new_module.name == module.name:
                    if new_module.get_library_parent_dir() == mod_lib_dir_name:
                        assert new_module.get_library_name != mod_lib_name, \
                            'duplicate module; ABORT.'

            # add module to list
            self.__modules.append(new_module)
            self.__log.debug('appended module %s', mod_node.get('name'))

        self.__log.debug('end __setup_modules()')

        return
#----------------------- end def __setup_modules():-------------------------------

    def __setup_networks( self, app_config_node ):
        '''
        A helper function used by the Application constructor to setup the networks
        portion of the Application.
        '''

        self.__log.debug('start __setup_networks()')

        for net_node in app_config_node.get_all_sub_nodes('network'):
            net_config_node = ConfigTree(net_node)
            assert net_config_node.get_node_name() == net_node.get('name'), 'check failed'

            network = Network(net_config_node)

            self.__networks.append(network)
            self.__log.debug('appended network %s', net_node.get('name'))

        self.__log.debug('end __setup_networks()')

        return
#----------------------- end def __setup_networks():------------------------------

#======================= end class Application: ==================================
