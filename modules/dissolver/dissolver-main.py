#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix Dissolver module wrapper 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time
import datetime
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
from nitron import Nitron
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
 for line in fin:
  nitronHomeDir = line.strip()
 fin.close()

 print('dissolver.py: input dir: ',nitronHomeDir)

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
 print('ports: ',ports)

 tree = None

#.................................................................................
# Fourth command line argument is the module runtime-status.xml file
 runtimeStatusFullPathFileName = argv[4]

#---------------------------------------------------------------------------------
# Run Nitron 

#................................................................................
# Setup input

# nothing for now

#................................................................................
# Create the dissolver equipment

# nitron = Nitron( ports )

#................................................................................
# Evolve the dissolver program

 facilityTime = 0.0

 dissolverMassLoadMax  = 250.0 # grams
 isDissolverReady2Load = True

 while facilityTime <= evolveTime:

  if isDissolverReady2Load == True: a = 1

# wait until there is enough fuel in the bucket  
#  if isDissolverReady2Load == True:
#
#    if  fuelBucket.GetMass(facilityTime) < dissolverMassLoadMax and \
#        fuelBucket.GetLastTimeStamp() > facilityTime: continue
#
#    if  fuelBucket.GetMass(facilityTime) >= dissolverMassLoadMax:
##        print('fuelBucket.GetMass(facilityTime) = ',fuelBucket.GetMass(facilityTime))
#        fuelMassLoad = 0.0
#        fuelSegmentsLoad = list()
#        while fuelMassLoad <= dissolverMassLoadMax:
#              fuelSegment = fuelBucket.WithdrawFuelSegment( facilityTime )
##              print('fuelBucket.GetMass(facilityTime) = ',fuelBucket.GetMass(facilityTime))
#              mass = fuelSegment[1]
##              print('mass ', mass)
#              fuelMassLoad += mass
##              print('fuelMassLoad ', fuelMassLoad)
#              if fuelMassLoad <= dissolverMassLoadMax: 
#                 fuelSegmentsLoad.append( fuelSegment )
#              else: 
#                 fuelBucket.RestockFuelSegment( fuelSegment )
#
#    if  fuelBucket.GetMass(facilityTime) < dissolverMassLoadMax and \
#        fuelBucket.GetLastTimeStamp() <= facilityTime:
#        fuelMassLoad = 0.0
#        fuelSegmentsLoad = list()
#        isBucketEmpty = False
#        while fuelMassLoad < dissolverMassLoadMax and isBucketEmpty == False:
#              fuelSegment = fuelBucket.WithdrawFuelSegment( facilityTime )
#              if    fuelSegment is None: isBucketEmpty = True
#              else: 
#                mass = fuelSegment[1]
##                print('mass ', mass)
#                fuelMassLoad += mass
#                if fuelMassLoad < dissolverMassLoadMax: 
#                   fuelSegmentsLoad.append( fuelSegment )
#
#    #*********************************************
#    # THIS IS A PLACE HOLDER
#    # START  THE DISSOLVER; THIS IS A PLACE HOLDER
#    # Uses:     fuelSegmentsLoad
#    # Provides: vapor data in the appropriate portName
#    runCommand = nitronHomeDir + 'main.m' + ' ' + inputFullPathFileName + ' &'
#    print( 'dissolver.py: time ' + runCommand  )
#    #os.system( 'time ' + runCommand  )
#    SetRuntimeStatus(runtimeStatusFullPathFileName, 'running') 
#    print('DISSOLVER start at time = ', facilityTime)
#    mass = 0.0
#    for i in fuelSegmentsLoad: mass += i[1]
#    print('DISSOLVER loaded mass = ', mass)
#    time.sleep(1)
#    #*********************************************
#
#    startDissolverTime    = facilityTime
#    isDissolverReady2Load = False
#
#  # allow for 120 min dissolution
#  if facilityTime >= startDissolverTime + 120: isDissolverReady2Load = True
#
# print('End of all dissolution; time = ',facilityTime)
# print('Fuel mass left over in the holding area = ', fuelBucket.GetMass())
#      
##................................................................................
## Communicate with Nitron to check running status
#
##................................................................................
#
 facilityTime += timeStep 
#
##---------------------------------------------------------------------------------
## Shutdown 
#
# SetRuntimeStatus(runtimeStatusFullPathFileName, 'finished') 
#
## tree.parse(runtimeStatusFullPathFileName)
## runtimeStatusXMLRootNode = tree.getroot()
## root = runtimeStatusXMLRootNode
## node = root.find('status')
## node.text = 'finished'
## a = Element('comment')
## a.text = 'Written by Dissolver.py'
## root.append(a)
## tree.write(runtimeStatusFullPathFileName,xml_declaration=True,encoding="UTF-8",method="xml")
#
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
