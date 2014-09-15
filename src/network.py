#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import datetime
from src.configtree import ConfigTree
#*********************************************************************************

#*********************************************************************************
class Network(object):

# Private member data
# __slots__ = [

 def __init__( self,
               netConfigNode = ConfigTree()
             ):

  assert type(netConfigNode) is ConfigTree, '-> netConfigNode is invalid.' 

  self.__configNode = netConfigNode

  self.__name = self.__configNode.GetNodeName()
#  print('\t\tCortix::Simulation::Application::Network: name:',self.__name)

  self.__connectivity = list(dict()) # connectivity information of the network
  self.__moduleNames  = list()        # modules involved in the network

  self.__runtimeCortixCommFile = dict() # cortix communication file for modules

  self.__Setup()

#---------------------------------------------------------------------------------
# Accessors (note: all accessors of member data can potentially change the
# python object referenced to). See NB below.

 def GetName(self):
  return self.__name

 def GetConnectivity(self):
  return self.__connectivity

 def GetModuleNames(self):
  return self.__moduleNames

 def SetRuntimeCortixCommFile(self, moduleName, fullPathFileName):
  self.__runtimeCortixCommFile[ moduleName ] = fullPathFileName

 def GetRuntimeCortixCommFile(self, moduleName):
     if moduleName in self.__runtimeCortixCommFile: 
        return self.__runtimeCortixCommFile[ moduleName ]
     return None

#---------------------------------------------------------------------------------
# Setup network             

 def __Setup(self):

  for child in self.__configNode.GetNodeChildren():

    ( tag, attributes, text ) = child

    if tag == 'connect':
     assert text is None, 'non empty text, %r, in %r network: ' % (text,self.__name)

    tmp = dict()

    if tag == 'connect': 

     for (key,value) in attributes: 
          assert key not in tmp.keys(), 'repeated key in attribute of %r network' % self.__name
          tmp[key] = value

     self.__connectivity.append( tmp )

     for (key,val) in tmp.items():
       if key == 'fromModule': self.__runtimeCortixCommFile[ val ] = 'null'
       if key == 'toModule'  : self.__runtimeCortixCommFile[ val ] = 'null'

#  print('\t\tCortix::Simulation::Application::Network: connectivity',self.__connectivity)

  self.__moduleNames = [ name for name in self.__runtimeCortixCommFile.keys()]

#  print('\t\tCortix::Simulation::Application::Network: modules',self.__moduleNames)

  return

#*********************************************************************************
# Unit testing. Usage: -> python network.py
if __name__ == "__main__":
  print('Unit testing for Network')
