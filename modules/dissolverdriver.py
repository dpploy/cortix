#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Dissolver module driver

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import logging
import xml.etree.ElementTree as ElementTree
from modules.dissolver import Dissolver
#*********************************************************************************

#---------------------------------------------------------------------------------
def DissolverDriver( inputFullPathFileName, 
                     cortexParamFullPathFileName,
                     cortexCommFullPathFileName,
                     runtimeStatusFullPathFileName ):

#.................................................................................
# First argument is the module input file name with full path.
# This input file may be empty or used by this driver and/or the native module.
# inputFullPathFileName 

#.................................................................................
# Second argument is the Cortix parameter file: cortix-param.xml
# cortexParamFullPathFileName 
 tree = ElementTree.parse(cortexParamFullPathFileName)
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
 tree = ElementTree.parse(cortexCommFullPathFileName)
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
# Fourth argument is the module runtime-status.xml file
# runtimeStatusFullPathFileName = argv[4]

#---------------------------------------------------------------------------------
# Create logger for this driver and its imported pymodule 
 log = logging.getLogger('drv')
 log.setLevel(logging.DEBUG)
# create file handler for logs
 fullPathTaskDir = cortexCommFullPathFileName[:cortexCommFullPathFileName.rfind('/')]+'/'
 fh = logging.FileHandler(fullPathTaskDir+'dissolver.log')
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

 s = 'created logger: main'
 log.info(s)

 s = 'orts: '+str(ports)
 log.debug(s)

#---------------------------------------------------------------------------------
# Run Dissolver
 log.info('entered Run Dissolver section')

#.................................................................................
# Setup input

# vfda: nothing for now

#.................................................................................
# Create the host code             
 host = Dissolver( ports )
 log.info("host = Dissolver( ports )")

#.................................................................................
# Evolve the dissolver

 SetRuntimeStatus( runtimeStatusFullPathFileName, 'running' )  
 log.info("SetRuntimeStatus( runtimeStatusFullPathFileName, 'running' )")

 facilityTime = 0.0

 while facilityTime <= evolveTime:

  host.CallPorts( facilityTime )

  host.Execute( facilityTime, timeStep )

  facilityTime += timeStep 
#
#---------------------------------------------------------------------------------
# Shutdown 

 SetRuntimeStatus( runtimeStatusFullPathFileName, 'finished' )  
 log.info("SetRuntimeStatus(runtimeStatusFullPathFileName, 'finished')")
 
#---------------------------------------------------------------------------------
def SetRuntimeStatus(runtimeStatusFullPathFileName, status):

 status = status.strip()
 assert status == 'running' or status == 'finished', 'status invalid.'

 fout = open( runtimeStatusFullPathFileName,'w' )
 s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
 s = '<!-- Written by Dissolver.py -->\n'; fout.write(s)
 today = datetime.datetime.today()
 s = '<!-- '+str(today)+' -->\n'; fout.write(s)
 s = '<runtime>\n'; fout.write(s)
 s = '<status>'+status+'</status>\n'; fout.write(s)
 s = '</runtime>\n'; fout.write(s)
 fout.close()

#*********************************************************************************
# Usage: -> python dissolver-main.py or ./dissolver-main.py
if __name__ == "__main__":
   DissolverDriver(sys.argv)
