#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native PyPlot module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import logging
import xml.etree.ElementTree as ElementTree
#*********************************************************************************

#*********************************************************************************
class PyPlot(object):

# Private member data
# __slots__ = [

 def __init__( self,
               ports 
             ):

  assert type(ports) is list, '-> ports type %r is invalid.' % type(ports)

  self.__ports = ports

  self.__fuelSegments = list()

  self.__withdrawMass = 0.0

  self.__log = logging.getLogger('pyplot')
  self.__log.info('initializing an instance of PyPlot')

  self.__gramDecimals = 3 # milligram significant digits

#---------------------------------------------------------------------------------
 def CallPorts(self, evolTime=0.0):

  self.__UseData( usePortName='time-series', evolTime=evolTime  )
 
#---------------------------------------------------------------------------------
 def Execute( self, evolTime=0.0, timeStep=1.0 ):

  s = 'Execute(): facility time [min] = ' + str(evolTime)
  self.__log.info(s)
  s = 'Execute(): total mass [g] = ' + str(round(self.__GetMass(),3))
  self.__log.info(s)

#---------------------------------------------------------------------------------
 def __UseData( self, usePortName=None, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( usePortName = usePortName )

# Get data from port files
  if usePortName == 'time-series': self.__TimeSeries( portFile, evolTime )

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

    maxNTrials = 50
    nTrials    = 0
    while not os.path.isfile(portFile) and nTrials < maxNTrials:
      nTrials += 1
      time.sleep(1)

    if nTrials >= 10:
      s = '__GetPortFile(): waited ' + str(nTrials) + ' trials for port: ' + portFile
      self.__log.warn(s)

    assert os.path.isfile(portFile) is True, 'portFile %r not available; stop.' % portFile

  if providePortName is not None:

    assert usePortName is None

    for port in self.__ports:
     if port[0] == providePortName and port[1] == 'provide': portFile = port[2]

  assert portFile is not None, 'portFile is invalid.'

  return portFile

#---------------------------------------------------------------------------------
# This uses a use portFile which is guaranteed at this point
 def __GetTineSeries( self, portFile, evolTime ):

  tree = ElementTree.parse(portFile)

  rootNode = tree.getroot()

  durationNode = rootNode.find('Duration')

  timeStep = float(durationNode.get('timeStep'))
  s = '__GetSolids(): timeStep='+str(timeStep)
  self.__log.debug(s)

  streamNode = rootNode.find('Stream')
  s = '__GetSolids(): streamNode='+streamNode.get('name')
  self.__log.debug(s)

  timeNodes = streamNode.findall('Time')
  s = '__GetSolids(): # time nodes ='+str(len(timeNodes))
  self.__log.debug(s)

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
   s = '__GetSolids(): timeIndex='+str(timeIndex)
   self.__log.debug(s)

   timeStamp = timeStep*timeIndex          

   s = '__GetSolids(): timeStamp='+str(timeStamp)
   self.__log.debug(s)

   if timeStamp == evolTime: 

     s = '__GetSolids(): timeStamp='+str(timeStamp)+';'+' evolTime='+str(evolTime)
     self.__log.debug(s)

#   print('Time index = ',timeIndex)
     n = timeNode.find('Segment_Length')
 
     if not ElementTree.iselement(n): continue # to the next timeNode
 
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
      segMass   = totalMass / int(nSegments)
      segLength = segmentLength
      segID     = iD
      U         = U  / int(nSegments)
      Pu        = Pu / int(nSegments)
      I         = I  / int(nSegments)
      Kr        = Kr / int(nSegments)
      Xe        = Xe / int(nSegments)
      a3H       = a3H/ int(nSegments)
      FP        = FP / int(nSegments)
      segment   = ( timeStamp, segMass, segLength, segID, 
                    U, Pu, I, Kr, Xe, a3H, FP )

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

#*********************************************************************************
# Usage: -> python pyplot.py
if __name__ == "__main__":
 print('Unit testing for PyPlot')
