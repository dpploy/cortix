#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix Fuel Accumulation module wrapper 

Sun Jun 29 21:34:18 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time
import datetime
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
from fuelaccumulationarea import FuelAccumulationArea
#*********************************************************************************

#---------------------------------------------------------------------------------
def main(argv):

 assert len(argv) == 5, 'incomplete command line input.'

#.................................................................................
# First command line argument is the module input file name with full path.
# This input file may be used by both the wrapper and the inner-code for 
# communication.
 inputFullPathFileName = argv[1]

 fin = open(inputFullPathFileName,'r')
 inputData = list()
 for line in fin:
  inputData.append(line.strip())
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
 print('Ports: ',ports)

 tree = None

#.................................................................................
# Fourth command line argument is the module runtime-status.xml file
 runtimeStatusFullPathFileName = argv[4]

#---------------------------------------------------------------------------------
# Run FuelAccumulation

#................................................................................
# Setup input

 found = False
 for port in ports:
  if port[0] == 'solids':
   print( 'cp -f ' + inputData[0] + ' ' + port[2] )
   os.system( 'cp -f ' + inputData[0] + ' ' + port[2] )
   found = True

 assert found, 'Input setup failed.'

 found = False
 for port in ports:
  if port[0] == 'withdrawal-request':
   print( 'cp -f ' + inputData[1] + ' ' + port[2] )
   os.system( 'cp -f ' + inputData[1] + ' ' + port[2] )
   found = True

 assert found, 'Input setup failed.'

#................................................................................
# Create a fuel holding drum
 fuelDrum = FuelAccumulationArea( ports )

#................................................................................
# Evolve the fuel-accumulation program

 SetRuntimeStatus( runtimeStatusFullPathFileName, 'running' )

 facilityTime = 0.0

 while facilityTime <= evolveTime:
  print(facilityTime)

  fuelDrum.UseData( usePortName='solids', evolTime=facilityTime  )
  fuelDrum.UseData( usePortName='withdrawal-request', evolTime=facilityTime  )

  fuelDrum.ProvideData( providePort='fuel-segments', evolTime=facilityTime )

  facilityTime += timeStep

#---------------------------------------------------------------------------------
# Shutdown 

 SetRuntimeStatus(runtimeStatusFullPathFileName, 'finished') 

# tree.parse(runtimeStatusFullPathFileName)
# runtimeStatusXMLRootNode = tree.getroot()
# root = runtimeStatusXMLRootNode
# node = root.find('status')
# node.text = 'finished'
# a = Element('comment')
# a.text = 'Written by Dissolver.py'
# root.append(a)
# tree.write(runtimeStatusFullPathFileName,xml_declaration=True,encoding="UTF-8",method="xml")

#---------------------------------------------------------------------------------
def SetRuntimeStatus(runtimeStatusFullPathFileName, status):

 status = status.strip()
 assert status == 'running' or status == 'finished', 'status invalid.'

 fout = open( runtimeStatusFullPathFileName,'w' )
 s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
 s = '<!-- Written by Dissolver.py -->\n'; fout.write(s)
 s = '<runtime>\n'; fout.write(s)
 s = '<status>'+status+'</status>\n'; fout.write(s)
 s = '</runtime>\n'; fout.write(s)
 fout.close()

#*********************************************************************************
# Usage: -> python fuel-accumulation.py or ./fuel-accumulation.py
if __name__ == "__main__":
   main(sys.argv)
