#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Dissolver module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import math
import logging
import xml.etree.ElementTree as ElementTree
#*********************************************************************************

#*********************************************************************************
class Dissolver(object):

# Private member data
# __slots__ = [

 def __init__( self,
               ports
             ):

# Sanity test
  assert type(ports) is list, '-> ports type %r is invalid.' % type(ports)

# Member data 

  self.__ports = ports

  self.__solidsMassLoadMax = 250.0 # gram
  self.__dutyPeriod        = 120.0 # minute
  self.__ready2LoadFuel    = True 

  self.__fuelSegmentsLoad = None

  self.__startDissolveTime = 0.0

  self.__stateHistory = list(dict())

  self.__log = logging.getLogger('dissolver')
  self.__log.info('initializing an instance of Dissolver')

#---------------------------------------------------------------------------------
 def CallPorts( self, evolTime=0.0 ):

  self.__ProvideData( providePortName='solids-request', evolTime=evolTime )     

  self.__UseData( usePortName='solids', evolTime=evolTime )     

#---------------------------------------------------------------------------------
 def Execute( self, evolTime=0.0, timeStep=1.0 ):

#  print('Dissolver::Execute: start dissolve time = ', self.__startDissolveTime)

  s = 'Execute(): facility time [min] = ' + str(evolTime)
  self.__log.info(s)

  if self.__fuelSegmentsLoad is not None:

     s = 'Execute(): start new duty cycle at ' + str(evolTime) + ' [min]'
     self.__log.info(s)
     s = 'Execute(): ready to load? = ' + str(self.__ready2LoadFuel)
     self.__log.info(s)
     (mass,unit) = self.__GetFuelLoadMass()
     s = 'Execute(): loaded mass ' + str(round(mass,3)) + ' [' + unit + ']'
     self.__log.info(s)
     (volume,unit) = self.__GetFuelLoadVolume()
     s = 'Execute(): loaded volume ' + str(round(volume,3)) + ' [' + unit + ']'
     self.__log.info(s)
     nSegments = len(self.__fuelSegmentsLoad[0])
     s = 'Execute(): new fuel load # segments = ' + str(nSegments)
     self.__log.info(s)

     if self.__startDissolveTime != 0.0:
        assert evolTime >= self.__startDissolveTime + self.__dutyPeriod

     self.__ready2LoadFuel    = False
     self.__startDissolveTime = evolTime

     self.__Dissolve( )

  if evolTime >= self.__startDissolveTime + self.__dutyPeriod: 
     s = 'Execute(): signal new duty cycle at ' + str(evolTime)+' [min]'
     self.__log.info(s)

     assert self.__fuelSegmentsLoad is None

     self.__ready2LoadFuel = True

     s = 'Execute(): ready to load? = ' + str(self.__ready2LoadFuel)
     self.__log.debug(s)

#---------------------------------------------------------------------------------
 def __UseData( self, usePortName=None, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( usePortName = usePortName )

# Get data from port files
  if usePortName == 'solids': 
     self.__fuelSegmentsLoad = self.__GetSolids( portFile, evolTime )

#---------------------------------------------------------------------------------
 def __ProvideData( self, providePortName=None, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( providePortName = providePortName )

# Send data to port files
  if providePortName == 'solids-request': self.__ProvideSolidsRequest( portFile, evolTime )

#---------------------------------------------------------------------------------
 def __GetPortFile( self, usePortName=None, providePortName=None ):

  portFile = None

  if usePortName is not None:

    assert providePortName is None

    for port in self.__ports:
     if port[0] == usePortName and port[1] == 'use': portFile = port[2]

    maxNTrials = 50
    nTrials    = 0
    while os.path.isfile(portFile) is False and nTrials <= maxNTrials:
      nTrials += 1
      time.sleep(1)

    if nTrials >= 10:
      s = '__GetPortFile(): waited ' + str(nTrials) + ' trials for port: ' + portFile
      self.__log.warn(s)

    assert os.path.isfile(portFile) is True, 'portFile %r not available; stop' % portFile
    time.sleep(1) # allow for file to finish writing

  if providePortName is not None:

    assert usePortName is None

    for port in self.__ports:
     if port[0] == providePortName and port[1] == 'provide': portFile = port[2]
 
  assert portFile is not None, 'portFile %r is invalid.' % portFile

  return portFile

#---------------------------------------------------------------------------------
 def __ProvideSolidsRequest( self, portFile, evolTime ):
 
  # if the first time step, write the header of a time-series data file
  if evolTime == 0.0:

    fout = open( portFile, 'w')

    s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
    s = '<time-series name="dissolutionFuelRequest">\n'; fout.write(s) 
    s = ' <comment author="cortix.modules.native.dissolver" version="0.1"/>\n'; fout.write(s)
    today = datetime.datetime.today()
    s = ' <comment today="'+str(today)+'"/>\n'; fout.write(s)
    s = ' <time unit="minute"/>\n'; fout.write(s)
    s = ' <var name="Fuel Mass Request" unit="gram"/>\n'; fout.write(s)

    s = '__ProvideSolidsRequest(): evolTime = '+str(evolTime)
    self.__log.debug(s)
    s = '__ProvideSolidsRequest(): ready to load = '+str(self.__ready2LoadFuel)
    self.__log.debug(s)

    if  self.__ready2LoadFuel is True:
 
      if self.__startDissolveTime != 0.0:
        assert evolTime >= self.__startDissolveTime + self.__dutyPeriod

      s = ' <timeStamp value="'+str(evolTime)+'">'+str(self.__solidsMassLoadMax)+'</timeStamp>\n';fout.write(s)

    s = '</time-series>\n'; fout.write(s)
    fout.close()

  # if not the first time step then parse the existing history file and append
  else:

    tree = ElementTree.parse( portFile )
    rootNode = tree.getroot()
    a = ElementTree.Element('timeStamp')
    a.set('value',str(evolTime))
    if  self.__ready2LoadFuel == True:
      a.text = str(self.__solidsMassLoadMax)
    else:
      a.text = '0'

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 


#---------------------------------------------------------------------------------
 def __ProvideSolidsRequest_DEPRECATED( self, portFile, evolTime ):
 
  # if the first time step, write a nice header
  if evolTime == 0.0:

    fout = open( portFile, 'w')
    s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
    s = '<!-- Written by Dissolver.py -->\n'; fout.write(s)
    today = datetime.datetime.today()
    s = '<!-- '+str(today)+' -->\n'; fout.write(s)
    s = '<dissolutionFuelRequest>\n'; fout.write(s)
    s = ' <timeStamp value="'+str(evolTime)+'" unit="minute">\n'; fout.write(s)

    s = '__ProvideSolidsRequest(): evolTime = '+str(evolTime)
    self.__log.debug(s)
    s = '__ProvideSolidsRequest(): ready to load = '+str(self.__ready2LoadFuel)
    self.__log.debug(s)


    if  self.__ready2LoadFuel is True:
 
      if self.__startDissolveTime != 0.0:
        assert evolTime >= self.__startDissolveTime + self.__dutyPeriod

      s = '  <var value="'+str(self.__solidsMassLoadMax)+'" unit="gram">Fuel Mass Requested</var>\n';fout.write(s)


    s = ' </timeStamp>\n'; fout.write(s)
    s = '</dissolutionFuelRequest>\n'; fout.write(s)
    fout.close()

  # if not the first time step then parse the existing history file and append
  else:

    tree = ElementTree.parse( portFile )
    rootNode = tree.getroot()
    a = ElementTree.Element('timeStamp')
    a.set('value',str(evolTime))
    a.set('unit','minute')
    if  self.__ready2LoadFuel == True:
      b = ElementTree.SubElement(a, 'var')
      b.set('value',str(self.__solidsMassLoadMax))
      b.set('unit','gram')
      b.text = 'Fuel Mass Requested'

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#---------------------------------------------------------------------------------
# Reads the solids from an existing history file
 def __GetSolids( self, portFile, evolTime ):

  fuelSegmentsLoad = None

  found = False

  while found is False:

    try:
      tree = ElementTree.parse( portFile )
    except ElementTree.ParseError as error:
      s = '__GetSolids(): '+portFile+' unavailable. Error code: '+str(error.code)+' File position: '+str(error.position)+'. Retrying...'
      self.__log.debug(s)
      continue

    rootNode = tree.getroot()

    nodes = rootNode.findall('timeStamp')

    for n in nodes:

      timeStamp = float(n.get('value').strip())

      # get data at timeStamp evolTime
      if timeStamp == evolTime:

        #...........
        found = True
        #...........

        # get data packs
        pack1 = n.findall('pack1')
        pack2 = n.findall('pack2')

        # if there are data packs then read proceed with parsing
        if len(pack1) != 0 or len(pack2) != 0:

          assert self.__ready2LoadFuel is True, 'sanity check failed.'

          if self.__startDissolveTime != 0.0:
             assert evolTime >= self.__startDissolveTime + self.__dutyPeriod, 'sanity check failed.'

          assert len(pack1) != 0 and len(pack2) != 0, 'sanity check failed.'
          assert len(pack1) == len(pack2), 'sanity check failed.'

          #............................
          # read the header information
          #............................

          timeElem = rootNode.find('time')
          timeStampUnit = timeElem.get('unit').strip()
          assert timeStampUnit == "minute"

          pack1Spec = rootNode.findall('pack1')
          assert len(pack1Spec) == 1, 'sanity check failed.'
          pack1Spec = rootNode.find('pack1')
 
          pack1Name = pack1Spec.get('name').strip()
          assert pack1Name == 'Geometry'

          # [(name,unit),(name,unit),...]
          segmentGeometrySpec = list()
          for child in pack1Spec:
            attributes = child.items()
            assert len(attributes) == 2
            for attribute in attributes:
              if   attribute[0] == 'name': name = attribute[1]
              elif attribute[0] == 'unit': unit = attribute[1]
              else: assert True
            segmentGeometrySpec.append( (name, unit) )

          pack2Spec = rootNode.findall('pack2')
          assert len(pack2Spec) == 1, 'sanity check failed.'
          pack2Spec = rootNode.find('pack2')
 
          pack2Name = pack2Spec.get('name').strip()
          assert pack2Name == 'Composition'

          # [(name,unit),(name,unit),...]
          segmentCompositionSpec = list()
          for child in pack2Spec:
            attributes = child.items()
            assert len(attributes) == 2
            for attribute in attributes:
              if   attribute[0] == 'name': name = attribute[1]
              elif attribute[0] == 'unit': unit = attribute[1]
              else: assert True
            segmentCompositionSpec.append( (name,unit) )

          #............................
          # read the timeStamp data
          #............................

          # [ [(name,unit,val), (name,unit,val),...], [(name,unit,val),..], ... ]
          segmentsGeometryData = list()
          for pack in pack1:
            packData = pack.text.strip().split(',')
            assert len(packData) == len(segmentGeometrySpec)
            for i in range(len(packData)): packData[i] = float(packData[i])
            segGeomData = list()
            for ((name,unit),val) in zip(segmentGeometrySpec,packData):
              segGeomData.append( (name,unit,val) )
            segmentsGeometryData.append( segGeomData )

          # [ [(name,unit,val), (name,unit,val),...], [(name,unit,val),..], ... ]
          segmentsCompositionData = list()
          for pack in pack2:
            packData = pack.text.strip().split(',')
            assert len(packData) == len(segmentCompositionSpec)
            for i in range(len(packData)): packData[i] = float(packData[i])
            segCompData = list()
            for ((name,unit),val) in zip(segmentCompositionSpec,packData):
              segCompData.append( (name,unit,val) )
            segmentsCompositionData.append( segCompData )

          assert len(segmentsGeometryData) == len(segmentsCompositionData)

          fuelSegmentsLoad = (segmentsGeometryData, segmentsCompositionData) 

        # end of if len(pack1) != 0 or len(pack2) != 0:

      # end of if timeStamp == evolTime:

    # end of for n in nodes:

    if found is False: 
      time.sleep(1)
      s = '__GetSolids(): did not find time stamp '+str(evolTime)+' [min] in '+portFile
      self.__log.debug(s)

  # end of while found is False:

  if fuelSegmentsLoad is None: nSegments = 0
  else:                        nSegments = len(fuelSegmentsLoad[0])

  s = '__GetSolids(): got fuel load at '+str(evolTime)+' [min], with '+str(nSegments)+' segments'
  self.__log.debug(s)

  return  fuelSegmentsLoad

#---------------------------------------------------------------------------------
# Reads the solids from an existing history file
 def __GetSolids_DEPRECATED( self, portFile, evolTime ):

  fuelSegmentsLoad = list()

  found = False

  while found is False:

    try:
      tree = ElementTree.parse( portFile )
    except ElementTree.ParseError as error:
      s = '__GetSolids(): '+portFile+' unavailable. Error code: '+str(error.code)+' File position: '+str(error.position)+'. Retrying...'
      self.__log.debug(s)
      continue

    rootNode = tree.getroot()

    nodes = rootNode.findall('timeStamp')

    for n in nodes:

      timeStamp = float(n.get('value').strip())

      # get data at timeStamp evolTime
      if timeStamp == evolTime:

        found = True

        timeStampUnit = n.get('unit').strip()
        assert timeStampUnit == "minute"

        subn = n.findall('fuelSegment')

        # if there are fuelSegments then read them
        if len(subn) != 0: 

          assert self.__ready2LoadFuel is True, 'sanity check failed.'

          if self.__startDissolveTime != 0.0:
             assert evolTime >= self.__startDissolveTime + self.__dutyPeriod, 'sanity check failed.'

          for fuelSegment in subn:

            store = ()

            for child in fuelSegment:

              if child.tag == 'timeStamp':
                 segTimeStamp     = float(child.text.strip())
                 attributes       = child.items()
                 assert len(attributes) == 1
                 assert attributes[0][0] == 'unit'
                 segTimeStampUnit = attributes[0][1]
              elif child.tag == 'mass':
                 segMass          = float(child.text.strip())
                 attributes       = child.items()
                 attributes       = child.items()
                 assert len(attributes) == 1
                 assert attributes[0][0] == 'unit'
                 segMassUnit = attributes[0][1]
              elif child.tag == 'length':
                 segLength        = float(child.text.strip())
                 attributes       = child.items()
                 assert len(attributes) == 1
                 assert attributes[0][0] == 'unit'
                 segLengthUnit = attributes[0][1]
              elif child.tag == 'innerDiameter':
                 segID            = float(child.text.strip())
                 attributes       = child.items()
                 assert len(attributes) == 1
                 assert attributes[0][0] == 'unit'
                 segIDUnit = attributes[0][1]
              elif child.tag == 'U':
                 segU             = float(child.text.strip())
                 attributes       = child.items()
                 assert len(attributes) == 1
                 assert attributes[0][0] == 'unit'
                 segUUnit = attributes[0][1]
              elif child.tag == 'Pu':
                 segPu            = float(child.text.strip())
                 attributes       = child.items()
                 assert len(attributes) == 1
                 assert attributes[0][0] == 'unit'
                 segPuUnit = attributes[0][1]
              elif child.tag == 'I':
                 segI             = float(child.text.strip())
                 attributes       = child.items()
                 assert len(attributes) == 1
                 assert attributes[0][0] == 'unit'
                 segIUnit = attributes[0][1]
              elif child.tag == 'Kr':
                 segKr            = float(child.text.strip())
                 attributes       = child.items()
                 assert len(attributes) == 1
                 assert attributes[0][0] == 'unit'
                 segKrUnit = attributes[0][1]
              elif child.tag == 'Xe':
                 segXe            = float(child.text.strip())
                 attributes       = child.items()
                 assert len(attributes) == 1
                 assert attributes[0][0] == 'unit'
                 segXeUnit = attributes[0][1]
              elif child.tag == 'a3H':
                 seg3H            = float(child.text.strip())
                 attributes       = child.items()
                 assert len(attributes) == 1
                 assert attributes[0][0] == 'unit'
                 seg3HUnit = attributes[0][1]
              elif child.tag == 'FP':
                 segFP            = float(child.text.strip())
                 attributes       = child.items()
                 assert len(attributes) == 1
                 assert attributes[0][0] == 'unit'
                 segFPUnit = attributes[0][1]
              else:
                 assert True, 'unknown child.'

            # end for child in fuelSegment:

            store = ( segTimeStamp, segMass, segLength, segID, 
                      segU,         segPu,   segI,      segKr,
                      segXe,        seg3H,   segFP             )

            fuelSegmentsLoad.append( store )

          # end of for fuelSegment in subn:

        # end of if len(subn) != 0:

      # end of if timeStamp == evolTime:

    # end of for n in nodes:

    if found is False: 
      time.sleep(1)
      s = '__GetSolids(): did not find time stamp '+str(evolTime)+' [min] in '+portFile
      self.__log.debug(s)

  # end of while found is False:

  s = '__GetSolids(): got fuel load at '+str(evolTime)+' [min], with '+str(len(fuelSegmentsLoad))+' segments'
  self.__log.debug(s)

  return  fuelSegmentsLoad

#---------------------------------------------------------------------------------
 def __GetFuelLoadMass( self ):

  mass = 0.0
  massUnit = 'null'

  if self.__fuelSegmentsLoad is None: return

  segmentsGeoData = self.__fuelSegmentsLoad[0]
  for segmentData in segmentsGeoData:
    for (name,unit,value) in segmentData:
      if name=='mass': 
        mass += value
        massUnit = unit

  return (mass,massUnit)

#---------------------------------------------------------------------------------
 def __GetFuelLoadVolume( self ):

  volume = 0.0
  volumeUnit = 'null'

  if self.__fuelSegmentsLoad is None: return

  segmentsGeoData = self.__fuelSegmentsLoad[0]
  for segmentData in segmentsGeoData:
    for (name,unit,value) in segmentData:
      if name=='length': 
        length = value
        lengthUnit = unit
      if name=='innerDiameter': 
        iD = value
        iDUnit = unit
    volume += length * math.pi * iD

  if lengthUnit=='mm' and iDUnit=='mm': 
     volumeUnit = 'cc'
     volume /= 1000.0
  else:
     assert True, 'invalid unit'

  return (volume,volumeUnit)

#---------------------------------------------------------------------------------
 def __GetFuelLoadGasSpecies( self ):

  gasSpecies = dict()

  if self.__fuelSegmentsLoad is None: return
 
  massI  = 0.0
  massKr = 0.0
  massXe = 0.0
  mass3H = 0.0

  segmentsCompData = self.__fuelSegmentsLoad[1]
  for segmentData in segmentsCompData:
    for (name,unit,value) in segmentData:
      if name=='I': 
         massI   += value
         massIUnit = unit
      if name=='Kr': 
         massKr += value
         massKrUnit = unit
      if name=='Xe': 
         massXe += value
         massXeUnit = unit
      if name=='3H': 
         mass3H += value
         mass3HUnit = unit

  gasSpecies = {'I':(massI,massIUnit), 'Kr':(massKr,massKrUnit),
                'Xe':(massXe,massXeUnit), '3H':(mass3H,mass3HUnit)}

  return gasSpecies

#---------------------------------------------------------------------------------
 def __Dissolve( self ):

#  self.__DissolverSetupSolids()

#  self.__stateHistory
  
  
  self.__fuelSegmentsLoad = None

  return

#*********************************************************************************
# Usage: -> python dissolver.py
if __name__ == "__main__":
 print('Unit testing for Dissolver')
