#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix Chopping module executable

Tue Jun 24 12:36:17 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
#*********************************************************************************

#---------------------------------------------------------------------------------
def Main(argv):

#---------------------------------------------------------------------------------
# Read and process the command prompt arguments

 assert len(argv) == 5, 'missing command line input.'

#.................................................................................
# First command line argument is the module input file name with full path.
# This input file may be used by both the wrapper and the host code for 
# communication.
 inputFullPathFileName = argv[1]

 fin = open(inputFullPathFileName,'r')
 inputDataFileNames = list()
 for line in fin:
  inputDataFileNames.append(line.strip())
 fin.close()

#.................................................................................
# Second command line argument is the Cortix parameter file: cortix-param.xml
 tree = ElementTree()
 cortexParamFullPathFileName = argv[2]
 tree.parse(cortexParamFullPathFileName)
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
 tree = ElementTree()
 cortexCommFullPathFileName = argv[3]
 tree.parse(cortexCommFullPathFileName)
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
 print('chopper-main.py::ports: ',ports)

 tree = None

#.................................................................................
# Fourth command line argument is the module runtime-status.xml file
 runtimeStatusFullPathFileName = argv[4]

#---------------------------------------------------------------------------------
# Run Chopper

#................................................................................
# Setup input

# nothing for now

#................................................................................
# Create the chopper equipment

# nothing for now

#.................................................................................
# Evolve the chopper

 SetRuntimeStatus(runtimeStatusFullPathFileName, 'running')

 time.sleep(1) # fake running time for the chopper

 resultsDir = os.path.dirname(__file__).strip()+'/'

 for port in ports:

  (portName,portType,portFile) = port

  if portName == 'Fuel_Solid':
   print( 'cp -f ' + resultsDir + inputDataFileNames[0] + ' ' + portFile )
   os.system( 'cp -f ' + resultsDir + inputDataFileNames[0] + ' ' + portFile )
  if portName == 'Gas_Release':
   print( 'cp -f ' + resultsDir + inputDataFileNames[1] + ' ' + portFile )
   os.system( 'cp -f ' + resultsDir + inputDataFileNames[1] + ' ' + portFile )

#---------------------------------------------------------------------------------
# Shutdown 

 SetRuntimeStatus(runtimeStatusFullPathFileName, 'finished')

#---------------------------------------------------------------------------------
def SetRuntimeStatus(runtimeStatusFullPathFileName, status):

 status = status.strip()
 assert status == 'running' or status == 'finished', 'status %r invalid.' % status

 fout = open( runtimeStatusFullPathFileName,'w' )
 s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
 s = '<!-- Written by Chopper.py -->\n'; fout.write(s)
 s = '<runtime>\n'; fout.write(s)
 s = '<status>'+status+'</status>\n'; fout.write(s)
 s = '</runtime>\n'; fout.write(s)
 fout.close()

#*********************************************************************************
# Usage: -> python pymain.py or ./pyplot.py
if __name__ == "__main__":
   Main(sys.argv)
