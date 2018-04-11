# -*- coding: utf-8 -*-

"""
This file contains the class definition for the Simulation feature
in the Cortix project.

Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""

#*********************************************************************************
import os
import logging
from cortix.utils.configtree import ConfigTree
from cortix.application._application import Application
from cortix.simulation._setuptask import setup_task
from cortix.main.set_logger_level import set_logger_level
#*********************************************************************************

#========================BEGIN SIMULATION CLASS DEFINITION=======================

class Simulation:

    """
    This is the main class definition for the simulation implementation in
    the Cortix project. This class provides an interface to the instantiation
    and execution of a simulation as defined in the Cortix config.
    """

    def __init__(self, parent_work_dir=None, sim_config_node=ConfigTree()):
        assert isinstance(parent_work_dir, str), "-> parentWorkDir invalid."

        # Inherit a configuration tree
        assert isinstance(sim_config_node, ConfigTree), "-> simConfigNode invalid."
        self.config_node = sim_config_node

        # Read the simulation name
        self.name = sim_config_node.get_node_name()

        # Create the cortix/simulation work directory
        self.work_dir = parent_work_dir + "sim_" + self.name + '/'

        os.system("mkdir -p " + self.work_dir)

        # Create the logging facility for each object
        node = sim_config_node.get_sub_node("logger")
        logger_name = self.name + ".sim"
        self.log = logging.getLogger(logger_name)
        self.log.setLevel(logging.NOTSET)

        logger_level = node.get('level').strip()
        self.log = set_logger_level(self.log, logger_name, logger_level)

        file_handler = logging.FileHandler(self.work_dir + 'sim.log')
        file_handler.setLevel(logging.NOTSET)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.NOTSET)

        for child in node:
            if child.tag == "fileHandler":
                file_handler_level = child.get("level").strip()
                file_handler = set_logger_level(file_handler, logger_name, file_handler_level)

            if child.tag == 'consoleHandler':
                console_handler_level = child.get('level').strip()
                console_handler = set_logger_level(console_handler, logger_name, console_handler_level)

        # formatter added to handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # add handlers to logger
        self.log.addHandler(file_handler)
        self.log.addHandler(console_handler)

        self.log.info("created Simulation logger: %s", self.name)
        self.log.debug("'logger level: %s", logger_level)
        self.log.debug("logger file handler level: %s", file_handler_level)
        self.log.debug("logger console handler level: %s", console_handler_level)

        for app_node in self.config_node.get_all_sub_nodes("application"):
            app_config_node = ConfigTree(app_node)
            assert app_config_node.get_node_name() == app_node.get("name"), "check failed"
            self.application = Application(self.work_dir, app_config_node)
            self.log.debug("created application: %s", app_node.get('name'))

        # Stores the task(s) created by the Execute method
        self.tasks = list()
        self.log.info("created simulation: %s", self.name)

    def execute(self, task_name=None):
        """
        This method allows for the execution of a simulation.
        """
        self.log.debug("start Execute(%s)", task_name)

        if task_name is not None:
            setup_task(self, task_name)
            for task in self.tasks:
                if task.get_name() == task_name:
                    task.execute(self.application)
                    self.log.debug("called task.Execute() on task %s", task_name)

        self.log.debug("end Execute(%s)", task_name)

    def __del__(self):
        self.log.info("destroyed simulation: %s", self.name)

#================================END SIMULATION CLASS DEFINITION================================
