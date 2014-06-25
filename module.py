#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for integrating systems level modules

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io, time
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

  self.__Setup()

#---------------------------------------------------------------------------------
# Accessors (note: all accessors of member data can potentially change the
# python object referenced to). See NB below.

 def GetName(self):
  return self.__name

#---------------------------------------------------------------------------------
# Execute module            

 def Execute(self, runtimeCortixParamFile, runtimeCortixCommFile ):

#  print('module:',self.__name)
#  print('module executable: ',self.__executableName)
#  print('module path      : ',self.__executablePath)
#  print('input file       : ',self.__configFilePath+self.__configFileName)
#  print('param file       : ',runtimeCortixParamFile)
#  print('comm  file       : ',runtimeCortixCommFile)
 
  module = self.__executablePath + self.__executableName
  input  = self.__configFilePath + self.__configFileName
  param  = runtimeCortixParamFile
  comm   = runtimeCortixCommFile

  runtimeModuleStatus = comm[:comm.rfind('/')]+'/'+'runtime-status.xml'
  status = runtimeModuleStatus 

  print('\t\tCortix::Simulation::Application::Module:Execute() '+self.__executableName)
  print( 'time '+ module + ' ' + input + ' ' + param + ' ' + comm + ' ' + status )
  os.system( 'time '+ module + ' ' + input + ' ' + param + ' ' + comm + ' ' + status + ' &')

  time.sleep(1)
  if os.path.isfile( status ): return status
  else:                        return None

  return

#---------------------------------------------------------------------------------
# Setup module              

 def __Setup(self):

  for child in self.__configNode.GetNodeChildren():
    (tag,items,text) = child
    text = text.strip()
    if tag == 'executableName': self.__executableName = text
    if tag == 'executablePath': 
     if text[-1] != '/': text += '/'
     self.__executablePath = text
    if tag == 'configFileName': self.__configFileName = text
    if tag == 'configFilePath': 
     if text[-1] != '/': text += '/'
     self.__configFilePath = text
    if tag == 'port': self.__ports.append(text)

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
