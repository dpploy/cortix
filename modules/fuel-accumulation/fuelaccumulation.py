#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix FuelAccumulation module wrapper

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time
import datetime
import xml.etree.ElementTree as ElementTree
#*********************************************************************************

#*********************************************************************************
class FuelAccumulation(object):

# Private member data
# __slots__ = [

 def __init__( self,
               ports 
             ):

  assert type(ports) is list, '-> ports type %r is invalid.' % type(ports)

  self.__ports = ports

  self.__fuelSegments = list()

  self.__withdrawMass = 0.0

#---------------------------------------------------------------------------------
 def GetMass(self, timeStamp=None):
  return self.__GetMass( timeStamp )

#---------------------------------------------------------------------------------
 def GetNSegments(self, timeStamp=None):
 
  nSegments = 0

  if timeStamp is None:
      nSegments = len(self.__fuelSegments)

  else:
     for fuelSeg in self.__fuelSegments:
      if fuelSeg[0] <= timeStamp: nSegments += 1

  return nSegments

#---------------------------------------------------------------------------------
 def GetLastTimeStamp(self):
 
  lastTimeStamp = 0.0
  for fuelSeg in self.__fuelSegments:
     lastTimeStamp = max(lastTimeStamp,fuelSeg[0])

  return lastTimeStamp

#---------------------------------------------------------------------------------
 def WithdrawFuelSegment(self, evolTime ):

  fuelSegment = self.__WithdrawFuelSegment( evolTime )

  return fuelSegment # if None, it is empty 
#---------------------------------------------------------------------------------
 def RestockFuelSegment( self, fuelSegment ):

  self.__RestockFuelSegment( fuelSegment )

#---------------------------------------------------------------------------------
 def UseData( self, usePortName=None, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( usePortName = usePortName )

# Get data from port files
  if usePortName == 'solids': self.__GetSolids( portFile, evolTime )

  if usePortName == 'withdrawal-request': self.__GetWithdrawalRequest( portFile, evolTime )

#---------------------------------------------------------------------------------
 def ProvideData( self, providePortName=None, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( providePortName = providePortName )

# Send data to port files
  if providePortName == 'fuel-segments': self.__ProvideFuelSegments( portFile, evolTime )

#---------------------------------------------------------------------------------
 def __GetPortFile( self, usePortName=None, providePortName=None ):

  portFile = None

  if usePortName is not None:

    assert providePortName is None

    for port in self.__ports:
     if port[0] == usePortName and port[1] == 'use': portFile = port[2]

    maxNTrials = 5
    nTrials    = 0
    while not os.path.isfile(portFile) and nTrials < maxNTrials:
      nTrials += 1
      print('FuelAccumulation::__GetPortFile: waiting for port:',portFile)
      time.sleep(5)

    assert os.path.isfile(portFile) is True, 'portFile %r not available' % portFile

  if providePortName is not None:

    assert usePortName is None

    for port in self.__ports:
     if port[0] == providePortName and port[1] == 'provide': portFile = port[2]
 

  assert portFile is not None, 'portFile is invalid.'

  return portFile

#---------------------------------------------------------------------------------
# This uses a use portFile which is guaranteed at this point
 def __GetSolids( self, portFile, evolTime ):

  tree = ElementTree.parse(portFile)
  rootNode = tree.getroot()
  durationNode = rootNode.find('Duration')
  timeStep = float(durationNode.get('timeStep'))
#  print('timeStep = ',timeStep)
  streamNode = rootNode.find('Stream')
#  print(streamNode.get('name'))
  timeNodes = streamNode.findall('Time')
#  print(len(timeNodes))

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
   timeStamp = timeStep*timeIndex          

   if timeStamp == evolTime: 

#   print('Time index = ',timeIndex)
     n = timeNode.find('Segment_Length')
 
     if n is None: continue # to the next timeNode
 
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

     for seg in range(1,int(nSegments)+1):
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

  return

#---------------------------------------------------------------------------------
# This uses a use portFile which is guaranteed at this point
 def __GetWithdrawalRequest( self, portFile, evolTime ):

  print('FuelAccumulation::__GetWithdrawalRequest: getting withdrawal request')
  tree = ElementTree.parse(portFile)
  rootNode = tree.getroot()

  n             = rootNode.find('timeStamp')
  timeStamp     = float(n.get('value').strip())

  if timeStamp != evolTime: 
     trial += 1
     time.sleep(2)

  assert timeStamp == evolTime, 'timeStamp = %r, evolTime = %r' % (timeStamp,evolTime)

  timeStampUnit = n.get('unit').strip()
  assert timeStampUnit == "minute"

  mass = 0.0
  subn = n.find('fuelLoad')
  if subn is not None:
     mass     = float(subn.text.strip())
     massUnit = subn.get('unit').strip()
     assert massUnit == "gram"
     self.__withdrawMass = mass
  else:
     self.__withdrawMass = 0.0

#  print('FuelAccumulation::__GetWithdrawalRequest(): mass ', self.__withdrawMass) 
#  print('FuelAccumulation::__GetWithdrawalRequest(): unit ', massUnit) 

# remove the request
  os.system( 'rm -f ' + portFile )

  return 

#---------------------------------------------------------------------------------
 def __GetMass(self, timeStamp=None):
 
  mass = 0.0

  if timeStamp is None:
     for fuelSeg in self.__fuelSegments:
      mass += fuelSeg[1]

  else:
     for fuelSeg in self.__fuelSegments:
      if fuelSeg[0] <= timeStamp: mass += fuelSeg[1]

  return mass

#---------------------------------------------------------------------------------
 def __ProvideFuelSegments( self, portFile, evolTime ):

  withdrawMass = self.__withdrawMass

  fout = open( portFile, 'w')

  s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
  s = '<!-- Written by FuelAccumulation.py -->\n'; fout.write(s)
  s = '<fuelsegments>\n'; fout.write(s)
  s = ' <timeStamp value="'+str(evolTime)+'" unit="minute">'; fout.write(s)

  if withdrawMass == 0.0 or withdrawMass > self.__GetMass( evolTime ): 

   s = '</timeStamp>\n'; fout.write(s)
   s = '</fuelsegments>\n'; fout.write(s)
   fout.close()
   self.__withdrawMass = 0.0
   return

  else:  

   fuelSegmentsLoad = list()
   fuelMassLoad = 0.0

   while fuelMassLoad <= withdrawMass:
         fuelSegmentCandidate = self.__WithdrawFuelSegment( evolTime )
         if fuelSegmentCandidate is None: break # no segments left with time stamp <= evolTime
         mass          = fuelSegmentCandidate[1]
         fuelMassLoad += mass
         if fuelMassLoad <= withdrawMass:
            fuelSegmentsLoad.append( fuelSegmentCandidate )
         else:
            self.__RestockFuelSegment( fuelSegmentCandidate )

   assert len(fuelSegmentsLoad) != 0

   for fuelSeg in fuelSegmentsLoad:
    s = ' <fuelSegment>\n'; fout.write(s)
    timeStamp = fuelSeg[0]
    mass      = fuelSeg[1]
    length    = fuelSeg[2]
    segID     = fuelSeg[3]
    massU     = fuelSeg[4]
    massPu    = fuelSeg[5]
    massI     = fuelSeg[6]
    massFP    = fuelSeg[7]
    s = '  <timeStamp     unit="minute">'+str(timeStamp)+'</timeStamp>\n'; fout.write(s)
    s = '  <mass          unit="gram">'+str(mass)+'</mass>\n';fout.write(s)
    s = '  <length        unit="m">'+str(length)+'</length>\n';fout.write(s)
    s = '  <innerDiameter unit="m">'+str(segID)+'</innerDiameter>\n';fout.write(s)
    s = '  <U  unit="gram">'+str(massU)+'</U>\n';fout.write(s)
    s = '  <Pu unit="gram">'+str(massPu)+'</Pu>\n';fout.write(s)
    s = '  <I  unit="gram">'+str(massI)+'</I>\n';fout.write(s)
    s = '  <FP unit="gram">'+str(massFP)+'</FP>\n';fout.write(s)
    s = '</fuelSegment>\n';      fout.write(s)
 
   s = '</timeStamp>\n'; fout.write(s)
   s = '</fuelsegments>\n'; fout.write(s)
   fout.close()

  return

#---------------------------------------------------------------------------------
 def __WithdrawFuelSegment(self, evolTime ):

  fuelSegment = None

  for fuelSeg in self.__fuelSegments:
     if fuelSeg[0] <= evolTime:
      fuelSegment = fuelSeg
      self.__fuelSegments.remove(fuelSeg)
      break 

#  print('WithdrawFuelSegment:: fuelSegment',fuelSegment, ' evolTime=',evolTime)

  return fuelSegment # if None, it is an empty drum

#---------------------------------------------------------------------------------
 def __RestockFuelSegment( self, fuelSegment ):

  self.__fuelSegments.insert(0,fuelSegment)

#*********************************************************************************
# Usage: -> python fuelaccumulation.py
if __name__ == "__main__":
 print('Unit testing for FuelAccumulation')
