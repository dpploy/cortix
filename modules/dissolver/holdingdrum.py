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

#*********************************************************************************
class HoldingDrum(object):

# Private member data
# __slots__ = [

 def __init__( self,
               portFile = None 
             ):

  if portFile is not None: 
   assert type(portFile) == str, '-> portFile is invalid.' 

  self.__fuelSegments = list()

  self.__SetupHoldingDrum( portFile )

#---------------------------------------------------------------------------------
 def GetMass(self, timeStamp=None):
 
  mass = 0.0

  if timeStamp is None:
     for fuelSeg in self.__fuelSegments:
      mass += fuelSeg[1]

  else:
     for fuelSeg in self.__fuelSegments:
      if fuelSeg[0] <= timeStamp: mass += fuelSeg[1]

  return mass

#---------------------------------------------------------------------------------
 def GetLastTimeStamp(self):
 
  lastTimeStamp = 0.0
  for fuelSeg in self.__fuelSegments:
     lastTimeStamp = max(lastTimeStamp,fuelSeg[0])

  return lastTimeStamp

#---------------------------------------------------------------------------------
 def WithdrawFuelSegment(self, evolTime ):

  fuelSegment = None

  for fuelSeg in self.__fuelSegments:
     if fuelSeg[0] <= evolTime:
      fuelSegment = fuelSeg
      self.__fuelSegments.remove(fuelSeg)
      break 

#  print('WithdrawFuelSegment:: fuelSegment',fuelSegment, ' evolTime=',evolTime)

  return fuelSegment # if None, it is an empty drum

#---------------------------------------------------------------------------------
 def RestockFuelSegment( self, fuelSegment ):

  self.__fuelSegments.insert(0,fuelSegment)

#---------------------------------------------------------------------------------
 def __SetupHoldingDrum( self, portFile ):

  if os.path.isfile(portFile) is False: time.sleep(5)
  assert os.path.isfile(portFile) is True, 'porFile not available'

  tree = ElementTree()

  tree.parse(portFile)
  rootNode = tree.getroot()
  durationNode = rootNode.find('Duration')
  timeStep = float(durationNode.get('timeStep'))
#  print('timeStep = ',timeStep)
  streamNode = rootNode.find('Stream')
#  print(streamNode.get('name'))
  timeNodes = streamNode.findall('Time')
#  print(len(timeNodes))

#  dataHistory = list()
#  drumInventory = list()
  self.__fuelSegments = list()

  totalMass = 0.0
  totalNSegments = 0.0
  totalU    = 0.0
  totalPu   = 0.0
  totalCs   = 0.0
  totalI    = 0.0
  totalO    = 0.0
  totalN    = 0.0
  totalFP   = 0.0

#.................................................................................
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

#   print('Time index = ',timeIndex)
   n = timeNode.find('Segment_Length')
 
   if n is None: 
#      load = ( timeStep*timeIndex  )
#      dataHistory.append( load )
#      accumLoad = ( timeStep*timeIndex, totalMass, totalNSegments, segmentLength, 
#                    iD, 
#                    totalU, totalPu, totalI, totalFP )
#      drumInventory.append( accumLoad )
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

#   load = ( timeStep*timeIndex, timeMass, nSegments, segmentLength, iD, 
#            timeU, timePu, timeI, timeFP )

#   dataHistory.append( load )
  
   for seg in range(1,int(nSegments)+1):
    timeStamp = timeStep*timeIndex          
#    print('timeStamp = ', timeStamp)
    segMass   = timeMass / int(nSegments)
    segLength = segmentLength
    segID     = iD
    massU     = timeU  / int(nSegments)
    massPu    = timePu / int(nSegments)
    massI     = timeI  / int(nSegments)
    massFP    = timeFP / int(nSegments)
    segment   = ( timeStamp, segMass, segLength, segID, massU, massPu,
                  massI, massFP )

    self.__fuelSegments.append( segment )
  
#   accumLoad = ( timeStep*timeIndex, totalMass, totalNSegments, segmentLength, iD,
#                 totalU, totalPu, totalI, totalFP )

#   drumInventory.append( accumLoad )

#  print('totalMass     [g]= ', totalMass)
#  print('total # segments = ', totalNSegments)
#  print('total # pieces   = ', len(self.__fuelSegments))
#  print('total U       [g]= ', totalU)
#  print('total Pu      [g]= ', totalPu)
#  print('total Cs      [g]= ', totalCs)
#  print('total I       [g]= ', totalI)
#  print('total O       [g]= ', totalO)
#  print('total N       [g]= ', totalN)
#  print('total FP      [g]= ', totalFP)
  
#  print(self.__fuelSegments)
#  for s in self.__fuelSegments:
#   print(s[0],s[1],s[2])
 
#*********************************************************************************
# Usage: -> python holdingdrum-fuel.py or ./holdingdrum.py
if __name__ == "__main__":
 print('Unit testing for SetupHoldingDrum')
 portFile = '/home/dealmeida/mac-fvu/gentoo-home/work/codes/reprocessing/cortix/modules/chopper/HeadEnd_Fuel_Solid.xml'
 bucket = HoldingDrum( portFile )
 print(' mass ', bucket.WithdrawFuelSegment( 0 )[1])
 print(' last time stamp: ',bucket.GetLastTimeStamp())
