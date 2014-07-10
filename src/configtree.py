#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for integrating system-level modules

This class generates objects that hold an ElementTree node of an XML tree 
structure. The level of the node depends on the argument passed when creating the 
object. If a node is passed, that node and all its subnodes are held. If a
filename is passed, instead, an XML file is read and the root node is held at the
top of the tree.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import datetime
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
#*********************************************************************************

#*********************************************************************************
class ConfigTree(object):

# Private member data
# __slots__ = [

 def __init__( self,
               configTreeNode = None,
               configFileName = None
             ):

    if configTreeNode is not None: 
       assert type(configTreeNode) is Element, '-> configTreeNode invalid .' 
       self.__configTreeNode = configTreeNode

    if configFileName is not None:
       assert type(configFileName) is str, '-> configFileName not a str.' 

       self.__ReadConfigTree( configFileName )

#---------------------------------------------------------------------------------
# Accessors (note: all accessors of member data can potentially change the
# python object referenced to). See NB below.

 def GetRootNode(self):
     return self.__configTreeNode

 def GetNodeTag(self):
     return self.__configTreeNode.tag

 def GetNodeName(self):
     return self.__configTreeNode.get('name')

 def GetNodeType(self):
     return self.__configTreeNode.get('type')

 def GetSubNode(self,tag):
     assert type(tag) is str, 'tag invalid'
     return self.__configTreeNode.find(tag)

 def GetAllSubNodes(self,tag):
     assert type(tag) is str, 'tag invalid'
     return self.__configTreeNode.findall(tag)

 def GetNodeChildren(self):
     return self.__GetNodeChildren()

#*********************************************************************************
# Helper internal methods

#---------------------------------------------------------------------------------
# Get node children

 def __GetNodeChildren(self):

  children = list()

  for child in self.__configTreeNode:

   # NB: child.items() is a list of pairs: (key, val)
   children.append( (child.tag, child.items(), child.text) )

  return children
#---------------------------------------------------------------------------------
# Read Cortix config xml data

 def __ReadConfigTree(self, configFileName ):
   
  tree = ElementTree()
  tree.parse( configFileName )
 
  self.__configTreeNode = tree.getroot()

#to do vfda    self.__VerifyConfigData()

  return 

#*********************************************************************************
# Unit testing. Usage: -> python configtree.py
if __name__ == "__main__":

  print('Unit testing for ConfigTree')
  tree = ConfigTree( configFileName="cortix-config.xml" )