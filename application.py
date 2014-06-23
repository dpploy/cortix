#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for integrating systems level modules

An Application object is the composition of Module objects and Network objects.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import datetime
from configtree import ConfigTree
from module import Module
from network import Network
#*********************************************************************************

#*********************************************************************************
class Application(object):

# Private member data
# __slots__ = [

 def __init__( self,
               appConfigNode = ConfigTree()
             ):

  assert type(appConfigNode) == ConfigTree, '-> appConfigNode invalid' 
  self.__configNode = appConfigNode

  self.__name = self.__configNode.GetNodeName()
  print('\t\tCortix::Simulation::Application: name:',self.__name)

# modules        
  self.__modules = list()
  self.__SetupModules()

# networks
  self.__networks = list()
  self.__SetupNetworks()

#---------------------------------------------------------------------------------
# Getters

 def GetNetworks(self):
  return self.__networks

 def GetNetwork(self, name):
  for net in self.__networks:
     if net.GetName() == name: return net
  return None

 def GetModules(self):
  return self.__modules

 def GetModule(self, name):
  for mod in self.__modules:
     if mod.GetName() == name: return mod
  return None

#---------------------------------------------------------------------------------
# Setup application         

 def Setup(self):

#  for modName in self.__configNode.GetModuleNames():
   
#   module = Module( modName, self.__configNode )
#   self.__modules.append( module )

  return

#---------------------------------------------------------------------------------
# Setup modules             

 def __SetupModules(self):

  for modNode in self.__configNode.GetAllSubNodes('module'):
   print('\t\tCortix::Simulation::Application: module:',modNode.get('name'))

   modConfigNode = ConfigTree( modNode )
   assert modConfigNode.GetNodeName() == modNode.get('name'), 'check failed'

   module = Module( modConfigNode )

   self.__modules.append( module )

  return

#---------------------------------------------------------------------------------
# Setup network             

 def __SetupNetworks(self):

  for netNode in self.__configNode.GetAllSubNodes('network'):
   print('\t\tCortix::Simulation::Application: network:',netNode.get('name'))

   netConfigNode = ConfigTree( netNode )
   assert netConfigNode.GetNodeName() == netNode.get('name'), 'check failed'

   network = Network( netConfigNode )

   self.__networks.append( network )

  return

#*********************************************************************************
# Unit testing. Usage: -> python application.py
if __name__ == "__main__":
  print('Unit testing for Application')
