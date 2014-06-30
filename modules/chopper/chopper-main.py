#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix Chopping module wrapper

Tue Jun 24 12:36:17 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time
import datetime
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
#*********************************************************************************

#---------------------------------------------------------------------------------
def main(argv):

 assert len(argv) == 5, 'missing command line input.'

#.................................................................................
# First command line argument is the module input file name with full path.
# This input file may be used by both the wrapper and the inner-code for 
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
     portFile = node.get('file')
     ports.append( (portName, portFile) )
 print('chopper.py::ports: ',ports)

 tree = None

#.................................................................................
# Fourth command line argument is the module runtime-status.xml file
 runtimeStatusFullPathFileName = argv[4]

#---------------------------------------------------------------------------------
# Run Chopper

# Connect to the provide ports 
 for (portName,portFile) in providePorts:
   if portName == 'Fuel_Solid':
      print('MODULE::chopper.py providing port: ',portName)
   if portName == 'Gas_Release':
      print('MODULE::chopper.py providing port: ',portName)

# Evolve the chopper
#.................................................................................

 SetRuntimeStatus(runtimeStatusFullPathFileName, 'running')

 time.sleep(5) # fake running time for the chopper

 resultsDir = os.path.dirname(__file__).strip()+'/'

 for providePort in providePorts:

  (portName,portFile) = providePort

  if portName == 'Fuel_Solid':
   print( 'cp -f ' + resultsDir + inputDataFileNames[0] + ' ' + portFile )
   os.system( 'cp -f ' + resultsDir + inputDataFileNames[0] + ' ' + portFile )
  if portName == 'Gas_Release':
   print( 'cp -f ' + resultsDir + inputDataFileNames[1] + ' ' + portFile )
   os.system( 'cp -f ' + resultsDir + inputDataFileNames[1] + ' ' + portFile )

#---------------------------------------------------------------------------------
# Shutdown 

 SetRuntimeStatus(runtimeStatusFullPathFileName, 'finished')

# tree.parse(runtimeStatusFullPathFileName)
# runtimeStatusXMLRootNode = tree.getroot()
# root = runtimeStatusXMLRootNode
# node = root.find('status')
# node.text = 'finished'
# a = Element('comment')
# a.text = 'Written by Chopper.py'
# root.append(a)
# tree.write(runtimeStatusFullPathFileName,xml_declaration=True,encoding="UTF-8",method="xml")

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
   main(sys.argv)
