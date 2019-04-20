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
The Cortix class definition.

Cortix: a program for system-level modules coupling, execution, and analysis.
'''
#*********************************************************************************
import os
import logging
from cortix.src.simulation import Simulation
from cortix.src.utils.xmltree import XMLTree
from cortix.src.utils.set_logger_level import set_logger_level
#*********************************************************************************

class Cortix():
    '''
    The main Cortix class definition. This class encapsulates the
    concepts of simulations, tasks, and modules, for a given application providing
    the user with an interface to the simulations.
    '''

#*********************************************************************************
# Construction 
#*********************************************************************************

    def __init__(self, name, config_xml_file='cortix-config.xml'):

        assert isinstance(name,str), 'must give Cortix object a name'

        assert isinstance(config_xml_file, str), '-> config_xml_file not a str.'

        # Create the configuration XML tree
        config_xml_tree = XMLTree( xml_tree_file=config_xml_file )

        assert config_xml_tree.get_node_tag() == 'cortix_config'

        # Read the cortix config element (tag) name <name></name>
        node = config_xml_tree.get_sub_node('name') # get sub_node w/ tag: name (XML element)

        # Set the Cortix configuration name
        self.__name = node.get_node_content()  # name is now, say, 'droplet-fall'

        # Consistency check
        assert self.__name == name,\
            'Runtime Cortix object name %r conflicts with cortix-config.xml %r' \
            % (self.__name, name)

        # Read the work directory name
        node = config_xml_tree.get_sub_node('work_dir')
        work_dir = node.get_node_content()
        if work_dir[-1] != '/':
            work_dir += '/'

        self.__work_dir = work_dir + self.__name + '-wrk/'

        # Create the work directory
        if os.path.isdir(self.__work_dir):
            os.system('rm -rf ' + self.__work_dir)

        os.system('mkdir -p ' + self.__work_dir)

        # Create the logging facility for each object
        self.__create_logging( config_xml_tree )

        self.__log.info('Created Cortix work directory: %s', self.__work_dir)

        #==================
        # Setup simulations (one or more as specified in the config file)
        #==================
        self.__setup_simulations( config_xml_tree )

        self.__log.info('Created Cortix object %s', self.__name)

        return

    def __del__(self):

        self.__log.info("Destroyed Cortix object: %s", self.__name)

        return

#*********************************************************************************
# Public member functions
#*********************************************************************************

    def run_simulations(self, task_name=None):
        '''
        This method runs every simulation defined by the Cortix object. At the
        moment this is done one simulation at a time.
        '''

        for sim in self.__simulations:

            sim.execute( task_name )

        return

    def __get_simulations(self):
        '''
        Get all simulations.

        Parameters
        ----------
        empty

        Returns
        -------
        self.__simulations: list(Simulation)
        '''

        return self.__simulations

    simulations = property(__get_simulations,None,None,None)

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

    def __create_logging(self, config_xml_tree):
        '''
        A helper function to setup the logging facility used in self.__init__()
        '''

        logger_name = self.__name

        self.__log = logging.getLogger(logger_name)
        self.__log.setLevel(logging.NOTSET)

        node = config_xml_tree.get_sub_node('logger') # tag name is logger

        logger_level = node.get_node_attribute('level')
        self.__log = set_logger_level(self.__log, logger_name, logger_level)

        file_handler = logging.FileHandler(self.__work_dir + 'cortix.log')
        file_handler.setLevel(logging.NOTSET)
        file_handler_level = None

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.NOTSET)
        console_handler_level = None

        for child in node.get_node_children():
            (elem,tag,attributes,text) = child
            elem = XMLTree( elem ) # fixme: remove wrapping
            if tag == 'file_handler':
                file_handler_level = elem.get_node_attribute('level')
                file_handler = set_logger_level(file_handler, logger_name,
                                                file_handler_level)
            if tag == 'console_handler':
                console_handler_level = elem.get_node_attribute('level')
                console_handler = set_logger_level(console_handler, logger_name,
                                                   console_handler_level)

        # Formatter added to handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # add handlers to logger
        self.__log.addHandler(file_handler)
        self.__log.addHandler(console_handler)
        self.__log.info('Created Cortix logger: %s', self.__name)
        self.__log.debug('Logger level: %s', logger_level)
        self.__log.debug('Logger file handler level: %s', file_handler_level)
        self.__log.debug('Logger console handler level: %s', console_handler_level)

        return

    def __setup_simulations(self, config_xml_tree):
        '''
        This method is a helper function for the Cortix constructor whose purpose is 
        to set up the simulations defined by the Cortix configuration.
        '''

        self.__simulations = list()

        for sim_config_xml_node in config_xml_tree.get_all_sub_nodes('simulation'):

            assert sim_config_xml_node.get_node_tag() == 'simulation'

            self.__log.debug('__setup_simulations(): simulation name: %s',
                    sim_config_xml_node.get_node_attribute('name'))

            simulation = Simulation( self.__work_dir, sim_config_xml_node )

            self.__simulations.append(simulation)

        return

#======================= end class Cortix: =======================================
