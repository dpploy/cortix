#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for integrating systems level modules

An Application object is the composition of Module objects and Network objects.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import logging
from configtree import ConfigTree
from module import Module
from network import Network
#*********************************************************************************

#*********************************************************************************
class Application(object): # this is meant to be a singleton class

# Private member data
# __slots__ = [

 def __init__( self,
               appWorkDir = None,
               appConfigNode = ConfigTree()
             ):

  assert type(appWorkDir) is str, '-> appWorkDir is invalid' 

# Inherit a configuration tree
  assert type(appConfigNode) is ConfigTree, '-> appConfigNode invalid' 
  self.__configNode = appConfigNode

# Read the application name
  self.__name = self.__configNode.GetNodeName()

# Set the work directory (previously created)

  self.__workDir = appWorkDir
  assert os.path.isdir( appWorkDir ), 'work directory not available.'

# Create the logging facility for the singleton object
  node = appConfigNode.GetSubNode('logger')
  loggerName = self.__name
  log = logging.getLogger(loggerName)
  log.setLevel(logging.NOTSET)

  loggerLevel = node.get('level').strip()
  if   loggerLevel == 'DEBUG': log.setLevel(logging.DEBUG)
  elif loggerLevel == 'INFO':  log.setLevel(logging.INFO)
  elif loggerLevel == 'WARN':  log.setLevel(logging.WARN)
  elif loggerLevel == 'ERROR':  log.setLevel(logging.ERROR)
  elif loggerLevel == 'CRITICAL':  log.setLevel(logging.CRITICAL)
  elif loggerLevel == 'FATAL':  log.setLevel(logging.FATAL)
  else:
    assert True, 'logger level for %r: %r invalid' % (loggerName, loggerLevel)

  self.__log = log

  fh = logging.FileHandler(self.__workDir+'app.log')
  fh.setLevel(logging.NOTSET)

  ch = logging.StreamHandler()
  ch.setLevel(logging.NOTSET)

  for child in node:
   if child.tag == 'fileHandler':
      # file handler
      fhLevel = child.get('level').strip()
      if   fhLevel == 'DEBUG': fh.setLevel(logging.DEBUG)
      elif fhLevel == 'INFO': fh.setLevel(logging.INFO)
      elif fhLevel == 'WARN': fh.setLevel(logging.WARN)
      elif fhLevel == 'ERROR': fh.setLevel(logging.ERROR)
      elif fhLevel == 'CRITICAL': fh.setLevel(logging.CRITICAL)
      elif fhLevel == 'FATAL': fh.setLevel(logging.FATAL)
      else:
        assert True, 'file handler log level for %r: %r invalid' % (loggerName, fhLevel)
   if child.tag == 'consoleHandler':
      # console handler
      chLevel = child.get('level').strip()
      if   chLevel == 'DEBUG': ch.setLevel(logging.DEBUG)
      elif chLevel == 'INFO': ch.setLevel(logging.INFO)
      elif chLevel == 'WARN': ch.setLevel(logging.WARN)
      elif chLevel == 'ERROR': ch.setLevel(logging.ERROR)
      elif chLevel == 'CRITICAL': ch.setLevel(logging.CRITICAL)
      elif chLevel == 'FATAL': ch.setLevel(logging.FATAL)
      else:
        assert True, 'console handler log level for %r: %r invalid' % (loggerName, chLevel)
  # formatter added to handlers
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  fh.setFormatter(formatter)
  ch.setFormatter(formatter)
  # add handlers to logger
  log.addHandler(fh)
  log.addHandler(ch)

  s = 'created logger: '+self.__name
  self.__log.info(s)

  s = 'logger level: '+loggerLevel
  self.__log.debug(s)
  s = 'logger file handler level: '+fhLevel
  self.__log.debug(s)
  s = 'logger console handler level: '+chLevel
  self.__log.debug(s)

#--------
# modules        
#--------
  self.__modules = list()
  self.__SetupModules()

#--------
# networks
#--------
  self.__networks = list()
  self.__SetupNetworks()

  s = 'created application: '+self.__name
  self.__log.info(s)

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

  s = 'start __SetupModules()'
  self.__log.debug(s)

  for modNode in self.__configNode.GetAllSubNodes('module'):

     modConfigNode = ConfigTree( modNode )
     assert modConfigNode.GetNodeName() == modNode.get('name'), 'check failed'

     module = Module( self.__workDir, modConfigNode )

     self.__modules.append( module )

     s = 'appended module ' + modNode.get('name')
     self.__log.debug(s)

  s = 'end __SetupModules()'
  self.__log.debug(s)

  return

#---------------------------------------------------------------------------------
# Setup network             

 def __SetupNetworks(self):

  s = 'start __SetupNetworks()'
  self.__log.debug(s)

  for netNode in self.__configNode.GetAllSubNodes('network'):

   netConfigNode = ConfigTree( netNode )
   assert netConfigNode.GetNodeName() == netNode.get('name'), 'check failed'

   network = Network( netConfigNode )

   self.__networks.append( network )

   s = 'appended network ' + netNode.get('name')
   self.__log.debug(s)

  s = 'end __SetupNetworks()'
  self.__log.debug(s)

  return

#*********************************************************************************
# Unit testing. Usage: -> python application.py
if __name__ == "__main__":
  print('Unit testing for Application')
