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
class Module(object):

# Private member data
# __slots__ = [

 def __init__( self,
               modConfigNode = ConfigTree()
             ):

  assert type(modConfigNode) == ConfigTree, '-> modConfigNode is invalid.' 

  self.__configNode = modConfigNode

  self.__name = self.__configNode.GetNodeName()
  print('\t\tCortix::Simulation::Application::Module: name:',self.__name)

  self.__executableName = 'null'
  self.__executablePath = 'null'
  self.__configFileName = 'null'
  self.__configFilePath = 'null'
  self.__ports = list()

  self.__runtimeCortixCommFile = 'null'

  self.__Setup()

#---------------------------------------------------------------------------------
# Accessors (note: all accessors of member data can potentially change the
# python object referenced to). See NB below.

 def GetName(self):
  return self.__name

 def SetRuntimeCortixCommFile(self, fullPath):
   self.__runtimeCortixCommFile = fullPath

 def GetRuntimeCortixCommFile(self):
   return self.__runtimeCortixCommFile

#---------------------------------------------------------------------------------
# Execute module            

 def Execute(self, runtimeCortixParamFile):

  print('module:',self.__name)
  print('input file:',self.__configFilePath+self.__configFileName)
  print('param file:',runtimeCortixParamFile)
  print('comm  file:',self.__runtimeCortixCommFile)

#  os.system( )

  return

#---------------------------------------------------------------------------------
# Setup module              

 def __Setup(self):

  for child in self.__configNode.GetNodeChildren():
    (tag,items,text) = child
    if tag == 'executableName': self.__executableName = text
    if tag == 'executablePath': 
     if text[-1] != '/': text += '/'
     self.__executablePath = text
    if tag == 'configFileName': self.__configFileName = text
    if tag == 'configFilePath': 
     print(text)
     if text[-1] != '/': text += '/'
     self.__configFilePath = text
    if tag == 'port':           self.__ports.append(text)

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
