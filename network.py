#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for integrating systems level modules

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import datetime
from configtree import ConfigTree
#*********************************************************************************

#*********************************************************************************
class Network(object):

# Private member data
# __slots__ = [

 def __init__( self,
               netConfigNode = ConfigTree()
             ):

  assert type(netConfigNode) == ConfigTree, '-> netConfigNode is invalid.' 

  self.__configNode = netConfigNode

  self.__name = self.__configNode.GetNodeName()
  print('\t\tCortix::Simulation::Application::Network: name:',self.__name)

  self.__connectivity = list(dict())

  self.__Setup()

#---------------------------------------------------------------------------------
# Accessors (note: all accessors of member data can potentially change the
# python object referenced to). See NB below.

 def GetName(self):
  return self.__name

 def GetConnectivity(self):
  return self.__connectivity

#---------------------------------------------------------------------------------
# Setup network             

 def __Setup(self):

  for child in self.__configNode.GetNodeChildren():
    (tag,items,text) = child
    tmp = dict()
    if tag == 'connect': 
     for (key,value) in items: tmp[key] = value
     self.__connectivity.append( tmp )

  print('\t\tCortix::Simulation::Application::Network: connectivity',self.__connectivity)

  return

#*********************************************************************************
# Unit testing. Usage: -> python network.py
if __name__ == "__main__":
  print('Unit testing for Network')
