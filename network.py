"""
This file contains the Network class definition
for the Cortix project. A network defines the 
connectivity between Cortix modules.

Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""

#*********************************************************************************
import networkx as nx
from cortix.utils.configtree import ConfigTree
#*********************************************************************************

#========================BEGIN NETWORK CLASS DEFINITION=========================
class Network:
    """
    Cortix network class definition. Defines the manner in which Modules interact.
    """
    def __init__(self, net_config_node=ConfigTree()):
        assert isinstance(net_config_node, ConfigTree), '-> net_config_node is invalid.'
        self.config_node = net_config_node
        self.name = self.config_node.get_node_name()
        self.connectivity = list(dict())
        self.slot_names = list()

        # cortix communication file for modules
        self.runtime_cortix_comm_file = dict()

        # network graph
        self.nx_graph = nx.MultiDiGraph(name=self.name)

        for child in self.config_node.get_node_children():
            (element, tag, attributes, text) = child
            if tag == 'connect':
                assert text is None, 'non empty text, %r, in %r network: ' % (text, self.name)

            tmp = dict()

            if tag == 'connect':
                for (key, value) in attributes:
                    assert key not in tmp.keys(), 'repeated key in attribute of %r network' \
                      % self.name
                    value = value.strip()
                    if key == 'fromModuleSlot':
                        value = value.replace(':', '_')
                    if key == 'toModuleSlot':
                        value = value.replace(':', '_')
                    tmp[key] = value
                self.connectivity.append(tmp)
                for (key, val) in tmp.items():
                    if key == 'fromModuleSlot':
                        self.runtime_cortix_comm_file[val] = 'null-runtimeCortixCommFile'
                    if key == 'toModuleSlot':
                        self.runtime_cortix_comm_file[val] = 'null-runtimeCortixCommFile'
                vtx1 = tmp['fromModuleSlot']
                vtx2 = tmp['toModuleSlot']
                self.nx_graph.add_edge(vtx1, vtx2,
                                       fromPort=tmp['fromPort'],
                                       toPort=tmp['toPort'])

        self.slot_names = [name for name in self.runtime_cortix_comm_file.keys()]

    def get_name(self):
        """
        Returns the network name
        """
        return self.name

    def get_connectivity(self):
        """
        Returns a list of the network connectivity
        """
        return self.connectivity

    def get_slot_names(self):
        """
        Returns a list of the network's slot names.
        """
        return self.slot_names

    def set_runtime_cortix_comm_file(self, slot_name, full_path_filename):
        """
        Sets the runtime cortix communications file to the one specified
        by full_path_filename
        """
        self.runtime_cortix_comm_file[slot_name] = full_path_filename

    def get_runtime_cortix_comm_file(self, slot_name):
        """
        Returns the cortix comm file that corresponds to slot_name.
        None if otherwise.
        """
        if slot_name in self.runtime_cortix_comm_file:
            return self.runtime_cortix_comm_file[slot_name]
        return None

    def get_nx_graph(self):
        """
        Returns the NXGraph corresponding the network
        """
        return self.nx_graph

    def __str__(self):
        """
        Network to string conversion
        """
        return 'Network data members: name=%5s' % (self.name)

    def __repr__(self):
        """
        Network to string conversion
        """
        return 'Network data members: name=%5s' % (self.name)

#========================END NETWORK CLASS DEFINITION=========================

# Unit testing. Usage: -> python network.py
if __name__ == "__main__":
    print('Unit testing for network')
