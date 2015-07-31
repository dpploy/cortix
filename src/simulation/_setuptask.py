"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
from src.configtree import ConfigTree
from src.task import Task
#*********************************************************************************

#---------------------------------------------------------------------------------
# Setup simulation          

def _SetupTask( self, taskName ):

  s = 'start _SetupTask()'
  self.log.debug(s)

  task = None

  for taskNode in self.configNode.GetAllSubNodes('task'):

   if taskNode.get('name') != taskName: continue

   taskConfigNode = ConfigTree( taskNode )

   task = Task( self.workDir, taskConfigNode )

   self.tasks.append( task )

   s = 'appended task: '+taskNode.get('name')
   self.log.debug(s)

  if task is None:
     s = 'no task to exectute; done here.'
     self.log.debug(s)
     s = 'end _SetupTask()'
     self.log.debug(s)
     return

  networks = self.application.GetNetworks()

# create subdirectory with task name
  taskName = task.GetName()
  taskWorkDir = task.GetWorkDir()
  assert os.path.isdir( taskWorkDir ), 'directory %r invalid.' % taskWorkDir

  # set the parameters for the task in the cortix param file 
  taskFile = taskWorkDir + 'cortix-param.xml'
  fout = open( taskFile,'w' )
  s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
  s = '<!-- Written by Simulation::_Setup() -->\n'; fout.write(s)
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
     toModule = self.application.GetModule( toModuleName )

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
          s = '<!-- Written by Simulation::_Setup() -->\n'; fout.write(s)
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

        r = '_Setup():: comm module: '+toModuleSlot+'; network: '+taskName+' '+s
        self.log.debug(r)

        # register the cortix-comm file for the network
        net.SetRuntimeCortixCommFile( toModuleSlot, toModuleSlotCommFile )
     else:
        toModuleSlotWorkDir  = taskWorkDir + toModuleSlot + '/'

     # Now do the ports that will function as use ports
     fromModuleSlot = con['fromModuleSlot']
     fromPort       = con['fromPort']

     fromModuleName = fromModuleSlot.split('_')[0]
     fromModule = self.application.GetModule(fromModuleName)

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
       s = '<!-- Written by Simulation::_Setup() -->\n'; fout.write(s)
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
     r = '_Setup():: comm module: '+fromModuleSlot+'; network: '+taskName+' '+s
     self.log.debug(r)

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

  s = 'end _Setup()'
  self.log.debug(s)

  return

#*********************************************************************************
