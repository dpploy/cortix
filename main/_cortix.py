"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import datetime
import logging
from cortix.utils.configtree import ConfigTree
from cortix.simulation.interface import Simulation
from ._setupsimulations import _SetupSimulations
#*********************************************************************************

class Cortix:
    def __init__(self, name=None, config_file="cortix-config.xml"):

        assert name is not None, "must give Cortix object a name"

        assert isinstance(config_file, str), "-> configFile not a str."
        self.config_file = config_file

        # Create a configuration tree
        self.config_tree = ConfigTree(configFileName=self.config_file)

        # Read this object's name
        node = self.config_tree.GetSubNode("name")
        self.name = node.text.strip()

        # check
        assert self.name == name,\
        "Cortix object name %r conflicts with cortix-config.xml %r" % (self.name, name)

        # Read the work directory name
        node = self.config_tree.GetSubNode("workDir")
        work_dir = node.text.strip()
        if work_dir[-1] != '/':
            work_dir += '/'

        self.work_dir = work_dir + self.name + "-wrk/"

        # Create the work directory
        if os.path.isdir(self.work_dir):
            os.system('rm -rf ' + self.work_dir)

        os.system('mkdir -p ' + self.work_dir)

        # Create the logging facility for each object
        node = self.config_tree.GetSubNode("logger")
        logger_name = self.name
        log = logging.getLogger(logger_name)
        log.setLevel(logging.NOTSET)

        logger_level = node.get("level").strip()
        self.set_logger_level(log, logger_name, logger_level)

        file_handler = logging.FileHandler(self.work_dir + "cortix.log")
        file_handler.setLevel(logging.NOTSET)
        file_handler_level = None

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.NOTSET)
        console_handler_level = None

        for child in node:
            if child.tag == "fileHandler":
                file_handler_level = child.get("level").strip()
                self.set_logger_level(file_handler, logger_name, file_handler_level)
            if child.tag == "consoleHandler":
                console_handler_level = child.get("level").strip()
                self.set_logger_level(console_handler, logger_name, console_handler_level)

        # Formatter added to handlers
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # add handlers to logger
        log.addHandler(file_handler)
        log.addHandler(console_handler)

        self.log = log
        self.log.info("Created Cortix logger: %s", self.name)
        self.log.debug("Logger level: %s", logger_level)
        self.log.debug("Logger file handler level: %s", file_handler_level)
        self.log.debug("Logger console handler level: %s", console_handler_level)
        self.log.info("Created Cortix work directory: %s", self.work_dir)

        # Setup simulations (one or more as specified in the config file)
        self.simulations = list()
        _SetupSimulations(self)

        self.log.info("Created Cortix object %s", self.name)

    def set_logger_level(self, handler, handler_name, handler_level):
        """
        This is a helper function for the constructor that
        takes in a file/console handler and sets its level
        accordingly.
        """

        if handler_level == 'DEBUG':
            handler.setLevel(logging.DEBUG)
        elif handler_level == 'INFO':
            handler.setLevel(logging.INFO)
        elif handler_level == 'WARN':
            handler.setLevel(logging.WARN)
        elif handler_level == 'ERROR':
            handler.setLevel(logging.ERROR)
        elif handler_level == 'CRITICAL':
            handler.setLevel(logging.CRITICAL)
        elif handler_level == 'FATAL':
            handler.setLevel(logging.FATAL)
        else:
            assert False, "File handler log level for %r: %r invalid"\
            % (handler_name, handler_level)

        return handler

    
    def run_simulations(self, task_name=None):
        """
        This method runs every simulation
        defined by the Cortix object.
        """
        for sim in self.simulations:
            sim.Execute(task_name)

    def __del__(self):
        self.log.info("Destroyed Cortix object: %s", self.name)

#*********************************************************************************

# Unit testing. Usage: -> python cortix.py
if __name__ == "__main__":
    print('Unit testing for Cortix')
    Cortix("cortix-config.xml")
