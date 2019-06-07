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
    Cortix Network class definition. Network class members:

    __config_xml_node: XMLTree
        Configuration data in the form of an XML tree.

    __name: str
        Name of the network.

    __connectivity: list(dict)
        List of dictionaries of connectivity. Dictionary:
        {'use_module_slot': module_slot_name, 'use_port': use_port_name, 'provide_module_slot': module_slot_name, 'provide_port': provide_port_name}.

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

    def __init__(self, net_config_xml_node):

        assert isinstance(net_config_xml_node, XMLTree),\
               '-> net_config_xml_node is invalid.'

        self.__config_xml_node = net_config_xml_node

        assert self.__config_xml_node.tag == 'network'

        self.__name = self.__config_xml_node.get_attribute('name')

        self.__connectivity = list( dict() )

        self.__module_slot_names = list()

        # Cortix communication files for modules.
        self.__runtime_cortix_comm_file_name = dict()

        # Network graph.
        self.__nx_graph = nx.MultiDiGraph(name=self.__name)

        # Loop over the connect xml tags.
        for child in self.__config_xml_node.children:

            (element, tag, attributes, text) = child

            # A connect element must have no content; format: <connect />
            if tag == 'connect':
                assert text is None, 'non empty text, %r, in %r network: '%\
                        (text, self.__name)

                tmp = dict() # of connect attributes

                for (key, value) in attributes:

                    assert key == 'use_port' or key == 'provide_port',\
                            'illegal port type %r'%key

                    assert key not in tmp.keys(), \
                        'repeated key in attribute of %r network'%self.__name

                    value = value.strip()

                    if key == 'use_port':
                        data = value.split('@')
                        assert len(data) == 2
                        use_port = data[0].strip()
                        use_module_slot = data[1].strip().replace(':','_')
                        assert use_port not in tmp.keys(), \
                            'repeated use_port in attribute of %r network' %\
                            self.__name
                        tmp['use_port'] = use_port
                        assert use_module_slot not in tmp.keys(), \
                            'repeated use_module_slot in attribute of %r network' %\
                            self.__name
                        tmp['use_module_slot'] = use_module_slot

                    if key == 'provide_port':
                        data = value.split('@')
                        assert len(data) == 2
                        provide_port = data[0].strip()
                        provide_module_slot = data[1].strip().replace(':','_')
                        assert provide_port not in tmp.keys(),\
                                'repeated provide_port in attribute of %r network' %\
                            self.__name
                        tmp['provide_port'] = provide_port
                        assert provide_module_slot not in tmp.keys(), \
                            'repeated provide_module_slot in attribute of %r network' %\
                            self.__name
                        tmp['provide_module_slot'] = provide_module_slot

                self.__connectivity.append( tmp )

                # initialize the runtime comm file for each module_slot
                for (key, val) in tmp.items():
                    if key == 'use_module_slot' or key == 'provide_module_slot':
                        self.__runtime_cortix_comm_file_name[val] = \
                            'null-runtime_cortix_comm_file_name'

                vtx1 = tmp['use_module_slot']
                vtx2 = tmp['provide_module_slot']

                self.__nx_graph.add_edge(vtx1, vtx2, use_port=tmp['use_port'],
                        provide_port=tmp['provide_port'])

        self.__module_slot_names = [name for name in
                                    self.__runtime_cortix_comm_file_name.keys()]

        return

#*********************************************************************************
# Public member functions 
#*********************************************************************************

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

    def set_runtime_cortix_comm_file_name(self, module_slot_name, full_path_file_name):
        '''
        Sets the runtime cortix communications file to the one specified
        by full_path_file_name
        '''

        self.__runtime_cortix_comm_file_name[module_slot_name] = full_path_file_name

        return

    def get_runtime_cortix_comm_file_name(self, module_slot_name):
        '''
        Returns the cortix communication file name (full path) that corresponds to
        module_slot_name. None if otherwise.

        Parameters
        ----------
        module_slot_name: str

        Returns
        -------
        full_path_file_name: str or None
        '''

        if module_slot_name in self.__runtime_cortix_comm_file_name:
            full_path_file_name = self.__runtime_cortix_comm_file_name[module_slot_name]
        else:
            full_path_file_name = None

        return full_path_file_name

    def get_runtime_port_comm_file(self, module_slot_name, port_name):
        '''
        From the Cortix runtime communication file search for the module and port
        given, and return the file associated to the specified arguments.

        Parameters
        ----------
        module_slot_name: str

        port_name: str

        Returns
        -------
        full_path_file_name: str or None
        '''

        assert module_slot_name in self.__runtime_cortix_comm_file_name

        comm_file = self.__runtime_cortix_comm_file_name[module_slot_name]
        comm_xml_tree = XMLTree(xml_tree_file=comm_file)

        data_file_name = None

        for child in comm_xml_tree.children:
            (node,name,attributes,content) = child
            (name,value) = attributes[0] # order: 0: (name,:) 1: (type,:) 2: (file,:)
            if value == port_name:
                data_file_name = attributes[-1][1] # (file,:)
                break

        # If the data file name is not found, it is not in the comm file.
        assert data_file_name is not None,'port name: %r not in runtime cortix comm file %r'%(port_name, comm_file)

        return data_file_name # full path

    def __str__(self):
        '''
        Network to string conversion used in a print statement.
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
