# -*- coding: utf-8 -*-

"""
This File contains the main Cortix class definition.

Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

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


#========================BEGIN CORTIX CLASS DEFINITION================================

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
        "Cortix object name %r conflicts with cortix-config.xml %r" % (self.name, name)

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
                file_handler = set_logger_level(file_handler, logger_name, file_handler_level)
            if child.tag == "consoleHandler":
                console_handler_level = child.get("level").strip()
                console_handler = set_logger_level(console_handler, logger_name, console_handler_level)

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
        self.setup_simulations()

        self.log.info("Created Cortix object %s", self.name)

    def run_simulations(self, task_name=None):
        """
        This method runs every simulation
        defined by the Cortix object.
        """
        for sim in self.simulations:
            sim.execute(task_name)

    def setup_simulations(self):
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

    def __del__(self):
        self.log.info("Destroyed Cortix object: %s", self.name)

#========================END CORTIX CLASS DEFINITION==================================

#=============================BEGIN SETUP_TASK=====================================
def setup_task(self, task_name):
    """
    This is a helper function used by the execute function in
    the simulation to constructor. It serves to setup the
    set of tasks defined in the Cortix config.
    """
    self.log.debug("start _SetupTask()")
    task = None

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    cmode = MPI.MODE_WRONLY|MPI.MODE_CREATE
    amode = MPI.MODE_WRONLY|MPI.MODE_APPEND

    for task_node in self.config_node.get_all_sub_nodes('task'):
        if task_node.get('name') != task_name:
            continue

        task_config_node = ConfigTree(task_node)
        task = Task(self.work_dir, task_config_node)
        self.tasks.append(task)

        self.log.debug("appended task: %s", task_node.get("name"))

    if task is None:
        self.log.debug('no task to exectute; done here.')
        self.log.debug('end setup_task')
        return

    networks = self.application.get_networks()

    # create subdirectory with task name
    task_name = task.get_name()
    task_work_dir = task.get_work_dir()
    assert os.path.isdir(task_work_dir), "directory %r invalid." % task_work_dir

    # set the parameters for the task in the cortix param file
    task_file = task_work_dir + 'cortix-param.xml'

    fout = MPI.File.Open(comm, task_file, cmode)
    fout.Write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
    fout.Write(b'<!-- Written by Simulation::_Setup() -->\n')
    fout.Write(b'<cortixParam>\n')
    start_time = task.get_start_time()
    start_time_unit = task.get_start_time_unit()
    fout.Write("".join('<startTime unit="'+start_time_unit+'"'+'>'+str(start_time)+'</startTime>\n').encode())
    evolve_time = task.get_evolve_time()
    evolve_time_unit = task.get_evolve_time_unit()
    fout.Write("".join('<evolveTime unit="'+evolve_time_unit+'"'+'>'+str(evolve_time)+'</evolveTime>\n').encode())
    time_step = task.get_time_step()
    time_step_unit = task.get_time_step_unit()
    fout.Write("".join('<timeStep unit="'+time_step_unit+'"'+'>'+str(time_step)+'</timeStep>\n').encode())
    fout.Write(b'</cortixParam>')
    fout.Close()
    task.set_runtime_cortix_param_file(task_file)

    # using the tasks and network create the runtime module directories and comm files
    for net in networks:
        if net.get_name() == task_name: # Warning: net and task name must match
            connect = net.get_connectivity()
            to_module_to_port_visited = dict()
            for con in connect:
                # Start with the ports that will function as a provide port or input port
                to_module_slot = con['toModuleSlot']
                to_port = con['toPort']

                if to_module_slot not in to_module_to_port_visited.keys():
                    to_module_to_port_visited[to_module_slot] = list()

                to_module_name = to_module_slot.split('_')[0]
                to_module = self.application.get_module(to_module_name)

                assert to_module is not None, \
                  'module %r does not exist in application' % to_module_name

                assert to_module.has_port_name(to_port), \
                  'module %r has no port %r.' % (to_module.get_name(), to_port)

                assert to_module.get_port_type(to_port) is not None,\
                  'network name: %r, module name: %r, to_port: %r port type invalid %r' %(\
                  net.get_name(), to_module.get_name(), to_port, type(to_module.get_port_type(to_port)))

                to_module_slot_work_dir = task_work_dir + to_module_slot + '/'

                if to_module.get_port_type(to_port) != 'input':
                    assert to_module.get_port_type(to_port) == 'provide', \
                      'port type %r invalid. Module %r, port %r' \
                      % (to_module.get_port_type(to_port), to_module.get_name(), to_port)

                # "to" is who receives the "call", hence the provider
                to_module_slot_comm_file = to_module_slot_work_dir + 'cortix-comm.xml'

                if not os.path.isdir(to_module_slot_work_dir):
                    os.system("mkdir -p " + to_module_slot_work_dir)

                if not os.path.isfile(to_module_slot_comm_file):
                    fout = MPI.File.Open(comm, to_module_slot_comm_file, cmode)
                    fout.Write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
                    fout.Write(b'<!-- Written by Simulation::_Setup() -->\n')
                    fout.Write(b'<cortixComm>\n')

                if to_port not in to_module_to_port_visited[to_module_slot]:
                    fout = MPI.File.Open(comm, to_module_slot_comm_file, amode)
                    # this is the cortix info for modules providing data
                    to_port_mode = to_module.get_port_mode(to_port)
                    if to_port_mode.split('.')[0] == 'file':
                        ext = to_port_mode.split('.')[1]
                        log_str = '<port name="'+to_port+'" type="provide" file="'\
                                               +to_module_slot_work_dir+to_port+'.'+ext+'"/>\n'
                    elif to_port_mode == 'directory':
                        log_str = '<port name="'+to_port+'" type="provide" directory="'+\
                                               to_module_slot_work_dir+to_port+'"/>\n'
                    else:
                        assert False, 'invalid port mode. fatal.'

                    fout.Write(log_str.encode())
                    fout.Close()
                    to_module_to_port_visited[to_module_slot].append(to_port)

                debug_str = '_Setup():: comm module: ' + to_module_slot + '; network: '\
                            + task_name + ' ' + log_str
                self.log.debug(debug_str)

                # register the cortix-comm file for the network
                net.set_runtime_cortix_comm_file(to_module_slot, to_module_slot_comm_file)

                # Now do the ports that will function as use ports
                from_module_slot = con['fromModuleSlot']
                from_port = con['fromPort']
                from_module_name = from_module_slot.split('_')[0]
                from_module = self.application.get_module(from_module_name)

                assert from_module.has_port_name(from_port), 'module %r has no port %r'\
                  % (from_module_name, from_port)

                assert from_module.get_port_type(from_port) is not None, \
                  'network name: %r, module name: %r, from_port: %r port type invalid %r'\
                  % (net.get_name(), from_module.get_name(), from_port, \
                     type(from_module.get_port_type(from_port)))

                from_module_slot_work_dir = task_work_dir + from_module_slot + '/'

                if from_module.get_port_type(from_port) != 'output':
                    assert from_module.get_port_type(from_port) == 'use', \
                      'port type %r invalid. Module %r, port %r'\
                      % (from_module.get_port_type(from_port), from_module.get_name(), from_port)

                    # "from" is who makes the "call", hence the user
                    from_module_slot_comm_file = from_module_slot_work_dir + 'cortix-comm.xml'

                    if not os.path.isdir(from_module_slot_work_dir):
                        os.system('mkdir -p '+ from_module_slot_work_dir)

                    if not os.path.isfile(from_module_slot_comm_file):
                        fout = MPI.File.Open(comm, from_module_slot_comm_file, cmode)
                        fout.Write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
                        fout.Write(b'<!-- Written by Simulation::_Setup() -->\n')
                        fout.Write(b'<cortixComm>\n')
                        fout.Close()

                    fout = MPI.File.Open(comm, from_module_slot_comm_file, amode)

                    # this is the cortix info for modules using data
                    assert from_module.get_port_type(from_port) == 'use', 'from_port must be use type.'

                    to_port_mode = to_module.get_port_mode(to_port)
                    if to_port_mode.split('.')[0] == 'file':
                        ext = to_port_mode.split('.')[1]
                        log_str = '<port name="' + from_port + '" type="use" file="' + \
                                  to_module_slot_work_dir + to_port +'.' + ext + '"/>\n'
                    elif to_port_mode == 'directory':
                        log_str = '<port name="' + from_port + '" type="use" directory="' + \
                                  to_module_slot_work_dir + to_port + '"/>\n'
                    else:
                        assert False, 'invalid port mode. fatal.'

                    fout.Write(log_str.encode())
                    fout.Close()

                    debug_str = "_Setup():: comm module: " + from_module_slot + '; network: '\
                                + task_name + ' ' + log_str
                    self.log.debug(debug_str)

            # register the cortix-comm file for the network
            net.set_runtime_cortix_comm_file(from_module_slot, from_module_slot_comm_file)

    # finish forming the XML documents for port types
    for net in networks:
        slot_names = net.get_slot_names()
        for slot_name in slot_names:
            comm_file = net.get_runtime_cortix_comm_file(slot_name)
            if comm_file == 'null-runtimeCortixCommFile':
                continue
            fout = MPI.File.Open(comm, comm_file, amode)
            fout.Write(b'</cortixComm>')
            fout.Close()

    self.log.debug('end _Setup()')

#======================================END SETUP_TASK==================================
# Unit testing. Usage: -> python cortix.py
if __name__ == "__main__":
    # TODO: THIS FAILS SINCE THERE DOES NOT EXIST A cortix-config.xml
    print('Unit testing for Cortix')
    Cortix("cortix-config.xml")
