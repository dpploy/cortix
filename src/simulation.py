#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import logging
from src.configtree import ConfigTree
from src.application import Application
from src.task import Task
#*********************************************************************************

#*********************************************************************************
class Simulation():

 def __init__( self,
               parentWorkDir = None,
               simConfigNode = ConfigTree()
             ):

  assert type(parentWorkDir) is str, '-> parentWorkDir invalid.' 

# Inherit a configuration tree
  assert type(simConfigNode) is ConfigTree, '-> simConfigNode invalid.' 
  self.__configNode = simConfigNode

# Read the simulation name
  self.__name = simConfigNode.GetNodeName()

# Create the cortix/simulation work directory
  wrkDir = parentWorkDir 
  wrkDir += 'sim_' + self.__name + '/'
  self.__workDir = wrkDir

  os.system( 'mkdir -p ' + self.__workDir )

# Create the logging facility for each object

  node = simConfigNode.GetSubNode('logger')
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

  fh = logging.FileHandler(self.__workDir+'sim.log')
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

#------------
# Application
#------------
  for appNode in self.__configNode.GetAllSubNodes('application'):

    appConfigNode = ConfigTree( appNode )
    assert appConfigNode.GetNodeName() == appNode.get('name'), 'check failed'

    self.__application = Application( self.__workDir, appConfigNode )

    s = 'created application: '+appNode.get('name')
    self.__log.debug(s)

#------------
# Tasks
#------------
  self.__tasks = list() # holds the task(s) created by the Execute method

  s = 'created simulation: '+self.__name
  self.__log.info(s)

#---------------------------------------------------------------------------------
# Execute  

 def Execute( self, taskName=None ):

  s = 'start Execute('+taskName+')'
  self.__log.debug(s)

  if taskName is not None: 

     self.__SetupTask( taskName )

     for task in self.__tasks:
       if task.GetName() == taskName: 

         s = 'called task.Execute() on task ' + taskName
         self.__log.debug(s)

         task.Execute( self.__application )

  s = 'end Execute('+taskName+')'
  self.__log.debug(s)

  return

#---------------------------------------------------------------------------------
# Setup simulation          

 def __SetupTask( self, taskName ):

  s = 'start __SetupTask()'
  self.__log.debug(s)

  task = None

  for taskNode in self.__configNode.GetAllSubNodes('task'):

   if taskNode.get('name') != taskName: continue

   taskConfigNode = ConfigTree( taskNode )

   task = Task( self.__workDir, taskConfigNode )

   self.__tasks.append( task )

   s = 'appended task: '+taskNode.get('name')
   self.__log.debug(s)

  if task is None:
     s = 'no task to exectute; done here.'
     self.__log.debug(s)
     s = 'end __SetupTask()'
     self.__log.debug(s)
     return

  networks = self.__application.GetNetworks()

# create subdirectory with task name
  taskName = task.GetName()
  taskWorkDir = task.GetWorkDir()
  assert os.path.isdir( taskWorkDir ), 'directory %r invalid.' % taskWorkDir

  # set the parameters for the task in the cortix param file 
  taskFile = taskWorkDir + 'cortix-param.xml'
  fout = open( taskFile,'w' )
  s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
  s = '<!-- Written by Simulation::__Setup() -->\n'; fout.write(s)
  s = '<cortixParam>\n'; fout.write(s)
  evolveTime     = task.GetEvolveTime()
  evolveTimeUnit = task.GetEvolveTimeUnit()
  s = '<evolveTime unit="'+evolveTimeUnit+'"'+'>'+str(evolveTime)+'</evolveTime>\n'
  fout.write(s)
  timeStep       = task.GetTimeStep()
  timeStepUnit   = task.GetTimeStepUnit()
  s = '<timeStep unit="'+timeStepUnit+'"'+'>'+str(timeStep)+'</timeStep>\n'
  fout.write(s)
  s = '</cortixParam>'; fout.write(s)
  fout.close()
  task.SetRuntimeCortixParamFile( taskFile )

  # using the tasks and network create the runtime module directories and comm files
  for net in networks:

   if net.GetName() == taskName: # Warning: net and task name must match

    connect = net.GetConnectivity()

    toModuleToPortVisited = dict()

    for con in connect:

     # Start with the ports that will function as a provide port or input port
     toModuleSlot = con['toModuleSlot']
     toPort       = con['toPort']

     if toModuleSlot not in toModuleToPortVisited.keys(): 
       toModuleToPortVisited[toModuleSlot] = list()

     toModuleName = toModuleSlot.split('_')[0]
     toModule = self.__application.GetModule( toModuleName )

     assert toModule is not None, 'module %r does not exist in application' % toModuleName
     assert toModule.HasPortName( toPort ), 'module %r does not have port %r.' % (toModule.GetName(), toPort )
     assert toModule.GetPortType(toPort) is not None, 'network name: %r, module name: %r, toPort: %r port type invalid %r' % (net.GetName(), toModule.GetName(), toPort, type(toModule.GetPortType(toPort)))

     if toModule.GetPortType(toPort) != 'input':

        assert toModule.GetPortType(toPort) == 'provide', 'port type %r invalid. Module %r, port %r' % (toModule.GetPortType(toPort), toModule.GetName(), toPort)

        # "to" is who receives the "call", hence the provider
        toModuleSlotWorkDir  = taskWorkDir + toModuleSlot + '/'
        toModuleSlotCommFile = toModuleSlotWorkDir + 'cortix-comm.xml'
        if not os.path.isdir( toModuleSlotWorkDir ):
          os.system( 'mkdir -p ' + toModuleSlotWorkDir )
        if not os.path.isfile( toModuleSlotCommFile ):
          fout = open( toModuleSlotCommFile,'w' )
          s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
          s = '<!-- Written by Simulation::__Setup() -->\n'; fout.write(s)
          s = '<cortixComm>\n'; fout.write(s)

        if toPort not in toModuleToPortVisited[toModuleSlot]:
          fout = open( toModuleSlotCommFile,'a' )
          # this is the cortix info for modules providing data           
          toPortMode = toModule.GetPortMode(toPort)
          if toPortMode.split('.')[0] == 'file':
             ext = toPortMode.split('.')[1]
             s = '<port name="'+toPort+'" type="provide" file="'+toModuleSlotWorkDir+toPort+'.'+ext+'"/>\n'
          elif toPortMode == 'directory': 
             s = '<port name="'+toPort+'" type="provide" directory="'+toModuleSlotWorkDir+toPort+'"/>\n'
          else:
             assert True, 'invalid port mode. fatal.'
          fout.write(s)
          fout.close()
          toModuleToPortVisited[toModuleSlot].append(toPort)

        r = '__Setup():: comm module: '+toModuleSlot+'; network: '+taskName+' '+s
        self.__log.debug(r)

        # register the cortix-comm file for the network
        net.SetRuntimeCortixCommFile( toModuleSlot, toModuleSlotCommFile )
     else:
        toModuleSlotWorkDir  = taskWorkDir + toModuleSlot + '/'

     # Now do the ports that will function as use ports
     fromModuleSlot = con['fromModuleSlot']
     fromPort       = con['fromPort']

     fromModuleName = fromModuleSlot.split('_')[0]
     fromModule = self.__application.GetModule(fromModuleName)

     assert fromModule.HasPortName( fromPort ), 'module %r has no port %r' % (fromModuleName, fromPort)
     assert fromModule.GetPortType(fromPort) == 'use' , 'module %r: invalid type for port %r' % (fromModuleName, fromPort)

#       print(fromPort)
#       print(fromPorts_visited)
#       assert fromPort not in fromPorts_visited, 'error in cortix-config connect.'

     # "from" is who makes the "call", hence the user        
     fromModuleSlotWorkDir  = taskWorkDir + fromModuleSlot + '/'
     fromModuleSlotCommFile = fromModuleSlotWorkDir + 'cortix-comm.xml'
     if not os.path.isdir( fromModuleSlotWorkDir ):
       os.system( 'mkdir -p '+ fromModuleSlotWorkDir )
     if not os.path.isfile(fromModuleSlotCommFile):
       fout = open( fromModuleSlotCommFile,'w' )
       s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
       s = '<!-- Written by Simulation::__Setup() -->\n'; fout.write(s)
       s = '<cortixComm>\n'; fout.write(s)

     fout = open( fromModuleSlotCommFile,'a' )
     # this is the cortix info for modules using data           
     assert fromModule.GetPortType(fromPort) == 'use', 'fromPort must be use type.'

     toPortMode = toModule.GetPortMode(toPort)
     if toPortMode.split('.')[0] == 'file':
#        print( toPortMode )
        ext = toPortMode.split('.')[1]
        s = '<port name="'+fromPort+'" type="use" file="'+toModuleSlotWorkDir+toPort+'.'+ext+'"/>\n'
     elif toPortMode == 'directory': 
       s = '<port name="'+fromPort+'" type="use" directory="'+toModuleSlotWorkDir+toPort+'"/>\n'
     else:
       assert True, 'invalid port mode. fatal.'
     fout.write(s)
     fout.close()
     r = '__Setup():: comm module: '+fromModuleSlot+'; network: '+taskName+' '+s
     self.__log.debug(r)

#       fromPorts_visited.append( fromPort )

     # register the cortix-comm file for the network
     net.SetRuntimeCortixCommFile( fromModuleSlot, fromModuleSlotCommFile )


# finish forming the XML documents for port types
  for net in networks:
   slotNames = net.GetSlotNames()
   for slotName in slotNames:
    commFile = net.GetRuntimeCortixCommFile(slotName)
    fout = open( commFile,'a' )
    s = '</cortixComm>'; fout.write(s)
    fout.close()

  s = 'end __Setup()'
  self.__log.debug(s)

  return

#*********************************************************************************
# Unit testing. Usage: -> python simulation.py
if __name__ == "__main__":
  print('Unit testing for Simulation')
