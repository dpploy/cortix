#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix Nitron dissolver module wrapper 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time
import datetime
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
#*********************************************************************************

#---------------------------------------------------------------------------------
def SetupHoldingDrum( portFile ):

 tree = ElementTree()

 tree.parse(portFile)
 rootNode = tree.getroot()
 durationNode = rootNode.find('Duration')
 timeStep = float(durationNode.get('timeStep'))
 print(timeStep)
 streamNode = rootNode.find('Stream')
 print(streamNode.get('name'))
 timeNodes = streamNode.findall('Time')
 print(len(timeNodes))

 dataHistory = list()
 drumInventory = list()

 totalMass = 0.0
 totalNSegments = 0.0
 totalU    = 0.0
 totalPu   = 0.0
 totalCs   = 0.0
 totalI    = 0.0
 totalO    = 0.0
 totalN    = 0.0
 totalFP   = 0.0

 for timeNode in timeNodes:
  timeMass = 0.0
  timeU    = 0.0
  timePu   = 0.0
  timeCs   = 0.0
  timeI    = 0.0
  timeO    = 0.0
  timeN    = 0.0
  timeFP   = 0.0

  timeIndex = int(timeNode.get('index'))

 # print('Time index = ',timeIndex)
  n = timeNode.find('Segment_Length')

  if n is None: 
     load = ( timeStep*timeIndex  )
     dataHistory.append( load )
     accumLoad = ( timeStep*timeIndex, totalMass, totalNSegments, segmentLength, 
                   iD, 
                   totalU, totalPu, totalI, totalFP )
     drumInventory.append( accumLoad )
     continue

  segmentLength = float(n.get('length'))
  n = timeNode.find('Segment_Outside_Diameter')
  oD = float(n.get('outside_diameter'))
  n = timeNode.find('Segment_Inside_Diameter')
  iD = float(n.get('inside_diameter'))
  n = timeNode.find('Segments_Output_This_Timestep')
  nSegments = float(n.get('segments_output'))

  elements = timeNode.findall('Element')
  for element in elements:
    isotopes = element.findall('Isotope')
    for isotope in isotopes:
     for child in isotope:
        if child.tag == 'Mass': 
           mass = float(child.text.strip())
           totalMass += mass
           timeMass  += mass
           if element.get('key') == 'U' : timeU  += mass; totalU  += mass
           if element.get('key') == 'Pu': timePu += mass; totalPu += mass
           if element.get('key') == 'Cs': timeCs += mass; totalCs += mass
           if element.get('key') == 'I' : timeI  += mass; totalI  += mass
           if element.get('key') == 'O' : timeO  += mass; totalO  += mass
           if element.get('key') == 'N' : timeN  += mass; totalN  += mass

#  print('mass     [g]= ', timeMass)
#  print('#segments   = ', nSegments)
#  print('length      = ', segmentLength)
#  print('OD          = ', oD)
#  print('ID          = ', iD)

  timeFP   = timeMass - (timeU + timePu + timeI)
  totalFP += timeFP
  totalNSegments += nSegments

#  print('mass U      = ', timeU)
#  print('mass Pu     = ', timePu)
#  print('mass Cs     = ', timeCs)
#  print('mass I      = ', timeI)
#  print('mass O      = ', timeO)
#  print('mass N      = ', timeN)
#  print('mass FP     = ', timeFP)

  load = ( timeStep*timeIndex, timeMass, nSegments, segmentLength, iD, 
           timeU, timePu, totalI, timeFP )
  
  for seg in range(int(nSegments)):
  segMass   = timeMass / nSegments
  segLength = segmentLength
  segment = ( timeStep*timeIndex, 

  dataHistory.append( load )
  
  accumLoad = ( timeStep*timeIndex, totalMass, totalNSegments, segmentLength, iD, 
                totalU, totalPu, totalI, totalFP )

  drumInventory.append( accumLoad )

 print('totalMass     [g]= ', totalMass)
 print('total # segm. [g]= ', totalNSegments)
 print('total U       [g]= ', totalU)
 print('total Pu      [g]= ', totalPu)
 print('total Cs      [g]= ', totalCs)
 print('total I       [g]= ', totalI)
 print('total O       [g]= ', totalO)
 print('total N       [g]= ', totalN)
 print('total FP      [g]= ', totalFP)

 return dataHistory

#---------------------------------------------------------------------------------
def GetFuel( time, drumInventory,  ):

 for item in dataHistory:
  

#*********************************************************************************
# Usage: -> python holdingdrum-fuel.py or ./holdingdrum.py
if __name__ == "__main__":
 print('Unit testing for SetupHoldingDrum')
 portFile = '/home/dealmeida/mac-fvu/gentoo-home/work/codes/reprocessing/cortix/modules/chopper/HeadEnd_Fuel_Solid.xml'
 SetupHoldingDrum(portFile)
