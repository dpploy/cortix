#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native FuelAccumulation module driver

Sun Jun 29 21:34:18 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import logging
import xml.etree.ElementTree as ElementTree
from modules.fuelaccumulation import FuelAccumulation
#*********************************************************************************

#---------------------------------------------------------------------------------
def FuelAccumulationDriver( inputFullPathFileName, 
                            cortexParamFullPathFileName,
                            cortexCommFullPathFileName,
                            runtimeStatusFullPathFileName ):

#.................................................................................
# First argument is the module input file name with full path.
# This input file may be empty or used by this driver and/or the native module.
# inputFullPathFileName 

 fin = open(inputFullPathFileName,'r')
 inputData = list()
 for line in fin:
  inputData.append(line.strip())
 fin.close()

#.................................................................................
# Second command line argument is the Cortix parameter file: cortix-param.xml
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
 timeStep       = float(node.text.strip())

 if    timeStepUnit == 'min':  timeStep *= 1.0
 elif  timeStepUnit == 'hour': timeStep *= 60.0
 elif  timeStepUnit == 'day':  timeStep *= 24.0 * 60.0
 else: assert True, 'time unit invalid.'

#.................................................................................
# Third command line argument is the Cortix communication file: cortix-comm.xml
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
# Fourth command line argument is the module runtime-status.xml file
# runtimeStatusFullPathFileName

#---------------------------------------------------------------------------------
# Create logger for this driver and its imported pymodule 

 log = logging.getLogger('drv')
 log.setLevel(logging.DEBUG)
 # create file handler for logs
 fullPathTaskDir = cortexCommFullPathFileName[:cortexCommFullPathFileName.rfind('/')]+'/'
 fh = logging.FileHandler(fullPathTaskDir+'fuelaccumulation.log')
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

#---------------------------------------------------------------------------------
# Run FuelAccumulation
 log.info('entered Run FuelAccumulation section')

#................................................................................
# Left here as an example; vfda
# Setup input (this was used when debugging; need proper cortix-config.xml

# found = False
# for port in ports:
#  if port[0] is 'solids':
#   print( 'cp -f ' + inputData[0] + ' ' + port[2] )
#   os.system( 'cp -f ' + inputData[0] + ' ' + port[2] )
#   found = True

# assert found, 'Input setup failed.'

# found = False
# for port in ports:
#  if port[0] is 'withdrawal-request':
#   print( 'cp -f ' + inputData[1] + ' ' + port[2] )
#   os.system( 'cp -f ' + inputData[1] + ' ' + port[2] )
#   found = True

# assert found, 'Input setup failed.'

#................................................................................
# Create the host code          
 host = FuelAccumulation( ports )
 log.info("host = FuelAccumulation( ports )")

#................................................................................
# Evolve the fuel accumulation

 SetRuntimeStatus( runtimeStatusFullPathFileName, 'running' )
 log.info("SetRuntimeStatus( runtimeStatusFullPathFileName, 'running' )")

 facilityTime = 0.0

 while facilityTime <= evolveTime:

  host.CallPorts( facilityTime )

  host.Execute( facilityTime, timeStep )

  facilityTime += timeStep

#---------------------------------------------------------------------------------
# Shutdown 

 SetRuntimeStatus(runtimeStatusFullPathFileName, 'finished') 
 log.info("SetRuntimeStatus(runtimeStatusFullPathFileName, 'finished')")

#---------------------------------------------------------------------------------
def SetRuntimeStatus(runtimeStatusFullPathFileName, status):

 status = status.strip()
 assert status == 'running' or status == 'finished', 'status invalid.'

 fout = open( runtimeStatusFullPathFileName,'w' )
 s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
 s = '<!-- Written by fuelaccumulation-main.py -->\n'; fout.write(s)
 today = datetime.datetime.today()
 s = '<!-- '+str(today)+' -->\n'; fout.write(s)
 s = '<runtime>\n'; fout.write(s)
 s = '<status>'+status+'</status>\n'; fout.write(s)
 s = '</runtime>\n'; fout.write(s)
 fout.close()

#*********************************************************************************
# Usage: -> python fuelaccumulation-main.py or ./fuelaccumulation-main.py
if __name__ == "__main__":
   FuelAccumulationDriver(sys.argv)
