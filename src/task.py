#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for integrating systems level modules

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io, time
import logging
from src.configtree import ConfigTree
from xml.etree.cElementTree import ElementTree
#*********************************************************************************

#*********************************************************************************
class Task(object):

# Private member data
# __slots__ = [

 def __init__( self,
               parentWorkDir = None,
               taskConfigNode = ConfigTree()
             ):

  assert type(parentWorkDir) is str, '-> parentWorkDir invalid.' 

# Inherit a configuration tree
  assert type(taskConfigNode) is ConfigTree, '-> taskConfigNode not a ConfigTree.' 
  self.__configNode = taskConfigNode

# Read the simulation name
  self.__name = self.__configNode.GetNodeName()

# Set the work directory (previously created)
  assert os.path.isdir( parentWorkDir ), 'work directory not available.'
  self.__workDir = parentWorkDir + 'task_' + self.__name + '/'
  os.system( 'mkdir -p ' + self.__workDir )

# Create the logging facility for the object
  node = taskConfigNode.GetSubNode('logger')
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

  fh = logging.FileHandler(self.__workDir+'task.log')
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

  self.__evolveTime     = 0.0
  self.__evolveTimeUnit = 'null'

  self.__timeStep     = 0.0
  self.__timeStepUnit = 'null'

  self.__runtimeCortixParamFile = 'null'

# Setup this object
  self.__Setup()

  s = 'created task: '+self.__name
  self.__log.info(s)

#---------------------------------------------------------------------------------
# Accessors (note: all accessors of member data can potentially change the
# python object referenced to). See NB below.

 def GetName(self): 
  return self.__name

 def GetWorkDir(self): 
  return self.__workDir

 def GetEvolveTime(self):
  return self.__evolveTime

 def GetEvolveTimeUnit(self):
  return self.__evolveTimeUnit

 def GetTimeStep(self):
  return self.__timeStep

 def GetTimeStepUnit(self):
  return self.__timeStepUnit

 def SetRuntimeCortixParamFile(self, fullPath):
  self.__runtimeCortixParamFile = fullPath

 def GetRuntimeCortixParamFile(self):
  return self.__runtimeCortixParamFile

#---------------------------------------------------------------------------------
# Execute task              

 def Execute(self, application ):

  network = application.GetNetwork( self.__name )

  runtimeStatusFiles = dict()
  
  for modName in network.GetModuleNames():

    mod = application.GetModule( modName )

    paramFile = self.__runtimeCortixParamFile
    commFile  = network.GetRuntimeCortixCommFile( modName )

    # Run module in the background
    statusFile = mod.Execute( paramFile, commFile )
    assert statusFile is not None, 'module launching failed.'

    runtimeStatusFiles[ mod.GetName() ] = statusFile

# monitor runtime status

  status = 'running'

  while status == 'running': 

   time.sleep(20)

   (status,modNames) = self.__GetRuntimeStatus( runtimeStatusFiles )

   s = 'runtime status: '+status+' modules: '+str(modNames)
   self.__log.info(s)

  return 

#---------------------------------------------------------------------------------
# Check overall task status 

 def __GetRuntimeStatus(self, runtimeStatusFiles):
  
  taskStatus = 'finished'
  runningModuleNames = list()

  for (modName,statusFile) in runtimeStatusFiles.items():

     if not os.path.isfile(statusFile): time.sleep(1)
     assert os.path.isfile(statusFile), 'runtime status file %r not found.' % statusFile

     tree = ElementTree()
     tree.parse( statusFile )
     statusFileXMLRootNode = tree.getroot()
     node = statusFileXMLRootNode.find('status')
     status = node.text.strip()
     if status == 'running': 
       taskStatus = 'running'
       runningModuleNames.append(modName)
  
  return (taskStatus, runningModuleNames)

#---------------------------------------------------------------------------------
# Setup task                

 def __Setup(self):

  s = 'start __Setup()'
  self.__log.debug(s)

  for child in self.__configNode.GetNodeChildren():
    (tag, items, text) = child
    if tag == 'evolveTime':
       for (key,value) in items:
        if key == 'unit' : self.__evolveTimeUnit = value
       
       self.__evolveTime = float(text.strip())
    if tag == 'timeStep':
       for (key,value) in items:
        if key == 'unit' : self.__timeStepUnit = value
       
       self.__timeStep = float(text.strip())

  s = 'evolveTime value = '+str(self.__evolveTime)
  self.__log.debug(s)
  s = 'evolveTime unit  = '+str(self.__evolveTimeUnit)
  self.__log.debug(s)

  s = 'end __Setup()'
  self.__log.debug(s)

  return

#*********************************************************************************
# Unit testing. Usage: -> python application.py
if __name__ == "__main__":
  print('Unit testing for Task')
