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
from holdingdrum import HoldingDrum
#*********************************************************************************

#---------------------------------------------------------------------------------
def main(argv):

 assert len(argv) == 5, 'incomplete command line input.'

#.................................................................................
# First command line argument is the module input file name with full path.
# This input file may be used by both the wrapper and the inner-code for 
# communication.
 inputFullPathFileName = argv[1]

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

#.................................................................................
# Third command line argument is the Cortix communication file: cortix-comm.xml
 tree = ElementTree()
 cortexCommFullPathFileName = argv[3]
 tree.parse(cortexCommFullPathFileName)
 cortexCommXMLRootNode = tree.getroot()

# Setup useports
 nodes = cortexCommXMLRootNode.findall('usePort')
 usePorts = list()
 if nodes is not None: 
   for node in nodes:
     usePortName = node.get('name')
     usePortFile = node.get('file')
     usePorts.append( (usePortName, usePortFile) )
 print('usePorts: ',usePorts)

# Setup provideports
 nodes = cortexCommXMLRootNode.findall('providePort')
 providePorts = list()
 if nodes is not None: 
   for node in nodes:
     providePortName = node.get('name')
     providePortFile = node.get('file')
     providePorts.append( (providePortName, providePortFile) )
 print('providePorts: ',providePorts)

#.................................................................................
# Fourth command line argument is the module runtime-status.xml file
 runtimeStatusFullPathFileName = argv[4]

#---------------------------------------------------------------------------------
# Run Nitron 

# Connect to the use ports 
 for (portName,portFile) in usePorts:
   if portName == 'solids':
      print('MODULE::dissolver.py using port: ',portName)
      fuelBucket = HoldingDrum(portFile)
   if portName == 'condenser-stream':
      print('MODULE::dissolver.py using port: ',portName)

# Connect to the provide ports
 for (portName,portFile) in providePorts:
   if portName == 'vapor':
      print('MODULE::dissolver.py providing port: ',portName)
   if portName == 'product':
      print('MODULE::dissolver.py providing port: ',portName)
   if portName == 'heat':
      print('MODULE::dissolver.py providing port: ',portName)

# Evolve the dissolver; solids use port is used below
 dissolverMassLoadMax = 250.0 # grams
 isDissolverReady2Load = True
#................................................................................
 for evolTime in range(int(evolveTime)):

#  print('DISSOLVER time ',evolTime)

# wait until there is enough fuel in the bucket  
  if isDissolverReady2Load == True:

    if  fuelBucket.GetMass(evolTime) < dissolverMassLoadMax and \
        fuelBucket.GetLastTimeStamp() > evolTime: continue

    if  fuelBucket.GetMass(evolTime) >= dissolverMassLoadMax:
#        print('fuelBucket.GetMass(evolTime) = ',fuelBucket.GetMass(evolTime))
        fuelMassLoad = 0.0
        fuelSegmentsLoad = list()
        while fuelMassLoad <= dissolverMassLoadMax:
              fuelSegment = fuelBucket.WithdrawFuelSegment( evolTime )
#              print('fuelBucket.GetMass(evolTime) = ',fuelBucket.GetMass(evolTime))
              mass = fuelSegment[1]
#              print('mass ', mass)
              fuelMassLoad += mass
#              print('fuelMassLoad ', fuelMassLoad)
              if fuelMassLoad <= dissolverMassLoadMax: 
                 fuelSegmentsLoad.append( fuelSegment )
              else: 
                 fuelBucket.RestockFuelSegment( fuelSegment )

    if  fuelBucket.GetMass(evolTime) < dissolverMassLoadMax and \
        fuelBucket.GetLastTimeStamp() <= evolTime:
        fuelMassLoad = 0.0
        fuelSegmentsLoad = list()
        isBucketEmpty = False
        while fuelMassLoad < dissolverMassLoadMax and isBucketEmpty == False:
              fuelSegment = fuelBucket.WithdrawFuelSegment( evolTime )
              if    fuelSegment is None: isBucketEmpty = True
              else: 
                mass = fuelSegment[1]
#                print('mass ', mass)
                fuelMassLoad += mass
                if fuelMassLoad < dissolverMassLoadMax: 
                   fuelSegmentsLoad.append( fuelSegment )

    #*********************************************
    # THIS IS A PLACE HOLDER
    # START  THE DISSOLVER; THIS IS A PLACE HOLDER
    # Uses:     fuelSegmentsLoad
    # Provides: vapor data in the appropriate portName
    runCommand = nitronHomeDir + 'main.m' + ' ' + inputFullPathFileName + ' &'
    print( 'dissolver.py: time ' + runCommand  )
    #os.system( 'time ' + runCommand  )
    SetRuntimeStatus(runtimeStatusFullPathFileName, 'running') 
    print('DISSOLVER start at time = ', evolTime)
    mass = 0.0
    for i in fuelSegmentsLoad: mass += i[1]
    print('DISSOLVER loaded mass = ', mass)
    time.sleep(1)
    #*********************************************

    startDissolverTime    = evolTime
    isDissolverReady2Load = False

  # allow for 120 min dissolution
  if evolTime >= startDissolverTime + 120: isDissolverReady2Load = True

 print('End of all dissolution; time = ',evolTime)
 print('Fuel mass left over in the holding area = ', fuelBucket.GetMass())
      
#................................................................................

# Communicate with Nitron to check running status

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
# Usage: -> python dissolver.py or ./dissolver.py
if __name__ == "__main__":
   main(sys.argv)
