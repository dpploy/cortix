#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Dissolver module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import math, random
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

  self.__solidsMassLoadMax = 670.0 # gram
  self.__dutyPeriod        = 120.0 # minute

  self.__ready2LoadFuel    = True   # this is a major control variable
  self.__startDissolveTime = -1.0   # this is a major control variable

  self.__fuelSegmentsLoad = None
  self.__loadedFuelMass   = None  # this is also a major control variable
  self.__loadedFuelVolume = None  # this is also a major control variable

#  self.__stateHistory = list(dict())

  self.__historyXeMassVapor = dict()
  self.__gasSpeciesFuelLoad = dict()

  self.__log = logging.getLogger('dissolver')
  self.__log.info('initializing an instance of Dissolver')

  self.__gramDecimals = 3 # milligram significant digits
  self.__mmDecimals   = 3 # micrometer significant digits

#---------------------------------------------------------------------------------
 def CallPorts( self, evolTime=0.0 ):

  self.__ProvideData( providePortName='solids-request', evolTime=evolTime )     

  self.__UseData( usePortName='solids', evolTime=evolTime )     

  self.__ProvideData( providePortName='Xe-vapor', evolTime=evolTime )     

#---------------------------------------------------------------------------------
# Evolve system from evolTime to evolTime+timeStep
 def Execute( self, evolTime=1.0, timeStep=1.0 ):

  s = 'Execute(): facility time [min] = ' + str(evolTime)
  self.__log.info(s)

  self.__Dissolve( evolTime, timeStep ) # starting at evolTime to evolTime + timeStep

#---------------------------------------------------------------------------------
 def __UseData( self, usePortName=None, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( usePortName = usePortName )

# Get data from port files
  if usePortName == 'solids': 

     if self.__ready2LoadFuel is True:
        self.__fuelSegmentsLoad = self.__GetSolids( portFile, evolTime )

     if self.__fuelSegmentsLoad is not None: 
        self.__ready2LoadFuel    = False
        self.__startDissolveTime = evolTime

#---------------------------------------------------------------------------------
 def __ProvideData( self, providePortName=None, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( providePortName = providePortName )

# Send data to port files
  if providePortName == 'solids-request': self.__ProvideSolidsRequest( portFile, evolTime )
  if providePortName == 'Xe-vapor': self.__ProvideXeVapor( portFile, evolTime )

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
    s = ' <var name="Fuel Request" unit="gram" legend="dissolver"/>\n'; fout.write(s)

    s = '__ProvideSolidsRequest(): evolTime = '+str(evolTime)
    self.__log.debug(s)
    s = '__ProvideSolidsRequest(): ready to load = '+str(self.__ready2LoadFuel)
    self.__log.debug(s)

    if  self.__ready2LoadFuel is True:
 
      if self.__startDissolveTime >= 0.0:
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

          if self.__startDissolveTime >= 0.0:
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
 def __Dissolve( self, evolTime, timeStep ):

  #..........
  # new start
  #..........
  if evolTime == self.__startDissolveTime: # this is the beginning of a duty cycle

    s = '__Dissolve(): starting new duty cycle at ' + str(evolTime) + ' [min]'
    self.__log.info(s)
    self.__loadedFuelMass = (mass,unit) = self.__GetFuelLoadMass()
    s = '__Dissolve(): loaded mass ' + str(round(mass,3)) + ' [' + unit + ']'
    self.__log.info(s)
    self.__loadedFuelVolume = (volume,unit) = self.__GetFuelLoadVolume()
    s = '__Dissolve(): loaded volume ' + str(round(volume,3)) + ' [' + unit + ']'
    self.__log.info(s)
    nSegments = len(self.__fuelSegmentsLoad[0])
    s = '__Dissolve(): new fuel load # segments = ' + str(nSegments)
    self.__log.info(s)

    self.__gasSpeciesFuelLoad = self.__GetFuelLoadGasSpecies()

    self.__fuelSegmentsLoad = None # clear the load

    s = '__Dissolve(): begin dissolving...' 
    self.__log.info(s)

    self.__UpdateStateVariables( evolTime, timeStep )

  #.....................
  # continue dissolving
  #.....................
  elif evolTime > self.__startDissolveTime and self.__loadedFuelMass is not None:

    s = '__Dissolve(): continue dissolving...' 
    self.__log.info(s)

    self.__UpdateStateVariables( evolTime, timeStep )
  
    if  evolTime + timeStep >= self.__startDissolveTime + self.__dutyPeriod: # time for new load

      s = '__Dissolve(): signal new duty cycle for ' + str(evolTime+timeStep)+' [min]'
      self.__log.info(s)

      self.__ready2LoadFuel   = True
      self.__loadedFuelMass   = None
      self.__loadedFuelVolume = None

  #.............................
  # do nothing in this time step
  #.............................
  else: 

      s = '__Dissolve(): idle at ' + str(evolTime)+' [min]'
      self.__log.info(s)

  return

#---------------------------------------------------------------------------------
 def __UpdateStateVariables( self, evolTime, timeStep ):
  
  (massXe, massXeUnit) = self.__gasSpeciesFuelLoad['Xe'] 

# place holder for evolving Xe in dissolution; 
# modeling as a log-normal distribution with positive skewness (right-skewness)
#
  t0 = self.__startDissolveTime 
  tf = t0 + self.__dutyPeriod
  sigma = 0.7
  mean = math.log(10) + sigma**2

  variability = 1.0 - random.random() * 0.15

  t = evolTime - t0
  if t == 0: 
    logNormalPDF = 0.0
  else:
    logNormalPDF = 1.0/t/sigma/math.sqrt(2.0*math.pi) * \
                 math.exp( - (math.log(t) - mean)**2 / 2/ sigma**2 )

  self.__historyXeMassVapor[evolTime+timeStep] = massXe * logNormalPDF * variability

#---------------------------------------------------------------------------------
 def __ProvideXeVapor( self, portFile, evolTime ):

  # if the first time step, write the header of a time-series data file
  if evolTime == 0.0:

    fout = open( portFile, 'w')

    s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
    s = '<time-series name="XeVapor">\n'; fout.write(s) 
    s = ' <comment author="cortix.modules.native.dissolver" version="0.1"/>\n'; fout.write(s)
    today = datetime.datetime.today()
    s = ' <comment today="'+str(today)+'"/>\n'; fout.write(s)
    s = ' <time unit="minute"/>\n'; fout.write(s)
    s = ' <var name="Xe Vapor Flow" unit="gram" legend="dissolver"/>\n'; fout.write(s)
    mass = 0.0
    s = ' <timeStamp value="'+str(evolTime)+'">'+str(mass)+'</timeStamp>\n';fout.write(s)

    s = '</time-series>\n'; fout.write(s)
    fout.close()

  # if not the first time step then parse the existing history file and append
  else:

    tree = ElementTree.parse( portFile )
    rootNode = tree.getroot()
    a = ElementTree.Element('timeStamp')
    a.set('value',str(evolTime))
    gDec = self.__gramDecimals
    if len(self.__historyXeMassVapor.keys()) > 0:
      mass = round(self.__historyXeMassVapor[evolTime],gDec)
    else:
      mass = 0.0
    a.text = str(mass)

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#*********************************************************************************
# Usage: -> python dissolver.py
if __name__ == "__main__":
 print('Unit testing for Dissolver')
