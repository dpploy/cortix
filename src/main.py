# -*- coding: utf-8 -*-
"""
The Cortix class definition.


Cortix: a program for system-level modules coupling, execution, and analysis.

Valmor F. de Almeida dealmeidav@ornl.gov; vfda
Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os
import logging
from mpi4py import MPI
from cortix.src.task import Task
from cortix.src.simulation import Simulation
from cortix.src.utils.configtree import ConfigTree
from cortix.src.utils.set_logger_level import set_logger_level
#*********************************************************************************

class Cortix():
    """
    The main Cortix class definition. This class encapsulates the
    concepts of a task, application, and module, providing the
    user with an interface to the simulations.
    """

    def __init__(self, name=None, config_file="cortix-config.xml"):

        assert name is not None, "must give Cortix object a name"
        assert isinstance(config_file, str), "-> configFile not a str."
        self.config_file = config_file

        # Create a configuration tree
        self.config_tree = ConfigTree(config_file_name=self.config_file)

        # Read this object's name
        node = self.config_tree.get_sub_node("name")
        self.name = node.text.strip()

        # check
        assert self.name == name,\
        "Cortix object name %r conflicts with cortix-config.xml %r" \
        % (self.name, name)

        # Read the work directory name
        node = self.config_tree.get_sub_node("workDir")
        work_dir = node.text.strip()
        if work_dir[-1] != '/':
            work_dir += '/'

        self.work_dir = work_dir + self.name + "-wrk/"

        # Create the work directory
        if os.path.isdir(self.work_dir):
            os.system('rm -rf ' + self.work_dir)

        os.system('mkdir -p ' + self.work_dir)

        # Create the logging facility for each object
        node = self.config_tree.get_sub_node("logger")
        logger_name = self.name
        self.log = logging.getLogger(logger_name)
        self.log.setLevel(logging.NOTSET)
        logger_level = node.get("level").strip()
        self.log = set_logger_level(self.log, logger_name, logger_level)

        file_handler = logging.FileHandler(self.work_dir + "cortix.log")
        file_handler.setLevel(logging.NOTSET)
        file_handler_level = None

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.NOTSET)
        console_handler_level = None

        for child in node:
            if child.tag == "fileHandler":
                file_handler_level = child.get("level").strip()
                file_handler = set_logger_level(file_handler, logger_name, \
                                                file_handler_level)
            if child.tag == "consoleHandler":
                console_handler_level = child.get("level").strip()
                console_handler = set_logger_level(console_handler, logger_name, \
                                                   console_handler_level)

        # Formatter added to handlers
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # add handlers to logger
        self.log.addHandler(file_handler)
        self.log.addHandler(console_handler)
        self.log.info("Created Cortix logger: %s", self.name)
        self.log.debug("Logger level: %s", logger_level)
        self.log.debug("Logger file handler level: %s", file_handler_level)
        self.log.debug("Logger console handler level: %s", console_handler_level)
        self.log.info("Created Cortix work directory: %s", self.work_dir)

        # Setup simulations (one or more as specified in the config file)
        self.simulations = list()
        self.__setup_simulations()

        self.log.info("Created Cortix object %s", self.name)
#---------------------- end def __init__():---------------------------------------

    def run_simulations(self, task_name=None):
        """
        This method runs every simulation
        defined by the Cortix object.
        """

        for sim in self.simulations:
            sim.execute(task_name)
#---------------------- end def run_simulations():--------------------------------

#*********************************************************************************
# Private helper functions (internal use: __)

    def __setup_simulations(self):
        """
        This method is a helper function for the Cortix constructor
        whose purpose is to set up the simulations defined by the
        Cortix configuration.
        """

        for sim in self.config_tree.get_all_sub_nodes('simulation'):
            self.log.debug("SetupSimulations(): simulation name: %s", sim.get('name'))
            sim_config_tree = ConfigTree(sim)
            simulation = Simulation(self.work_dir, sim_config_tree)
            self.simulations.append(simulation)
#---------------------- end def __setup_simulations():----------------------------

    def __del__(self):

        self.log.info("Destroyed Cortix object: %s", self.name)
#---------------------- end def __del__():----------------------------------------

#====================== end class Cortix: ========================================
# Unit testing. Usage: -> python cortix.py
if __name__ == "__main__":
    # TODO: THIS FAILS SINCE THERE DOES NOT EXIST A cortix-config.xml
    print('Unit testing for Cortix')
    Cortix("cortix-config.xml")
