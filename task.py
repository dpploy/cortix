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
class Task(object):

# Private member data
# __slots__ = [

 def __init__( self,
               taskConfigNode = ConfigTree()
             ):

  assert type(taskConfigNode) == ConfigTree, '-> taskConfigNode not a ConfigTree.' 
  self.__configNode = taskConfigNode

  self.__name = self.__configNode.GetNodeName()
  print('\t\tCortix::Simulation::Task: name:',self.__name)

  self.__evolveTime     = 0.0
  self.__evolveTimeUnit = 'null'

  self.__runtimeCortixParamFile = 'null'

  self.__Setup()

#---------------------------------------------------------------------------------
# Accessors (note: all accessors of member data can potentially change the
# python object referenced to). See NB below.

 def GetName(self): 
  return self.__name

 def GetEvolveTime(self):
  return self.__evolveTime

 def GetEvolveTimeUnit(self):
  return self.__evolveTimeUnit

 def SetRuntimeCortixParamFile(self, fullPath):
  self.__runtimeCortixParamFile = fullPath

 def GetRuntimeCortixParamFile(self):
  return self.__runtimeCortixParamFile

#---------------------------------------------------------------------------------
# Execute task              

 def Execute(self, application ):

  network = application.GetNetwork( self.__name )
  
  for con in network.GetConnectivity():

    mod = application.GetModule( con['toModule'] )
    mod.Execute( self.__runtimeCortixParamFile )

    mod = application.GetModule( con['fromModule'] )
    mod.Execute( self.__runtimeCortixParamFile )

  return 

#---------------------------------------------------------------------------------
# Setup task                

 def __Setup(self):

  for child in self.__configNode.GetNodeChildren():
    (tag,items,text) = child
    if tag == 'evolveTime':
       for (key,value) in items:
        if key == 'unit' : self.__evolveTimeUnit = value
       
       self.__evolveTime = float(text)

  print('\t\tCortix::Simulation::Task: evolveTime(value):',self.__evolveTime)
  print('\t\tCortix::Simulation::Task: evolveTime(unit) :',self.__evolveTimeUnit)

  return

#*********************************************************************************
# Unit testing. Usage: -> python application.py
if __name__ == "__main__":
  print('Unit testing for Task')
