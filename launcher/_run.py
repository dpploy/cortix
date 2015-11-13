"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Sat Jun  6 22:43:33 EDT 2015
"""
#*********************************************************************************
import os, sys, io, time, datetime
import xml.etree.ElementTree as ElementTree

from ._setruntimestatus import _SetRuntimeStatus
#*********************************************************************************

#---------------------------------------------------------------------------------
# Internal threading run helper

def _Run( self ):

#.................................................................................
# Verify the module input file name with full path.
# This input file may be empty or used by this driver and/or the native/wrapped module.
# inputFullPathFileName 

  assert os.path.isfile(self.inputFullPathFileName), 'file %r not available;stop.' % self.inputFullPathFileName

#.................................................................................
# Read the Cortix parameter file: cortix-param.xml
# cortexParamFullPathFileName 

  assert os.path.isfile(self.cortexParamFullPathFileName), 'file %r not available;stop.' % cortexParamFullPathFileName

  tree = ElementTree.parse(self.cortexParamFullPathFileName)

  cortexParamXMLRootNode = tree.getroot()

  node = cortexParamXMLRootNode.find('startTime')

  startTimeUnit = node.get('unit')
  startTime     = float(node.text.strip())

  if    startTimeUnit == 'min':  startTime *= 1.0
  elif  startTimeUnit == 'hour': startTime *= 60.0
  elif  startTimeUnit == 'day':  startTime *= 24.0 * 60.0
  else: assert True, 'time unit invalid.'

  node = cortexParamXMLRootNode.find('evolveTime')

  evolveTimeUnit = node.get('unit')
  evolveTime     = float(node.text.strip())

  if    evolveTimeUnit == 'min':  evolveTime *= 1.0
  elif  evolveTimeUnit == 'hour': evolveTime *= 60.0
  elif  evolveTimeUnit == 'day':  evolveTime *= 24.0 * 60.0
  else: assert True, 'time unit invalid.'

  node = cortexParamXMLRootNode.find('timeStep')

  timeStepUnit = node.get('unit')
  timeStep     = float(node.text.strip())

  if    timeStepUnit == 'min':  timeStep *= 1.0
  elif  timeStepUnit == 'hour': timeStep *= 60.0
  elif  timeStepUnit == 'day':  timeStep *= 24.0 * 60.0
  else: assert True, 'time unit invalid.'

#.................................................................................
# Read the Cortix communication file: cortix-comm.xml  and  setup ports
# cortexCommFullPathFileName 

  assert os.path.isfile(self.cortexCommFullPathFileName), 'file %r not available;stop.' % self.cortexCommFullPathFileName

  tree = ElementTree.parse( self.cortexCommFullPathFileName )

  cortexCommXMLRootNode = tree.getroot()

  # setup ports
  nodes = cortexCommXMLRootNode.findall('port')
  ports = list()
  if nodes is not None: 
    for node in nodes:
      portName = node.get('name')
      portType = node.get('type')
      portFile = node.get('file')
      portDirectory = node.get('directory')

      if portFile is not None: 
        ports.append( (portName, portType, portFile) ) 
      elif portDirectory is not None: 
        ports.append( (portName, portType, portDirectory) ) 
      else: 
         assert True, 'port mode incorrect. fatal.'

  tree = None

  s = 'ports: '+str(ports)
  self.log.debug(s)

#---------------------------------------------------------------------------------
# Run ModuleName

  self.log.info('entered Run '+self.moduleName+'_'+str(self.slotId)+' section')

  finalTime = startTime + evolveTime

#.................................................................................
# Create the guest code driver
  guestDriver = self.pyModule.CortixDriver( self.slotId, 
                                            self.inputFullPathFileName, 
                                            self.execFullPathFileName,
                                            self.workDir,
                                            ports, startTime, finalTime )

  self.log.info('guestDriver = CortixDriver( slotId='+str(self.slotId)+',file='+self.inputFullPathFileName+',ports='+str(ports)+',startTime='+str(startTime)+',finalTime='+str(finalTime)+' )' )

#.................................................................................
# Evolve the module 
 
  _SetRuntimeStatus(self, 'running')  
  self.log.info("_SetRuntimeStatus(self, 'running')")

  facilityTime = startTime

  while facilityTime <= finalTime:
 
    s = '****************************************************************************'
    self.log.debug(s)
    s = 'CORTIX::LAUNCHER->***->LAUNCHER->***->LAUNCHER->***->LAUNCHER->***->LAUNCHER'
    self.log.debug(s)
    s = '****************************************************************************'
    self.log.debug(s)

    s = '_Run('+str(round(facilityTime,3))+'[min]): '
    self.log.debug(s)

    startTime = time.time()

    #-----------------------------------------------------------------------------
    # Data exchange at facilityTime (at startTime, this is here for provide state)
    guestDriver.CallPorts( facilityTime )
    #-----------------------------------------------------------------------------

    #-----------------------------------------------------------------------------
    # Advance to facilityTime + timeStep
    guestDriver.Execute( facilityTime, timeStep )
    #-----------------------------------------------------------------------------

    endTime = time.time()

    s = 'elapsed time (s): '+str(round(endTime-startTime,2))
    self.log.debug(s)

    s = '_Run('+str(round(facilityTime,3))+'[min]) '
    self.log.info(s)

    facilityTime += timeStep 
#
#---------------------------------------------------------------------------------
# Shutdown 

  _SetRuntimeStatus(self, 'finished')  
  self.log.info("_SetRuntimeStatus(self, 'finished'")

#*********************************************************************************
