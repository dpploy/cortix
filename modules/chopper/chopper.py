#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix module for shearing 

Tue Jun 24 12:36:17 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time
import datetime
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
#*********************************************************************************

def main(argv):

 assert len(argv) == 5, 'missing command line input.'

# First command line argument is the module input file name with full path.
# This input file is used by both the wrapper and the inner-code for 
# communication.
 inputFullPathFileName = argv[1]

 tree = ElementTree()

# Second command line argument is the Cortix parameter file
 cortexParamFullPathFileName = argv[2]
 tree.parse(cortexParamFullPathFileName)
 cortexParamXMLRootNode = tree.getroot()
 node = cortexParamXMLRootNode.find('evolveTime')
 evolveTimeUnit = node.get('unit')
 evolveTime     = float(node.text.strip())

# print("chopper.py::main: evolveTime     = ", evolveTime)
# print("chopper.py::main: evolveTimeUnit = ", evolveTimeUnit)

# Third command line argument is the Cortix communication file
 cortexCommFullPathFileName = argv[3]
 tree.parse(cortexCommFullPathFileName)
 cortexCommXMLRootNode = tree.getroot()

# Get useports
 nodes = cortexCommXMLRootNode.findall('usePort')
 assert len(nodes) == 0, 'active useports unsupported at this time.'
 usePorts = list()
 if nodes != None: 
   for node in nodes:
     usePortName = node.get('name')
     usePortFile = node.get('file')
     usePorts.append( (usePortName, usePortFile) )
 print('usePorts: ',usePorts)

# Get provideports
 nodes = cortexCommXMLRootNode.findall('providePort')
 providePorts = list()
 if nodes != None: 
   for node in nodes:
     providePortName = node.get('name')
     providePortFile = node.get('file')
     providePorts.append( (providePortName, providePortFile) )
 print('providePorts: ',providePorts)

# Fourth command line argument is the module runtime-status.xml file
 runtimeStatusFullPathFileName = argv[4]

# Simulate shearing and generate results
# FAKE CODE RUNNING HERE
# Write runtimeStatus.xml file
 fout = open( runtimeStatusFullPathFileName,'w' )
 s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
 s = '<!-- Written by Chopper.py -->\n'; fout.write(s)
 s = '<runtime>\n'; fout.write(s)
 s = '<status>running</status>\n'; fout.write(s)
 s = '</runtime>\n'; fout.write(s)
 fout.close()

 resultsDir = os.path.dirname(__file__).strip()+'/'

 results_fuel_solid  = ('Fuel_Solid','HeadEnd_Fuel_Solid.xml')
 results_gas_release = ('Gas_Release','HeadEnd_Gas_Release.xml')

 for providePort in providePorts:
  (portName,portFile) = providePort
  if portName == results_fuel_solid[0]:
   print( 'cp -f ' + resultsDir + results_fuel_solid[1] + ' ' + portFile )
   os.system( 'cp -f ' + resultsDir + results_fuel_solid[1] + ' ' + portFile )
  if portName == results_gas_release[0]:
   print( 'cp -f ' + resultsDir + results_gas_release[1] + ' ' + portFile )
   os.system( 'cp -f ' + resultsDir + results_gas_release[1] + ' ' + portFile )

 time.sleep(10)

# produce plotting results
# todo

# Communicate with Nitron to check running status
# FAKE


# Shutdown 

 tree.parse(runtimeStatusFullPathFileName)
 runtimeStatusXMLRootNode = tree.getroot()
 root = runtimeStatusXMLRootNode
 node = root.find('status')
 node.text = 'finished'
 a = Element('comment')
 a.text = 'Written by Chopper.py'
 root.append(a)
 tree.write(runtimeStatusFullPathFileName,xml_declaration=True,encoding="UTF-8",method="xml")

#*********************************************************************************
# Usage: -> python pymain.py or ./pyplot.py
if __name__ == "__main__":
   main(sys.argv)
