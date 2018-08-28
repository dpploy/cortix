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
"""
This file contains the class definition of ConfigTree,
which aids in parsing the XML configuration files used
within the Cortix project.

Cortix: a program for system-level modules coupling, execution, and analysis.
"""
# *********************************************************************************
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ElementTree
# *********************************************************************************


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
            assert isinstance(
                config_tree_node, Element), "-> config_tree_node invalid."
            self.config_tree_node = config_tree_node

        if config_file_name is not None:
            assert isinstance(
                config_file_name, str), "-> configFileName not a str."
            assert config_tree_node is None, "node and file not allowed together."

            tree = ElementTree()
            tree.parse(config_file_name)
            self.config_tree_node = tree.getroot()
# ---------------------- end def __init__():------------------------------

    def get_root_node(self):
        """Returns the Element tree's root node"""

        return self.config_tree_node
# ---------------------- end def get_root_node:():------------------------

    def get_node_tag(self):
        """
        Returns the tag associated with the root node
        of the element tree.
        """

        return self.config_tree_node.tag
# ---------------------- end def get_node_tag:():-------------------------

    def get_node_name(self):
        """
        Returns the name associated with the root
        node of the element tree
        """

        return self.config_tree_node.get('name')
# ---------------------- end def get_node_name:():------------------------

    def get_node_type(self):
        """
        Returns the type associated with the root
        node of the element tree.
        """

        return self.config_tree_node.get('type')
# ---------------------- end def get_node_type:():------------------------

    def get_sub_node(self, tag):
        """
        Returns a subnode of the element tree
        specified by the parameter tag.
        """
        assert isinstance(tag, str), 'tag invalid'

        return self.config_tree_node.find(tag)
# ---------------------- end def get_sub_node:():-------------------------

    def get_all_sub_nodes(self, tag):
        """
        Returns a list of all nodes in the element
        tree that contain a given tag.
        """
        assert isinstance(tag, str), 'tag invalid'

        return self.config_tree_node.findall(tag)
# ---------------------- end def get_all_sub_nodes:():--------------------

    def get_node_children(self):
        """
        Returns a list of all the nodes in the
        element tree.
        """

        children = list()
        for child in self.config_tree_node:
            children.append((child, child.tag, child.items(), child.text))

        return children
# ---------------------- end def get_note_children:():--------------------

# ====================== end class ConfigTree: =+++_======================
