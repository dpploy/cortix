# -*- coding: utf-8 -*-

"""
This file contains the Cortix Module class defintion.

Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""

#*********************************************************************************
import os
from mpi4py import MPI
from mpi4py.futures import MPIPoolExecutor
from cortix.utils.configtree import ConfigTree
from cortix.launcher import Launcher
#*********************************************************************************

#=================================BEGIN MODULE CLASS DEFINITION==========================
class Module:
    """
    This is the main class definition of the Cortix Module
    functionality.
    """
    def __init__(self, parent_work_dir=None, mod_lib_name=None, \
                 mod_lib_parent_dir=None, mod_config_node=ConfigTree()):

        assert isinstance(parent_work_dir, str), "-> parent_work_dir is invalid."

        # Inherit a configuration tree
        assert isinstance(mod_config_node, ConfigTree), "-> mod_config_node is invalid."
        self.config_node = mod_config_node

        # Read the module name and type
        self.mod_name = self.config_node.get_node_name()
        self.mod_type = self.config_node.get_node_type()

        # Specify module library with upstream information (override in _Setup() if needed)
        self.mod_lib_parent_dir = mod_lib_parent_dir
        self.mod_lib_name = mod_lib_name

        self.executable_name = 'null-executableName'
        self.executable_path = 'null-executablePath'
        self.input_file_name = 'null-inputFileName'
        self.input_file_path = 'null-inputFilePath'

        self.ports = list()  # list of (portName, portType, portMultiplicity)

        # Save config data
        for child in self.config_node.get_node_children():
            (elem, tag, attributes, text) = child
            text = text.strip()

            if self.mod_type != 'native':
                if tag == 'executableName':
                    self.executable_name = text

            if tag == 'executablePath':
                if text[-1] != '/':
                    text += '/'
                self.executable_path = text

            if tag == 'inputFileName':
                self.input_file_name = text

            if tag == 'inputFilePath':
                if text[-1] != '/':
                    text += '/'
                self.input_file_path = text

            if tag == 'library':
                assert len(attributes) == 1, 'only name of library allowed.'
                key = attributes[0][0]
                assert key == 'name', 'invalid attribute.'
                val = attributes[0][1].strip()
                self.mod_lib_name = val

                node = ConfigTree(elem)
                sub_node = node.get_sub_node('parentDir')
                assert sub_node is not None, 'missing parentDir.'

                self.mod_lib_parent_dir = sub_node.text.strip()

                if self.mod_lib_parent_dir[-1] == '/':
                    self.mod_lib_parent_dir.strip('/')

            if tag == 'port':
                assert len(attributes) == 3, "only <= 3 attributes allowed."

                tmp = dict() # store port name and three attributes

                for attribute in attributes:
                    key = attribute[0]
                    val = attribute[1].strip()

                    if key == 'type':
                        assert val == 'use' or val == 'provide' or val == 'input' or \
                        val == 'output', 'port attribute value invalid.'
                        tmp['portName'] = text  # portName
                        tmp['portType'] = val   # portType
                    elif key == 'mode':
                        file_value = val.split('.')[0]
                        assert file_value == 'file' or file_value == 'directory',\
                        'port attribute value invalid.'
                        tmp['portMode'] = val
                    elif key == 'multiplicity':
                        tmp['portMultiplicity'] = int(val)  # portMultiplicity
                    else:
                        assert False, 'invalid port attribute. fatal.'

                assert len(tmp) == 4
                store = (tmp['portName'], tmp['portType'], tmp['portMode'], \
                         tmp['portMultiplicity'])
                self.ports.append(store) # (portName, portType, portMode, portMultiplicity)
                tmp = None
                store = None

    def get_name(self):
        """
        Returns the module name
        """
        return self.mod_name

    def get_library_name(self):
        """
        Returns the module's library name.
        """
        return self.mod_lib_name

    def get_library_parent_dir(self):
        """
        Returns the library's parent directory.
        """
        return self.mod_lib_parent_dir

    def get_ports(self):
        """
        Returns a list of the module's ports.
        """
        return self.ports

    def get_port_type(self, port_name):
        """
        Retuns the port type specified by port_name
        """
        port_type = None
        for port in self.ports:
            if port[0] == port_name:
                port_type = port[1]
        return port_type

    def get_port_mode(self, port_name):
        """
        Returns the port mode specified by port_name
        """
        port_mode = None
        for port in self.ports:
            if port[0] == port_name:
                port_mode = port[2]
        return port_mode

    def get_port_names(self):
        """
        Returns a list containing the name of all of the module's ports
        """
        port_names = list()
        for port in self.ports:
            port_names.append(port[0])
        return port_names

    def has_port_name(self, port_name):
        """
        Returns true iff a port with the name
        port_name is available in the module.
        """
        for port in self.ports:
            if port[0] == port_name:
                return True
        return False

    def execute(self, slot_id, runtime_cortix_param_file, runtime_cortix_comm_file):
        """
        Spawns a worker process to execute the module.
        """
        module_input = self.input_file_path + self.input_file_name
        param = runtime_cortix_param_file
        comm = runtime_cortix_comm_file

        full_path_comm_dir = comm[:comm.rfind('/')]+'/'
        runtime_module_status_file = full_path_comm_dir + 'runtime-status.xml'

        status = runtime_module_status_file

        mod_lib_name = self.mod_lib_name
        mod_name = self.mod_name

        # provide for all modules for additional work IO data
        assert os.path.isdir(full_path_comm_dir), 'module directory not available.'
        mod_work_dir = full_path_comm_dir + 'wrk/'

        os.system('mkdir -p ' + mod_work_dir)

        assert os.path.isdir(mod_work_dir), 'module work directory not available.'

        # only for wrapped modules
        mod_exec_name = self.executable_path + self.executable_name

        # run module on its own thread using file IO communication
        worker_thread = Launcher(mod_lib_name, mod_name,
                                 slot_id,
                                 module_input,
                                 mod_exec_name,
                                 mod_work_dir,
                                 param, comm, status)

        # Launch an MPI process
        print("Spawning a process...")
        executor = MPIPoolExecutor(max_workers=1)
        future = executor.submit(worker_thread.start())
        print("Finished spawning process...")
        
        return runtime_module_status_file

#=================================END MODULE CLASS DEFINITION==========================
