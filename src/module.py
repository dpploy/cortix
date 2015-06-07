#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io, time
import logging  
from src.configtree import ConfigTree
from src.launcher   import Launcher
#*********************************************************************************

#*********************************************************************************
class Module():

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

# Read the module name and type
  self.__name = self.__configNode.GetNodeName()
  self.__type = self.__configNode.GetNodeType()

  self.__executableName = 'null'
  self.__executablePath = 'null'
  self.__inputFileName  = 'null'
  self.__inputFilePath  = 'null'

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
#  print('input file       : ',self.__inputFilePath+self.__inputFileName)
#  print('param file       : ',runtimeCortixParamFile)
#  print('comm  file       : ',runtimeCortixCommFile)
 
  hostExec = self.__executablePath + self.__executableName
  input    = self.__inputFilePath + self.__inputFileName
  param    = runtimeCortixParamFile
  comm     = runtimeCortixCommFile

  fullPathCommDir = comm[:comm.rfind('/')]+'/'
  runtimeModuleStatusFile = fullPathCommDir + 'runtime-status.xml'

  status = runtimeModuleStatusFile

#.................................................................................
# Stand-alone modules run with external system call using file IO communication
# Good luck, I will leave you alone now.
  if self.__type == 'stand-alone':
     os.system( 'time '+ hostExec + ' ' + 
                input + ' ' + param + ' ' + comm + ' ' + status + ' &' )

#.................................................................................
# Native modules run on threads using file IO communication
# Wrapped modules run on threads and external system call of their own with IO comm
  elif self.__type == 'native' or self.__type == 'wrapped':
    modName = self.__name 
    modType = self.__type

    t = Launcher( modType, modName, input, param, comm, status )
    t.start()

  else: 
     assert True, 'module type invalid.'

  return runtimeModuleStatusFile

#---------------------------------------------------------------------------------
# Setup module              

 def __Setup(self):

# Save config data
  for child in self.__configNode.GetNodeChildren():

    ( tag, attributes, text ) = child
    text = text.strip()

    if self.__type != 'native':
       if tag == 'executableName': self.__executableName = text
       if tag == 'executablePath': 
        if text[-1] != '/': text += '/'
        self.__executablePath = text

    if tag == 'inputFileName': self.__inputFileName = text
    if tag == 'inputFilePath': 
     if text[-1] != '/': text += '/'
     self.__inputFilePath = text

    if tag == 'port': 
       assert len(attributes) == 1, 'only 1 attribute allowed/required at this moment.'
       key = attributes[0][0]
       val = attributes[0][1].strip()
       assert key == 'type', 'port attribute key must be "type".'
       assert val == 'use' or val == 'provide' or val == 'input', 'port attribute value invalid.'
       self.__ports.append( (text, attributes[0][1].strip()) ) # (portName, portType)

# 
#  print('\t\tCortix::Simulation::Application::Module: executableName',self.__executableName)
#  print('\t\tCortix::Simulation::Application::Module: executablePath',self.__executablePath)
#  print('\t\tCortix::Simulation::Application::Module: inputFileName',self.__inputFileName)
#  print('\t\tCortix::Simulation::Application::Module: inputFilePath',self.__inputFilePath)
#  print('\t\tCortix::Simulation::Application::Module: ports',self.__ports)

  return

#*********************************************************************************
# Unit testing. Usage: -> python module.py
if __name__ == "__main__":
  print('Unit testing for Module')
