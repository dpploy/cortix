#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix module for shearing 

Tue Jun 24 12:36:17 EDT 2014
"""
#*********************************************************************************
import os, sys, io
import datetime
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
#*********************************************************************************

def main(argv):

 assert len(argv) == 4, 'missing command line input.'

# first command line argument is an input file
 inputFullPathFileName = argv[1]

 tree = ElementTree()

# second command line argument is the Cortix parameter file
 cortexParamFullPathFileName = argv[2]
 tree.parse(cortexParamFullPathFileName)
 cortexParamXMLRootNode = tree.getroot()
 node = cortexParamXMLRootNode.find('evolveTime')
 evolveTimeUnit = node.get('unit')
 evolveTime     = float(node.text)

# print("chopper.py::main: evolveTime     = ", evolveTime)
# print("chopper.py::main: evolveTimeUnit = ", evolveTimeUnit)

# third command line argument is the Cortix communication file
 cortexCommFullPathFileName  = argv[3]
 tree.parse(cortexCommFullPathFileName)
 cortexCommXMLRootNode = tree.getroot()

# get useports
 nodes = cortexCommXMLRootNode.findall('usePort')
 assert len(nodes) == 0, 'active useports unsupported at this time.'
 usePorts = list()
 if nodes != None: 
   for node in nodes:
     usePortName = node.get('name')
     usePortFile = node.get('file')
     userPorts.append( (usePortName, usePortFile) )
 print('usePorts: ',usePorts)

# get provideports
 nodes = cortexCommXMLRootNode.findall('providePort')
 providePorts = list()
 if nodes != None: 
   for node in nodes:
     providePortName = node.get('name')
     providePortFile = node.get('file')
     providePorts.append( (providePortName, providePortFile) )
 print('providePorts: ',providePorts)

# simulate shearing and generate results

 resultsDir = '/home/dealmeida/mac-fvu/gentoo-home/work/codes/reprocessing/cortix/modules/chopper/'
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

# produce plotting results
# todo

#*********************************************************************************
# Usage: -> python pymain.py or ./pyplot.py
if __name__ == "__main__":
   main(sys.argv)
