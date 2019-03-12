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
This file contains the class definition of `ConfigTree`,
which aids in parsing the XML configuration files used
within the Cortix project.

Background
----------
An XML document consists of a collection of elements (nested or not). These elements
are containers of information and are the most important components of an XML
document. An element container is defined by a start tag and an end tag. A tag
starts with an opening angle bracket and finishes with a closing angle bracket as
follows
 + **element**: <ele_name> </ele_name>, *e.g*, <net_x> </net_x>.
Here `<net_x>` is the start tag and `</net_x>` is the end tag for the element named
`net_x`. An element with the same name can be used repeatedly in an XML document.
In `Cortix` we will use element names following the Python variable name snake
convention. It is also common to call the element name as the tag name. The start tag
of an element may have any number of atributes:
 + **attributes**: name='value', *e.g.*, <net_x mod_slot='wind:0'> </net_x>
these are name-value pairs; we will use the same name convention for element names
when creating attribute names. There may be many attributes in a start tag. Finally 
everything in between tags of an element, is considered as the element content:
 + **content**: <tag> content </tag>, *e.g.*, <net_x mod_slot='wind:0'>189.67 MeV</net_x>

Cortix: a program for system-level modules coupling, execution, and analysis.
'''
#*********************************************************************************
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ElementTree
#*********************************************************************************

class ConfigTree:
    '''
    This class generates objects that hold an ElementTree node of an XML tree
    structure. The level of the node depends on the argument passed when creating a
    `ConfigTree` object. If a node is passed, that node and all of its subnodes are held
    in a new tree. If a filename is passed, instead, an XML file is read and the root
    node is held at the top of the tree. A node is the same thing as an XML element as
    described in the Background above.
    '''

    def __init__(self, config_tree_node=None, config_file_name=None):

        # hold a given XML tree node
        if config_tree_node is not None:
            assert isinstance(config_tree_node, Element), '-> config_tree_node invalid.'
            self.__config_tree_node = config_tree_node

        # parse an XML tree and hold its root node
        if config_file_name is not None:
            assert isinstance(
                config_file_name, str), '-> configFileName not a str.'
            assert config_tree_node is None, 'node and file not allowed together.'

            tree = ElementTree()
            tree.parse(config_file_name)
            self.__config_tree_node = tree.getroot()

        return
# ---------------------- end def __init__():------------------------------

    def get_root_node(self):
        '''Returns the Element tree's root node'''

        return self.__config_tree_node
# ---------------------- end def get_root_node:():------------------------

    def get_node_tag(self):
        '''
        Returns the tag name associated with the root node of the element tree. This is
        the element name or tag name, *e.g.*, `<elem_name> </elem_name>`.

        Parameters
        ----------
        empty:

        Returns
        -------
        tag_name: str
        '''

        tag_name = self.__config_tree_node.tag
        assert isinstance(tag_name,str)

        return tag_name
# ---------------------- end def get_node_tag:():-------------------------

    def get_node_name(self):
        '''
        Returns the value of the `name` attribute associated with the root node of
        the element tree, *e.g.* <task name='solo-wind'></task>. This attribute 
        must exist.

        Parameters
        ----------
        empty:

        Returns
        -------
        attribute_value: str
        '''

        attribute_name  = 'name'
        attribute_value = self.__config_tree_node.get(attribute_name)

        assert attribute_value is not None
        assert isinstance(attribute_value,str)

        return attribute_value.strip()
# ---------------------- end def get_node_name:():------------------------

    def get_node_type(self):
        '''
        Returns the value of the `type` attribute associated with the root node of
        the element tree, *e.g.* <module type='native'></module>. This attribute
        must exist.

        Parameters
        ----------
        empty:

        Returns
        -------
        attribute_value: str
        '''

        attribute_name = 'type'
        attribute_value = self.__config_tree_node.get('type')

        assert attribute_value is not None
        assert isinstance(attribute_value,str)

        return attribute_value.strip()
# ---------------------- end def get_node_type:():------------------------

    def get_sub_node(self, tag):
        '''
        Returns a subnode of the element tree specified by the parameter tag.
        '''
        assert isinstance(tag, str), 'tag invalid'

        return self.__config_tree_node.find(tag)
# ---------------------- end def get_sub_node:():-------------------------

    def get_all_sub_nodes(self, tag):
        '''
        Returns a list of all nodes in the element tree with tag name.

        Parameters
        ----------
        tag: str
            XML element name or tag name, *e.g.* <task></task>
        Returns
        -------
        sub_nodes: list(Element)
            List of Element entries.
        '''

        assert isinstance(tag, str), 'tag invalid'

        return self.__config_tree_node.findall(tag)
# ---------------------- end def get_all_sub_nodes:():--------------------

    def get_node_children(self):
        '''
        Returns a list of the sub-elements in the given element (node) containing
        the subnode, the tag (element) name, the attributes a list of tuples,
        and the content (text) of the node. This is not recursive. Recursion
        can be done by calling this method on the children nodes (that is the first
        element of the tuple below).

        Parameters
        ----------
        empty:

        Returns
        -------
        children: list(tuple)
                  Tuple: (node, tag, [(attribute name,attribute value),(.,.)...],
                  content). Attribute name and value are string type.
        '''

        children = list()

        for child in self.__config_tree_node:

            children.append( (child, child.tag, child.items(), child.text) )

        return children
# ---------------------- end def get_note_children:():--------------------

# ====================== end class ConfigTree: =+++_======================
