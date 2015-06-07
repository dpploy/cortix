#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Sat Jun  6 22:43:33 EDT 2015
"""
#*********************************************************************************
import os, sys, io, time, datetime
import logging
from threading import Thread
import xml.etree.ElementTree as ElementTree
import importlib
#*********************************************************************************

#*********************************************************************************
class Launcher(Thread):
                     
 def __init__( self, moduleType, moduleName,
                     inputFullPathFileName, 
                     cortexParamFullPathFileName,
                     cortexCommFullPathFileName,
                     runtimeStatusFullPathFileName ):

    self.__moduleName                    = moduleName
    self.__inputFullPathFileName         = inputFullPathFileName 
    self.__cortexParamFullPathFileName   = cortexParamFullPathFileName 
    self.__cortexCommFullPathFileName    = cortexCommFullPathFileName 
    self.__runtimeStatusFullPathFileName = runtimeStatusFullPathFileName 

    super(Launcher, self).__init__()

    modulePath = 'modulib.'+moduleType+'.'+moduleName+'.driver'
    self.__module = importlib.import_module(modulePath)

#---------------------------------------------------------------------------------
 def run(self):

#.................................................................................
# Create logger for this driver and its imported pymodule 
  log = logging.getLogger('launcher-'+self.__moduleName)
  log.setLevel(logging.DEBUG)
# create file handler for logs
  fullPathTaskDir = self.__cortexCommFullPathFileName[:self.__cortexCommFullPathFileName.rfind('/')]+'/'
  fh = logging.FileHandler(fullPathTaskDir+'launcher.log')
  fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
  ch = logging.StreamHandler()
  ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  fh.setFormatter(formatter)
  ch.setFormatter(formatter)
# add the handlers to the logger
  log.addHandler(fh)
  log.addHandler(ch)

  s = 'created logger: main'
  log.info(s)

  s = 'input file: ' + self.__inputFullPathFileName
  log.debug(s)

  s = 'param file: ' + self.__cortexParamFullPathFileName
  log.debug(s)

  s = 'comm file: ' + self.__cortexCommFullPathFileName
  log.debug(s)

#.................................................................................
# First argument is the module input file name with full path.
# This input file may be empty or used by this driver and/or the native module.
# inputFullPathFileName 

  assert os.path.isfile(self.__inputFullPathFileName), 'file %r not available;stop.' % self.__inputFullPathFileName

#.................................................................................
# Second argument is the Cortix parameter file: cortix-param.xml
# cortexParamFullPathFileName 

  assert os.path.isfile(self.__cortexParamFullPathFileName), 'file %r not available;stop.' % cortexParamFullPathFileName

  tree = ElementTree.parse(self.__cortexParamFullPathFileName)
  cortexParamXMLRootNode = tree.getroot()

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
# Third argument is the Cortix communication file: cortix-comm.xml
# cortexCommFullPathFileName 

  assert os.path.isfile(self.__cortexCommFullPathFileName), 'file %r not available;stop.' % self.__cortexCommFullPathFileName

  tree = ElementTree.parse(self.__cortexCommFullPathFileName)
  cortexCommXMLRootNode = tree.getroot()

# Setup ports
  nodes = cortexCommXMLRootNode.findall('port')
  ports = list()
  if nodes is not None: 
    for node in nodes:
      portName = node.get('name')
      portType = node.get('type')
      portFile = node.get('file')
      ports.append( (portName, portType, portFile) )

  tree = None

  s = 'ports: '+str(ports)
  log.debug(s)

#.................................................................................
# Fourth argument is the module runtime-status.xml file
# runtimeStatusFullPathFileName = argv[4]

#---------------------------------------------------------------------------------
# Run ModuleName
  log.info('entered Run '+self.__moduleName+' section')

#.................................................................................
# Setup input

# vfda: nothing for now

#.................................................................................
# Create the guest code             
  guest = self.__module.Driver( self.__inputFullPathFileName, ports, evolveTime )
  log.info("guest = Driver( args )")

#.................................................................................
# Evolve the module 
 
  self.__SetRuntimeStatus('running')  
  log.info("SetRuntimeStatus('running')")

  facilityTime = 0.0

  while facilityTime <= evolveTime:

   guest.CallPorts( facilityTime )

   guest.Execute( facilityTime, timeStep )

   facilityTime += timeStep 
#
#---------------------------------------------------------------------------------
# Shutdown 

  self.__SetRuntimeStatus('finished')  
  log.info("SetRuntimeStatus('finished')")
 
#---------------------------------------------------------------------------------
 def __SetRuntimeStatus(self, status):

  status = status.strip()
  assert status == 'running' or status == 'finished', 'status invalid.'

  fout = open( self.__runtimeStatusFullPathFileName,'w' )
  s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
  s = '<!-- Written by Launcher.py -->\n'; fout.write(s)
  today = datetime.datetime.today()
  s = '<!-- '+str(today)+' -->\n'; fout.write(s)
  s = '<runtime>\n'; fout.write(s)
  s = '<status>'+status+'</status>\n'; fout.write(s)
  s = '</runtime>\n'; fout.write(s)
  fout.close()

#*********************************************************************************
# Usage: -> python launcher.py or ./launcher.py
if __name__ == "__main__":
   Launcher()
