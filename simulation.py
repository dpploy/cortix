#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for integrating systems level modules

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import datetime
import logging
from configtree import ConfigTree
from application import Application
from task import Task
#*********************************************************************************

#*********************************************************************************
class Simulation(object):

# Private member data
# __slots__ = [

 def __init__( self,
               cortixWorkDir = None,
               simConfigNode = ConfigTree()
             ):

  log = logging.getLogger('cortix.simulation')
  self.__logger = log

  self.__name = simConfigNode.GetNodeName()
  s = 'creating simulation: '+self.__name
  log.info(s)

  assert type(simConfigNode) is ConfigTree, '-> simConfigNode invalid.' 
  self.__configNode = simConfigNode

#------------
# Application
#------------
  for appNode in self.__configNode.GetAllSubNodes('application'):
    s = 'appName: '+appNode.get('name')
    log.debug(s)

    appConfigNode = ConfigTree( appNode )
    assert appConfigNode.GetNodeName() == appNode.get('name'), 'check failed'

    self.__application = Application( appConfigNode )

#------------
# Tasks
#------------
  self.__tasks = list()
  self.__SetupTasks()

  self.__Setup( cortixWorkDir )

#---------------------------------------------------------------------------------
# Execute  

 def Execute(self, taskName=None):

  if taskName is not None: 
     for task in self.__tasks:
       if task.GetName() == taskName: 
         task.Execute( self.__application )

  return

#---------------------------------------------------------------------------------
# Setup simulation          

 def __Setup(self, cortixWorkDir):

# create the cortix/simulation work directory
  wrkDir = cortixWorkDir 
  wrkDir += 'sim_' + self.__name + '/'

  networks = self.__application.GetNetworks()

# create subdirectories with task names
  for task in self.__tasks:
    taskName = task.GetName()
    taskWorkDir = wrkDir + 'task_' + taskName + '/'
    os.system( 'mkdir -p ' + taskWorkDir )

    # set the parameters for the task in the cortix param file 
    taskFile = taskWorkDir + 'cortix-param.xml'
    fout = open( taskFile,'w' )
    s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
    s = '<!-- Written by Cortix::Simulation::__Setup() -->\n'; fout.write(s)
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

    # using the taks and network create the module directories and comm files
    for net in networks:

     if net.GetName() == taskName: # Warning: net and task name must match

      connect = net.GetConnectivity()

      toPorts_visited   = list()
      fromPorts_visited = list()

      for con in connect:

       # Start with the ports that will function as a provide port or input port
       toModule = con['toModule']
       toPort   = con['toPort']

       module = self.__application.GetModule(toModule)

       assert module.HasPortName( toPort ), 'module %r does not have port %r.' % (module.GetName(), toPort )
       assert module.GetPortType(toPort) is not None, 'network name: %r, module name: %r, toPort: %r port type invalid %r' % (net.GetName(), module.GetName(), toPort, type(module.GetPortType(toPort)))

       if module.GetPortType(toPort) != 'input':

          assert module.GetPortType(toPort) == 'provide', 'port type %r invalid. Module %r, port %r' % (module.GetPortType(toPort), module.GetName(), toPort)

          # skip provide ports already inserted in the comm file 
          if toPort not in toPorts_visited:

            # "to" is who receives the "call", hence the provider
            toModuleWorkDir  = taskWorkDir + toModule + '/'
            toModuleCommFile = toModuleWorkDir + 'cortix-comm.xml'
            if not os.path.isdir( toModuleWorkDir ):
              os.system( 'mkdir -p ' + toModuleWorkDir )
            if not os.path.isfile( toModuleCommFile ):
              fout = open( toModuleCommFile,'w' )
              s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
              s = '<!-- Written by Cortix::Simulation -->\n'; fout.write(s)
              s = '<cortixComm>\n'; fout.write(s)
 
            fout = open( toModuleCommFile,'a' )
            # this is the cortix info for modules providing data           
            s = '<port name="'+toPort+'" type="provide" file="'+toModuleWorkDir+toPort+'.xml"/>\n'
            fout.write(s)

            fout.close()

            toPorts_visited.append( toPort )
  
            # register the cortix-comm file for the network
            net.SetRuntimeCortixCommFile( toModule, toModuleCommFile )
       else:
            toModuleWorkDir  = taskWorkDir + toModule + '/'


       # Now do the ports that will function as use ports
       fromModule = con['fromModule']
       fromPort   = con['fromPort']

       module = self.__application.GetModule(fromModule)

       assert module.HasPortName( fromPort ), 'module %r has no port %r' % (fromModule, fromPort)
       assert module.GetPortType(fromPort) == 'use' , 'module %r: invalid type for port %r' % (fromModule, fromPort)

#       print(fromPort)
#       print(fromPorts_visited)
#       assert fromPort not in fromPorts_visited, 'error in cortix-config connect.'

       # "from" is who makes the "call", hence the user        
       fromModuleWorkDir  = taskWorkDir + fromModule + '/'
       fromModuleCommFile = fromModuleWorkDir + 'cortix-comm.xml'
       if not os.path.isdir( fromModuleWorkDir ):
         os.system( 'mkdir -p '+ fromModuleWorkDir )
       if not os.path.isfile(fromModuleCommFile):
         fout = open( fromModuleCommFile,'w' )
         s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
         s = '<!-- Written by Cortix::Simulation -->\n'; fout.write(s)
         s = '<cortixComm>\n'; fout.write(s)

       fout = open( fromModuleCommFile,'a' )
       # this is the cortix info for modules using data           
       assert module.GetPortType(fromPort) == 'use', 'fromPort must be use type.'
       s = '<port name="'+fromPort+'" type="use" file="'+toModuleWorkDir+toPort+'.xml"/>\n'
       fout.write(s)

       fout.close()

#       fromPorts_visited.append( fromPort )

       # register the cortix-comm file for the network
       net.SetRuntimeCortixCommFile( fromModule, fromModuleCommFile )

#  modules  = self.__application.GetModules()

# finish forming the XML documents test for port types
  for net in networks:
   modNames = net.GetModuleNames()
   for modName in modNames:
    commFile = net.GetRuntimeCortixCommFile(modName)
    fout = open( commFile,'a' )
    s = '</cortixComm>'; fout.write(s)
    fout.close()

  return

#---------------------------------------------------------------------------------
# Setup tasks               

 def __SetupTasks(self):

  for taskNode in self.__configNode.GetAllSubNodes('task'):
   print('\tCortix::Simulation: task:',taskNode.get('name'))

   taskConfigNode = ConfigTree( taskNode )
   task = Task( taskConfigNode )

   self.__tasks.append( task )

  return

#*********************************************************************************
# Unit testing. Usage: -> python simulation.py
if __name__ == "__main__":
  print('Unit testing for Simulation')
