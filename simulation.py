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

  self.__name = simConfigNode.GetNodeName()
  print('\tCortix::Simulation: name:',self.__name)

  assert type(simConfigNode) == ConfigTree, '-> simConfigNode invalid.' 
  self.__configNode = simConfigNode

# Application
  for appNode in self.__configNode.GetAllSubNodes('application'):
    print('\tCortix::Simulation: appName:',appNode.get('name'))

    appConfigNode = ConfigTree( appNode )
    assert appConfigNode.GetNodeName() == appNode.get('name'), 'check failed'

    self.__application = Application( appConfigNode )

# Tasks
  self.__tasks = list()
  self.__SetupTasks()

  self.__Setup( cortixWorkDir )

#---------------------------------------------------------------------------------
# Execute  

 def Execute(self, taskName=None):

  if taskName != None: 
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

  if not os.path.isdir(wrkDir):
    os.system( 'mkdir -p ' + wrkDir )
  else:
    os.system( 'rm -rf ' + wrkDir )

  networks = self.__application.GetNetworks()
  modules  = self.__application.GetModules()

# create subdirectories with task names
  for task in self.__tasks:
    taskName = task.GetName()
    taskWorkDir = wrkDir + 'task_' + taskName + '/'
    os.system( 'mkdir -p ' + taskWorkDir )

    # set the parameters for the task in the cortix param file 
    taskFile = taskWorkDir + 'cortix-param.xml'
    fout = open( taskFile,'w' )
    s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
    s = '<!-- Written by Cortix::Simulation -->\n'; fout.write(s)
    evolveTime     = task.GetEvolveTime()
    evolveTimeUnit = task.GetEvolveTimeUnit()
    s = '<evolveTime unit="'+evolveTimeUnit+'"'+'>'+str(evolveTime)+'</evolveTime>\n'
    fout.write(s)
    fout.close()
    task.SetRuntimeCortixParamFile( taskFile )

    # using the taks and network create the module directories and comm files
    for net in networks:
     if net.GetName() == taskName:
      connect = net.GetConnectivity()
      for con in connect:

       toModule   = con['toModule']
       toPort     = con['toPort']

       # "to" is who receives the "call", hence the provider
       toModuleWorkDir    = taskWorkDir + toModule + '/'
       toModuleCommFile = toModuleWorkDir + 'cortix-comm.xml'
       if not os.path.isdir( toModuleWorkDir ):
         os.system( 'mkdir -p '+ toModuleWorkDir )
       if not os.path.isfile( toModuleCommFile ):
         fout = open( toModuleCommFile,'w' )
         s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
         s = '<!-- Written by Cortix::Simulation -->\n'; fout.write(s)

       fout = open( toModuleCommFile,'a' )
       # this is the cortix info for modules providing data           
       s = '<providePort name="'+toPort+'" file="'+toModuleWorkDir+toPort+'.xml"/>\n'
       fout.write(s)

       fout.close()

       # register the cortix-comm file for the network
       net.SetRuntimeCortixCommFile( toModule, toModuleCommFile )

       fromModule = con['fromModule']
       fromPort   = con['fromPort']

       # "from" is who makes the "call", hence the user        
       fromModuleWorkDir = taskWorkDir + fromModule + '/'
       fromModuleCommFile = fromModuleWorkDir + 'cortix-comm.xml'
       if not os.path.isdir( fromModuleWorkDir ):
         os.system( 'mkdir -p '+ fromModuleWorkDir )
       if not os.path.isfile(fromModuleCommFile):
         fout = open( fromModuleCommFile,'w' )
         s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
         s = '<!-- Written by Cortix::Simulation -->\n'; fout.write(s)

       fout = open( fromModuleCommFile,'a' )
       # this is the cortix info for modules using data           
       s = '<usePort name="'+fromPort+'" file="'+toModuleWorkDir+toPort+'.xml"/>\n'
       fout.write(s)

       fout.close()

       # register the cortix-comm file for the network
       net.SetRuntimeCortixCommFile( fromModule, fromModuleCommFile )


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
