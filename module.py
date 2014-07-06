#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for integrating systems level modules

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io, time
import logging  
from configtree import ConfigTree
from modules.chopperdriver import ChopperDriver
from modules.fuelaccumulationdriver import FuelAccumulationDriver
from modules.dissolverdriver import DissolverDriver
#*********************************************************************************

#*********************************************************************************
class Module(object):

# Private member data
# __slots__ = [

 def __init__( self,
               parentWorkDir = None,
               modConfigNode = ConfigTree()
             ):

  assert type(parentWorkDir) is str, '-> parentWorkDir is invalid.' 

# Inherit a configuration tree
  assert type(modConfigNode) is ConfigTree, '-> modConfigNode is invalid.' 
  self.__configNode = modConfigNode

# Read the module name
  self.__name = self.__configNode.GetNodeName()
  self.__type = self.__configNode.GetNodeType()

  self.__executableName = 'null'
  self.__executablePath = 'null'
  self.__configFileName = 'null'
  self.__configFilePath = 'null'

  self.__ports = list()

  self.__Setup()

#---------------------------------------------------------------------------------
# Accessors (note: all accessors of member data can potentially change the
# python object referenced to). See NB below.

 def GetName(self):
  return self.__name

 def GetPorts(self):
  return self.__ports

 def GetPortType(self, portName):
     portType = None
     for port in self.__ports:
       if port[0] == portName:
          portType = port[1] 

     return portType        

 def GetPortNames(self):
     portNames = list()
     for port in self.__ports:
        portNames.append( port[0] )

     return portNames

 def HasPortName(self, portName):
     for port in self.__ports:
       if port[0] == portName: return True

     return False
#---------------------------------------------------------------------------------
# Execute module            

 def Execute(self, runtimeCortixParamFile, runtimeCortixCommFile ):

#  print('module:',self.__name)
#  print('module executable: ',self.__executableName)
#  print('module path      : ',self.__executablePath)
#  print('input file       : ',self.__configFilePath+self.__configFileName)
#  print('param file       : ',runtimeCortixParamFile)
#  print('comm  file       : ',runtimeCortixCommFile)
 
  hostExec = self.__executablePath + self.__executableName
  input    = self.__configFilePath + self.__configFileName
  param    = runtimeCortixParamFile
  comm     = runtimeCortixCommFile

  fullPathCommDir = comm[:comm.rfind('/')]+'/'
  runtimeModuleStatusFile = fullPathCommDir + 'runtime-status.xml'

  status = runtimeModuleStatusFile

  if self.__type == 'stand-alone':
     os.system( 'time '+ hostExec + ' ' + 
                input + ' ' + param + ' ' + comm + ' ' + status + ' &' )

  elif self.__type == 'native':
    name = self.__name 
    if name == 'chopper':          
       host = ChopperDriver( input, param, comm, status )
    if name == 'fuelaccumulation': 
       host = FuelAccumulationDriver( input, param, comm, status )
    if name == 'dissolver':        
       host = DissolverDriver( input, param, comm, status )

  elif self.__type == 'wrapped':
     assert True, 'module type not implemented.'
  else: 
     assert True, 'module type invalid.'

#  print('\t\tCortix::Simulation::Application::Module:Execute() '+self.__executableName)
#  print( 'time '+ hostExec + ' ' + input + ' ' + param + ' ' + comm + ' ' + status )
#  os.system( 'time '+ hostExec + ' ' + input + ' ' + param + ' ' + comm + ' ' + status + ' &')

  return runtimeModuleStatusFile

#---------------------------------------------------------------------------------
# Setup module              

 def __Setup(self):

# Save config data
  for child in self.__configNode.GetNodeChildren():

    ( tag, attributes, text ) = child
    text = text.strip()

    if tag == 'executableName': self.__executableName = text
    if tag == 'executablePath': 
     if text[-1] != '/': text += '/'
     self.__executablePath = text

    if tag == 'configFileName': self.__configFileName = text
    if tag == 'configFilePath': 
     if text[-1] != '/': text += '/'
     self.__configFilePath = text

    if tag == 'port': 
       assert len(attributes) == 1, 'only 1 attribute allowed/required at this moment.'
       key = attributes[0][0]
       val = attributes[0][1].strip()
       assert key == 'type', 'port attribute key must be "type".'
       assert val == 'use' or val == 'provide' or val == 'input', 'port attribute value invalid.'
       self.__ports.append( (text, attributes[0][1].strip()) ) # (portName, portType)

# 
  print('\t\tCortix::Simulation::Application::Module: executableName',self.__executableName)
  print('\t\tCortix::Simulation::Application::Module: executablePath',self.__executablePath)
  print('\t\tCortix::Simulation::Application::Module: configFileName',self.__configFileName)
  print('\t\tCortix::Simulation::Application::Module: configFilePath',self.__configFilePath)
  print('\t\tCortix::Simulation::Application::Module: ports',self.__ports)

  return

#*********************************************************************************
# Unit testing. Usage: -> python module.py
if __name__ == "__main__":
  print('Unit testing for Module')
