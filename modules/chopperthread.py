#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Chopping module thread 

Tue Jun 24 12:36:17 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import logging
from threading import Thread
import xml.etree.ElementTree as ElementTree
#*********************************************************************************

#*********************************************************************************
class ChopperThread(Thread):

 def __init__( self, inputFullPathFileName, 
                     cortexParamFullPathFileName,
                     cortexCommFullPathFileName,
                     runtimeStatusFullPathFileName ):

    self.__inputFullPathFileName         = inputFullPathFileName 
    self.__cortexParamFullPathFileName   = cortexParamFullPathFileName 
    self.__cortexCommFullPathFileName    = cortexCommFullPathFileName 
    self.__runtimeStatusFullPathFileName = runtimeStatusFullPathFileName 
  
    super(ChopperThread, self).__init__()

#---------------------------------------------------------------------------------
 def run(self):

#.................................................................................
# First argument is the module input file name with full path.
# This input file may be empty or used by this driver and/or the native module.
# inputFullPathFileName 

  fin = open(self.__inputFullPathFileName,'r')
  inputDataFileNames = list()
  for line in fin:
   inputDataFileNames.append(line.strip())
  fin.close()

#.................................................................................
# Second command line argument is the Cortix parameter file: cortix-param.xml
# cortexParamFullPathFileName 
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
  timeStep       = float(node.text.strip())

  if    timeStepUnit == 'min':  timeStep *= 1.0
  elif  timeStepUnit == 'hour': timeStep *= 60.0
  elif  timeStepUnit == 'day':  timeStep *= 24.0 * 60.0
  else: assert True, 'time unit invalid.'

#.................................................................................
# Third command line argument is the Cortix communication file: cortix-comm.xml
# cortexCommFullPathFileName 
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

#.................................................................................
# Fourth command line argument is the module runtime-status.xml file
# runtimeStatusFullPathFileName 

#.................................................................................
# Create logger for this driver and its imported pymodule 

  log = logging.getLogger('chopper')
  log.setLevel(logging.DEBUG)
# create file handler for logs
  fullPathTaskDir = self.__cortexCommFullPathFileName[:self.__cortexCommFullPathFileName.rfind('/')]+'/'
  fh = logging.FileHandler(fullPathTaskDir+'chopper.log')
  fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
  ch = logging.StreamHandler()
  ch.setLevel(logging.WARN)
# create formatter and add it to the handlers
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  fh.setFormatter(formatter)
  ch.setFormatter(formatter)
# add the handlers to the logger
  log.addHandler(fh)
  log.addHandler(ch)

  s = 'created logger: drv'
  log.info(s)

  s = 'ports: '+str(ports)
  log.debug(s)

#.................................................................................
# Run Chopper
  log.info('entered Run Chopper section')


#................................................................................
# Setup input

# vfda: nothing for now

#................................................................................
# Create the host code          

# nothing for now
  log.info("host = Chopper( ports )")


#.................................................................................
# Evolve the chopper

  self.__SetRuntimeStatus('running')
  log.info("SetRuntimeStatus('running')")

  time.sleep(1) # fake running time for the chopper

  resultsDir = os.path.dirname(__file__).strip()+'/chopper/'

  for port in ports:

   (portName,portType,portFile) = port

   if portName == 'Fuel_Solid':
    s = 'cp -f ' + resultsDir + inputDataFileNames[0] + ' ' + portFile 
    log.debug(s)
    os.system(s)
   if portName == 'Gas_Release':
    s = 'cp -f ' + resultsDir + inputDataFileNames[1] + ' ' + portFile 
    log.debug(s)
    os.system(s)

#.................................................................................
# Shutdown 

  self.__SetRuntimeStatus('finished')
  log.info("SetRuntimeStatus('finished')")

#---------------------------------------------------------------------------------
 def __SetRuntimeStatus(self, status):

  status = status.strip()
  assert status == 'running' or status == 'finished', 'status %r invalid.' % status

  fout = open( self.__runtimeStatusFullPathFileName,'w' )
  s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
  s = '<!-- Written by Chopper.py -->\n'; fout.write(s)
  today = datetime.datetime.today()
  s = '<runtime>\n'; fout.write(s)
  s = '<status>'+status+'</status>\n'; fout.write(s)
  s = '</runtime>\n'; fout.write(s)
  fout.close()

#*********************************************************************************
# Usage: -> python chopperthread.py or ./chopperthread.py
if __name__ == "__main__":
  ChopperThread()
