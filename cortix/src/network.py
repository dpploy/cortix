#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/cortix
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/cortix/blob/master/COPYRIGHT.txt
#
# Licensed under the GNU General Public License v. 3, please see LICENSE file.
# https://www.gnu.org/licenses/gpl-3.0.txt
'''
Network class for the Cortix project. A network defines the connectivity between
Cortix modules.

Cortix: a program for system-level modules coupling, execution, and analysis.
'''
#*********************************************************************************
import networkx as nx
from cortix.src.utils.configtree import ConfigTree
#*********************************************************************************

class Network:
    '''
    Cortix network class definition. Defines the manner in which Modules interact.
    '''

    def __init__(self, net_config_node=ConfigTree()):

        assert isinstance(net_config_node, ConfigTree), \
            '-> net_config_node is invalid.'

        self.__config_node = net_config_node
        self.__name = self.__config_node.get_node_name()
        self.__connectivity = list(dict())
        self.__slot_names = list()

        # cortix communication file for modules
        self.__runtime_cortix_comm_file = dict()

        # network graph
        self.__nx_graph = nx.MultiDiGraph(name=self.__name)

        for child in self.__config_node.get_node_children():
            (element, tag, attributes, text) = child
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
                        self.__runtime_cortix_comm_file[val] = \
                            'null-runtime_cortix_comm_file'
                    if key == 'toModuleSlot':
                        self.__runtime_cortix_comm_file[val] = \
                            'null-runtime_cortix_comm_file'
                vtx1 = tmp['fromModuleSlot']
                vtx2 = tmp['toModuleSlot']
                self.__nx_graph.add_edge(vtx1, vtx2,
                                       fromPort=tmp['fromPort'],
                                       toPort=tmp['toPort'])

        self.__slot_names = [
            name for name in self.__runtime_cortix_comm_file.keys()]
#----------------------- end def __init__():--------------------------------------

    def __get_name(self):
        '''
        `str`:Network name
        '''

        return self.__name
    name = property(__get_name, None, None, None)
#----------------------- end def get_name():--------------------------------------

    def __get_connectivity(self):
        '''
        `list(dict)`:List of the network connectivity
        '''

        return self.__connectivity
    connectivity = property(__get_connectivity, None, None, None)
#----------------------- end def get_connectivity():------------------------------

    def __get_slot_names(self):
        '''
        `list(str)`:List of network slot names
        '''

        return self.__slot_names
    slot_names = property(__get_slot_names, None, None, None)
#----------------------- end def get_slot_names():--------------------------------

    def set_runtime_cortix_comm_file(self, slot_name, full_path_file_name):
        '''
        Sets the runtime cortix communications file to the one specified
        by full_path_file_name
        '''

        self.__runtime_cortix_comm_file[slot_name] = full_path_file_name
#----------------------- end def set_runtime_cortix_comm_file():------------------

    def get_runtime_cortix_comm_file(self, slot_name):
        '''
        Returns the cortix comm file that corresponds to slot_name.
        None if otherwise.
        '''

        if slot_name in self.__runtime_cortix_comm_file:
            return self.__runtime_cortix_comm_file[slot_name]
        return None
#----------------------- end def get_runtime_cortix_comm_file():------------------

    def __get_nx_graph(self):
        '''
        `str`:NXGraph corresponding to network
        '''

        return self.__nx_graph
    nx_graph = property(__get_nx_graph, None, None, None)
#----------------------- end def get_nx_graph():----------------------------------

    def __str__(self):
        '''
        Network to string conversion
        '''
        s = 'Network data members:\n name=%s\n slot names=%s\n connectivity=%s\n runtime comm file= %s'
        return s % (self.__name, self.__slot_names, self.__connectivity, 
                    self.__runtime_cortix_comm_file)
#----------------------- end def __str__():---------------------------------------

        self.__runtime_cortix_comm_file = dict()
    def __repr__(self):
        '''
        Network to string conversion
        '''

        s = 'Network data members:\n name=%s\n slot names=%s\n connectivity=%s\n runtime comm file= %s'
        return s % (self.__name, self.__slot_names, self.__connectivity, 
                    self.__runtime_cortix_comm_file)
#----------------------- end def __repr__():--------------------------------------

#======================= end class Network: ======================================
