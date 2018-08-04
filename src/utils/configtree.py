# -*- coding: utf-8 -*-

"""
This file contains the class definition of ConfigTree,
which aids in parsing the XML configuration files used
within the Cortix project.

Author: Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""

#*********************************************************************************
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ElementTree
#*********************************************************************************

#========================BEGIN CONFIG_TREE CLASS DEFINITION================================
class ConfigTree:

    """
    This class generates objects that hold an ElementTree node of an XML tree
    structure. The level of the node depends on the argument passed when creating the
    object. If a node is passed, that node and all its subnodes are held. If a
    filename is passed, instead, an XML file is read and the root node is held at the
    top of the tree.
    """

    def __init__(self, config_tree_node=None, config_file_name=None):
        if config_tree_node is not None:
            assert isinstance(config_tree_node, Element), "-> config_tree_node invalid."
            self.config_tree_node = config_tree_node

        if config_file_name is not None:
            assert isinstance(config_file_name, str), "-> configFileName not a str."
            assert config_tree_node is None, "node and file not allowed together."

            tree = ElementTree()
            tree.parse(config_file_name)
            self.config_tree_node = tree.getroot()

    def get_root_node(self):
        """Returns the Element tree's root node"""
        return self.config_tree_node

    def get_node_tag(self):
        """
        Returns the tag associated with the root node
        of the element tree.
        """
        return self.config_tree_node.tag

    def get_node_name(self):
        """
        Returns the name associated with the root
        node of the element tree
        """
        return self.config_tree_node.get('name')

    def get_node_type(self):
        """
        Returns the type associated with the root
        node of the element tree.
        """
        return self.config_tree_node.get('type')

    def get_sub_node(self, tag):
        """
        Returns a subnode of the element tree
        specified by the parameter tag.
        """
        assert isinstance(tag, str), 'tag invalid'
        return self.config_tree_node.find(tag)

    def get_all_sub_nodes(self, tag):
        """
        Returns a list of all nodes in the element
        tree that contain a given tag.
        """
        assert isinstance(tag, str), 'tag invalid'
        return self.config_tree_node.findall(tag)

    def get_node_children(self):
        """
        Returns a list of all the nodes in the
        element tree.
        """
        children = list()
        for child in self.config_tree_node:
            children.append((child, child.tag, child.items(), child.text))
        return children

#========================END CONFIG_TREE CLASS DEFINITION===========================

# Unit testing. Usage: -> python configtree.py
if __name__ == "__main__":
    print('Unit testing for ConfigTree')
    # TODO: FIX THE UNIT TEST, IT FAILS DUE TO THE LACK OF INPUT FILE
    ConfigTree(config_file_name="cortix-config.xml")
