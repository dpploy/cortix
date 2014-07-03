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
 def CallPorts(self, evolTime=0.0):

  self.__UseData( usePortName='solids', evolTime=evolTime  )
 
  self.__UseData( usePortName='withdrawal-request', evolTime=evolTime  )

  self.__ProvideData( providePortName='fuel-segments', evolTime=evolTime )

#---------------------------------------------------------------------------------
 def Execute( self, evolTime=0.0, timeStep=1.0 ):

  print('\n')
  print('************************************************')
  print('FuelAccumulation::Execute: evolTime       = ',evolTime )
  print('FuelAccumulation::Execute: # of segments  = ', len(self.__fuelSegments))
  print('FuelAccumulation::Execute: total mass [g] = ', self.__GetMass())
  print('************************************************')

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
 def __UseData( self, usePortName=None, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( usePortName = usePortName )

# Get data from port files
  if usePortName == 'solids': self.__GetSolids( portFile, evolTime )

  if usePortName == 'withdrawal-request': self.__GetWithdrawalRequest( portFile, evolTime )

#---------------------------------------------------------------------------------
 def __ProvideData( self, providePortName=None, evolTime=0.0 ):

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
#      print('FuelAccumulation::__GetPortFile: waiting for port:',portFile)
      time.sleep(1)

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

#.................................................................................
  for timeNode in timeNodes:

   totalMass = 0.0

   U    = 0.0
   Pu   = 0.0
   Cs   = 0.0
   Sr   = 0.0
   I    = 0.0
   Kr   = 0.0
   Xe   = 0.0
   a3H  = 0.0
   Ru   = 0.0
   O    = 0.0
   N    = 0.0
   FP   = 0.0

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
              if element.get('key') == 'U' :  U  += mass; 
              if element.get('key') == 'Pu':  Pu += mass; 
              if element.get('key') == 'Cs':  Cs += mass; 
              if element.get('key') == 'Sr':  Sr += mass; 
              if element.get('key') == 'I' :  I  += mass; 
              if element.get('key') == 'Kr':  Kr += mass; 
              if element.get('key') == 'Kr':  Xe += mass; 
              if element.get('key') == 'H' : a3H += mass; 
              if element.get('key') == 'Ru':  Ru += mass; 
              if element.get('key') == 'O' :  O  += mass; 
              if element.get('key') == 'N' :  N  += mass; 

#  print('mass     [g]= ', mass)
#  print('#segments   = ', nSegments)
#  print('length      = ', segmentLength)
#  print('OD          = ', oD)
#  print('ID          = ', iD)

     FP = totalMass - (U + Pu + I + Kr + Xe + a3H)
#     totalNSegments += nSegments

#  print('mass U      = ', U)
#  print('mass Pu     = ', Pu)
#  print('mass Cs     = ', Cs)
#  print('mass I      = ', I)
#  print('mass O      = ', O)
#  print('mass N      = ', N)
#  print('mass FP     = ', FP)

     for seg in range(1,int(nSegments)+1):
      segMass   = mass / int(nSegments)
      segLength = segmentLength
      segID     = iD
      U         = U  / int(nSegments)
      Pu        = Pu / int(nSegments)
      I         = I  / int(nSegments)
      FP        = FP / int(nSegments)
      segment   = ( timeStamp, segMass, segLength, segID, U, Pu,
                    I, FP )

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

   break

  return

#---------------------------------------------------------------------------------
# This uses a use portFile which is guaranteed at this point
 def __GetWithdrawalRequest( self, portFile, evolTime ):

#  print('FuelAccumulation::__GetWithdrawalRequest: getting withdrawal request')
  tree = ElementTree.parse(portFile)
  rootNode = tree.getroot()

  n             = rootNode.find('timeStamp')
  timeStamp     = float(n.get('value').strip())

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
