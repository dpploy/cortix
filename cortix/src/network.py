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
Network class for the Cortix project. A network defines the connectivity between
Cortix modules.

Cortix: a program for system-level modules coupling, execution, and analysis.
'''
#*********************************************************************************
import networkx as nx
from cortix.src.utils.xmltree import XMLTree
#*********************************************************************************

class Network:
    '''
    Cortix network class definition. Network class members:

    __config_node: XMLTree
        Configuration data in the form of an XML tree.

    __name:str
        Name of the network.

    __connectivity: list(dict)
        List of dictionaries of connectivity. Dictionary:
        {'fromModuleSlot': module_slot_name, 'fromPort': use_port_name, 'toModuleSlot': module_slot_name, 'toPort': provide_port_name}.

    __module_slot_names: list(str)
        List of names of module slots.

    __runtime_cortix_comm_file_name: dict
        Full path filename of the communication file for each module slot.
        {module_slot_name:full_path_comm_file_name, .:., .:., ...}.
        This is initially filled with a null filename at construction time. Later,
        Simulation.__setup_task() will fill in the information.

    __nx_graph:

    '''

#*********************************************************************************
# Construction 
#*********************************************************************************

    def __init__(self, net_config_node): 
        assert isinstance(net_config_node, XMLTree), '-> net_config_node is invalid.'

        self.__config_node = net_config_node

        assert self.__config_node.get_node_tag() == 'network'

        self.__name = self.__config_node.get_node_attribute('name')

        self.__connectivity = list(dict())
        self.__module_slot_names = list()

        # cortix communication file for modules
        self.__runtime_cortix_comm_file_name = dict()

        # network graph
        self.__nx_graph = nx.MultiDiGraph(name=self.__name)

        for child in self.__config_node.get_node_children():

            (element, tag, attributes, text) = child

            # a connect element must have no content; format: <connect />
            if tag == 'connect':
                assert text is None, 'non empty text, %r, in %r network: ' \
                    % (text, self.__name)

            tmp = dict()

            if tag == 'connect':

                for (key, value) in attributes:
                    assert key not in tmp.keys(), \
                        'repeated key in attribute of %r network' % self.__name
                    value = value.strip()
                    if key == 'fromModuleSlot':
                        value = value.replace(':', '_')
                    if key == 'toModuleSlot':
                        value = value.replace(':', '_')
                    tmp[key] = value

                self.__connectivity.append(tmp)

                for (key, val) in tmp.items():
                    if key == 'fromModuleSlot':
                        self.__runtime_cortix_comm_file_name[val] = \
                            'null-runtime_cortix_comm_file_name'
                    if key == 'toModuleSlot':
                        self.__runtime_cortix_comm_file_name[val] = \
                            'null-runtime_cortix_comm_file_name'
                vtx1 = tmp['fromModuleSlot']
                vtx2 = tmp['toModuleSlot']

                self.__nx_graph.add_edge(vtx1, vtx2,
                    fromPort=tmp['fromPort'], toPort=tmp['toPort'])

        self.__module_slot_names = [name for name in self.__runtime_cortix_comm_file_name.keys()]

        return

#*********************************************************************************
# Public member functions 
#*********************************************************************************

    def set_runtime_cortix_comm_file_name(self, module_slot_name, full_path_file_name):
        '''
        Sets the runtime cortix communications file to the one specified
        by full_path_file_name
        '''

        self.__runtime_cortix_comm_file_name[module_slot_name] = full_path_file_name

        return

    def get_runtime_cortix_comm_file_name(self, module_slot_name):
        '''
        Returns the cortix comm file that corresponds to module_slot_name. None if otherwise.
        '''

        if module_slot_name in self.__runtime_cortix_comm_file_name:
            return self.__runtime_cortix_comm_file_name[module_slot_name]
        else:
            return None

    def __get_name(self):
        '''
        `str`:Network name
        '''

        return self.__name

    name = property(__get_name, None, None, None)

    def __get_connectivity(self):
        '''
        `list(dict)`:List of the network connectivity
        '''

        return self.__connectivity

    connectivity = property(__get_connectivity, None, None, None)

    def __get_module_slot_names(self):
        '''
        `list(str)`:List of network slot names
        '''

        return self.__module_slot_names

    module_slot_names = property(__get_module_slot_names, None, None, None)

    def __get_nx_graph(self):
        '''
        `networkx.MultiDiGraph`:NXGraph corresponding to network
        '''

        return self.__nx_graph

    nx_graph = property(__get_nx_graph, None, None, None)

    def __str__(self):
        '''
        Network to string conversion
        '''

        s = 'Network data members:\n name=%s\n module slot names=%s\n connectivity=%s\n runtime comm file= %s'
        return s % (self.__name, self.__module_slot_names, self.__connectivity,
                    self.__runtime_cortix_comm_file_name)

    def __repr__(self):
        '''
        Network to string conversion
        '''

        s = 'Network data members:\n name=%s\n module slot names=%s\n connectivity=%s\n runtime comm file= %s'
        return s % (self.__name, self.__module_slot_names, self.__connectivity,
                    self.__runtime_cortix_comm_file_name)

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

#======================= end class Network: ======================================
