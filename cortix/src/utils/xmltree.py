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
This file contains the class definition of `XMLTree`,
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
from xml.etree.ElementTree import ElementTree # the whole XML tree data structure
from xml.etree.ElementTree import Element     # an XML element or tree node
#*********************************************************************************

class XMLTree:
    '''
    This class is a wrapper around the XML parser ElementTree and Element. See
    import statement above. This XML parser is fast but the interface is not very
    user friendly; hence the motivation for this wrapper.
    The interface is designed to facilitate the use of XML data within Cortix and
    its modules. This class generates objects that hold an XML tree: ElementTree.
    Configuration of Cortix and some runtime files are the primary usage of XMLTree.
    The construction of an XMLTree object either uses a file with an XML content or
    an XML branch of an XML tree. This makes it useful throughout Cortix to inspect
    branches of a configuration XML tree to retrieve data.
    A node in a tree is the root of a branch. That is, the same thing as an XML
    element and all its direct sub-elements; described in the Background above.
    '''

#*********************************************************************************
# Construction
#*********************************************************************************

    def __init__(self, xml_tree_node=None, xml_tree_file=None):
        '''
        Overall description of the constructor
        '''

        # hold a given XML tree node
        if xml_tree_node is not None:
            assert isinstance(xml_tree_node, Element), '-> xml_tree_node invalid.'
            tag_name = xml_tree_node.tag
            assert isinstance(tag_name,str)
            assert len(tag_name) > 0

            self.__xml_tree_node = xml_tree_node

        # parse an XML tree and hold its root node
        if xml_tree_file is not None:
            assert isinstance(xml_tree_file, str), '-> xml_tree_file not a str.'
            assert xml_tree_node is None, 'node and file not allowed together.'

            tree = ElementTree()
            tree.parse( xml_tree_file )

            self.__xml_tree_node = tree.getroot()

        return

#*********************************************************************************
# Public member functions
#*********************************************************************************

    def get_root_node(self):
        '''
        Returns the Element tree's root node.

        Parameters
        ----------
        empty:

        Returns
        -------
        self.__xml_tree_node: Element
        '''

        return self.__xml_tree_node

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

        tag_name = self.__xml_tree_node.tag
        assert isinstance(tag_name,str)

        return tag_name

    def get_node_attribute(self, attribute_name):
        '''
        Returns the value of the attribute associated with the root node of
        the element tree, *e.g.* <module type='native'></module>. Attribute
        name is `type`, value is 'native'.

        Parameters
        ----------
        attribute_name: str

        Returns
        -------
        attribute_value: str
        '''

        assert isinstance(attribute_name,str)
        attribute_value = self.__xml_tree_node.get(attribute_name.strip())

        assert attribute_value is not None
        assert isinstance(attribute_value,str)

        return attribute_value.strip()

    def get_attribute(self, attribute_name):
        '''
        Returns the value of the attribute associated with the root node of
        the element tree, *e.g.* <module type='native'></module>. Attribute
        name is `type`, value is 'native'.

        Parameters
        ----------
        attribute_name: str

        Returns
        -------
        attribute_value: str or None
        '''

        assert isinstance(attribute_name,str)
        attribute_value = self.__xml_tree_node.get(attribute_name.strip())

        if attribute_value is not None:
            return attribute_value.strip()
        else:
            return attribute_value

    def get_node_content(self):
        '''
        Returns the content or text of the XML element.This is what is in between
        the start and end tags of the element.

        Parameters
        ----------
        Empty

        Returns
        -------
        content: str
        '''

        content = self.__xml_tree_node.text

        assert isinstance(content,str)

        return content

    def get_sub_node(self, tag):
        '''
        Returns the first subnode (branch) of the element tree specified by the
        parameter tag.

        Parameters
        ----------
        tag: str
            This is the XML element name (or tag name).

        Returns
        -------
        node: XMLTree
            An XML branch tree starting from `node`.
        '''

        assert isinstance(tag, str), 'tag invalid'

        node = self.__xml_tree_node.find(tag)

        assert node is not None

        node = XMLTree(node)  # wrap Element

        return node

    def get_all_sub_nodes(self, tag):
        '''
        Returns a list of all direct children nodes in the element tree with tag name.

        Parameters
        ----------
        tag: `str`
            XML element name or tag name, *e.g.*: `<task></task>`

        Returns
        -------
        sub_nodes: list(XMLTree)
            List of XMLTree items.
        '''

        assert isinstance(tag, str), 'tag invalid'

        sub_nodes = self.__xml_tree_node.findall(tag)

        assert isinstance(sub_nodes,list)
        assert len(sub_nodes) > 0

        xml_tree_list = [XMLTree(sub_node) for sub_node in sub_nodes]

        return xml_tree_list

    def get_node_children(self):
        '''
        Returns a list of the direct sub-elements in the given element (node) containing:
        the subnode, the tag (element) name, the attributes as a list of tuples,
        and the content (text) of the node. This is not recursive. Recursion
        can be done by calling this method on the children nodes (that is, the first
        element of the tuple).

        Parameters
        ----------
        empty:

        Returns
        -------
        children: list(tuple)
                  Tuple: (node, tag name, [(attribute name,attribute value),(.,.)...],
                  content). Attribute name and value are string type.
        '''

        children = list()

        for child in self.__xml_tree_node:

            children.append( (child, child.tag, child.items(), child.text) )

        return children

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

#======================= end class XMLTree =======================================
