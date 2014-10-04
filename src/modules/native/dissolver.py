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
from src.modules.native.core.nitron import Nitron
from scipy.integrate import odeint
#*********************************************************************************

#*********************************************************************************
class Dissolver(object):

# Private member data
# __slots__ = [

 def __init__( self,
               ports,
               evolveTime=0.0
             ):

  # Sanity test
  assert type(ports) is list, '-> ports type %r is invalid.' % type(ports)
  assert type(evolveTime) is float, '-> time type %r is invalid.' % type(evolveTime)
 
  # Logger
  self.__log = logging.getLogger('dissolution.dissolver')
  self.__log.info('initializing an instance of Dissolver')

  # Temporary configuration
  self.__solidsMassLoadMax = 670.0 # gram
  self.__dissolverVolume   = 10.0  # liter
  self.__dutyPeriod        = 120.0 # minute

  self.__molarMassU         = 238.0
  self.__molarMassPu        = 239.0
  self.__molarMassFP        = 135.34-16*1.18
  self.__molarMassH2O       = 18.0    # g/mole
  self.__molarMassHNO3      = 63.0    # g/mole
  self.__molarMassNO        = 30.01   # g/mole
  self.__molarMassNO2       = 46.0055 # g/mole
  self.__molarMassUO2       = 270.05
  self.__molarMassPuO2      = 271.17
  self.__molarMassFPO1dot18 = 135.34
  self.__molarMassUO2NO3_2  = self.__molarMassUO2 + 62.0*2.0 # g/mole
  self.__molarMassPuNO3_4   = self.__molarMassPu  + 62.0*4.0 # g/mole
  self.__molarMassFPNO3_2dot36 = 328.22

  self.__rho_uo2       =  8.300  # g/cc
  self.__rho_puo2      = 11.460
  self.__rho_fpo1dot18 = 12.100

  self.__gramDecimals = 4 # tenth of a milligram significant digits
  self.__mmDecimals   = 3 # micrometer significant digits
  self.__ccDecimals   = 3 # cubic centimeter significant digits

  # Core dissolver module
  self.__nitron = Nitron()

  self.__HNO3molarity = 9  # Molar

  # Member data 
  self.__ports = ports

  self.__ready2LoadFuel    = True   # major control variable
  self.__startDissolveTime = -1.0   # major control variable

  self.__fuelSegmentsLoad = None
  self.__loadedFuelMass   = None  # major control variable
  self.__loadedFuelVolume = None  # major control variable

#  self.__stateHistory = list(dict())

  self.__historyXeMassVapor   = dict()  # persistent variable
  self.__historyXeMassVapor[0.0] = 0.0 

  self.__historyKrMassVapor   = dict()  # persistent variable
  self.__historyI2MassVapor   = dict()  # persistent variable
  self.__historyRuO4MassVapor = dict()  # persistent variable
  self.__historyCO2MassVapor  = dict()  # persistent variable

  self.__historyI2MassLiquid = dict()  # persistent variable
  self.__historyI2MassLiquid[0.0] = 0.0

  self.__historyHNO3Liquid = dict()  # persistent variable
  self.__historyHNO3Liquid[0.0] = 0.0

  self.__loadedSpecies = None  # control variable

#---------------------------------------------------------------------------------
 def CallPorts( self, facilityTime=0.0 ):

  self.__ProvideData( providePortName='signal', atTime=facilityTime )     

  self.__UseData( usePortName='solids', atTime=facilityTime )     

  self.__ProvideData( providePortName='vapor', atTime=facilityTime )     
  self.__ProvideData( providePortName='state', atTime=facilityTime )     

  self.__UseData( usePortName='condensate', atTime=facilityTime )     

#---------------------------------------------------------------------------------
# Evolve system from facilityTime to facilityTime+timeStep
 def Execute( self, facilityTime=0.0, timeStep=1.0 ):

  s = 'Execute(): facility time [min] = ' + str(facilityTime)
  self.__log.info(s)

  self.__Dissolve( facilityTime, timeStep ) # starting at facilityTime advance timeStep

#---------------------------------------------------------------------------------
 def __UseData( self, usePortName=None, atTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( usePortName = usePortName )

# Get data from port files
  if usePortName == 'solids': 

     if self.__ready2LoadFuel is True:
        self.__fuelSegmentsLoad = self.__GetSolids( portFile, atTime )

     if self.__fuelSegmentsLoad is not None: 
        self.__ready2LoadFuel    = False
        self.__startDissolveTime = atTime

  if usePortName == 'condensate': self.__GetCondensate( portFile, atTime )

#---------------------------------------------------------------------------------
 def __ProvideData( self, providePortName=None, atTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( providePortName = providePortName )

# Send data to port files
  if providePortName == 'signal' and portFile is not None: 
    self.__ProvideSignal( portFile, atTime )

  if providePortName == 'vapor' and portFile is not None: 
    self.__ProvideVapor( portFile, atTime )

  if providePortName == 'state' and portFile is not None: 
    self.__ProvideState( portFile, atTime )

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
 
  return portFile

#---------------------------------------------------------------------------------
# Signal to request fuel load
 def __ProvideSignal( self, portFile, facilityTime ):
 
  gDec = self.__gramDecimals

  # if the first time step, write the header of a time-sequence data file
  if facilityTime == 0.0:

    assert os.path.isfile(portFile) is False, 'portFile %r exists; stop.' % portFile

    tree = ElementTree.ElementTree()
    rootNode = tree.getroot()

    a = ElementTree.Element('time-sequence')
    a.set('name','dissolver-signal')

    b = ElementTree.SubElement(a,'comment')
    today = datetime.datetime.today()
    b.set('author','cortix.modules.native.dissolver')
    b.set('version','0.1')

    b = ElementTree.SubElement(a,'comment')
    today = datetime.datetime.today()
    b.set('today',str(today))

    b = ElementTree.SubElement(a,'time')
    b.set('unit','minute')

    # first variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Fuel Request')
    b.set('unit','gram')
    b.set('legend','Dissolver-signal')

    # values for all variables
    b = ElementTree.SubElement(a,'timeStamp')
    b.set('value',str(facilityTime))
    if  self.__ready2LoadFuel == True:
      b.text = str(round(self.__solidsMassLoadMax,gDec))
    else:
      b.text = '0'

    tree = ElementTree.ElementTree(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  # if not the first time step then parse the existing history file and append
  else:

    tree = ElementTree.parse( portFile )
    rootNode = tree.getroot()
    a = ElementTree.Element('timeStamp')
    a.set('value',str(facilityTime))
    if  self.__ready2LoadFuel == True:
      a.text = str(round(self.__solidsMassLoadMax,gDec))
    else:
      a.text = '0'

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#---------------------------------------------------------------------------------
# Reads the solids from an existing history file
 def __GetSolids( self, portFile, facilityTime ):

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

      # get data at timeStamp facilityTime
      if timeStamp == facilityTime:

        #...........
        found = True
        #...........

        # get data packs
        pack1 = n.findall('pack1')
        pack2 = n.findall('pack2')

        # if there are data packs then proceed with parsing
        if len(pack1) != 0 or len(pack2) != 0:

          assert self.__ready2LoadFuel is True, 'sanity check failed.'

          if self.__startDissolveTime >= 0.0:
             assert facilityTime >= self.__startDissolveTime + self.__dutyPeriod, 'sanity check failed.'

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

        # end of: if len(pack1) != 0 or len(pack2) != 0:

      # end of: if timeStamp == facilityTime:

    # end of: for n in nodes:

    if found is False: 
      time.sleep(1)
      s = '__GetSolids(): did not find time stamp '+str(facilityTime)+' [min] in '+portFile
      self.__log.debug(s)

  # end of: while found is False:

  if fuelSegmentsLoad is None: nSegments = 0
  else:                        nSegments = len(fuelSegmentsLoad[0])

  s = '__GetSolids(): got fuel load at '+str(facilityTime)+' [min], with '+str(nSegments)+' segments'
  self.__log.debug(s)

  return  fuelSegmentsLoad

#---------------------------------------------------------------------------------
 def __ProvideVapor( self, portFile, atTime ):

  # if the first time step, write the header of a time-sequence data file
  if atTime == 0.0:

    assert os.path.isfile(portFile) is False, 'portFile %r exists; stop.' % portFile

    tree = ElementTree.ElementTree()
    rootNode = tree.getroot()

    a = ElementTree.Element('time-sequence')
    a.set('name','dissolver-vapor')

    b = ElementTree.SubElement(a,'comment')
    b.set('author','cortix.modules.native.dissolver')
    b.set('version','0.1')

    b = ElementTree.SubElement(a,'comment')
    today = datetime.datetime.today()
    b.set('today',str(today))

    b = ElementTree.SubElement(a,'time')
    b.set('unit','minute')

    # first variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Xe Vapor')
    b.set('unit','gram/min')
    b.set('legend','Dissolver-vapor')

    # second variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Kr Vapor')
    b.set('unit','gram/min')
    b.set('legend','Dissolver-vapor')

    # third variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','I2 Vapor')
    b.set('unit','gram/min')
    b.set('legend','Dissolver-vapor')

    # fourth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','RuO4 Vapor')
    b.set('unit','gram/min')
    b.set('legend','Dissolver-vapor')

    # fifth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','CO2 Vapor')
    b.set('unit','gram/min')
    b.set('legend','Dissolver-vapor')

    # values for all variables
    b = ElementTree.SubElement(a,'timeStamp')
    b.set('value',str(atTime))
    b.text = str('0.0') + ',' + \
             str('0.0') + ',' + \
             str('0.0') + ',' + \
             str('0.0') + ',' + \
             str('0.0')

    tree = ElementTree.ElementTree(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  # if not the first time step then parse the existing history file and append
  else:

    tree = ElementTree.parse( portFile )
    rootNode = tree.getroot()
    a = ElementTree.Element('timeStamp')
    a.set('value',str(atTime))

    # all variables
    gDec = self.__gramDecimals

    if len(self.__historyXeMassVapor.keys()) > 0:
      massXe = round(self.__historyXeMassVapor[atTime],gDec)
    else:
      massXe = 0.0

    if len(self.__historyKrMassVapor.keys()) > 0:
      massKr = round(self.__historyKrMassVapor[atTime],gDec)
    else:
      massKr = 0.0

    if len(self.__historyI2MassVapor.keys()) > 0:
      massI2 = round(self.__historyI2MassVapor[atTime],gDec)
    else:
      massI2 = 0.0

    if len(self.__historyRuO4MassVapor.keys()) > 0:
      massRuO4 = round(self.__historyRuO4MassVapor[atTime],gDec)
    else:
      massRuO4 = 0.0

    if len(self.__historyCO2MassVapor.keys()) > 0:
      massCO2 = round(self.__historyCO2MassVapor[atTime],gDec)
    else:
      massCO2 = 0.0

    a.text = str(massXe)   +','+ \
             str(massKr)   +','+ \
             str(massI2)   +','+ \
             str(massRuO4) +','+ \
             str(massCO2)

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#---------------------------------------------------------------------------------
 def __ProvideState( self, portFile, atTime ):
 
  gDec  = self.__gramDecimals
  ccDec = self.__ccDecimals   

  # if the first time step, write the header of a time-sequence data file
  if atTime == 0.0:

    assert os.path.isfile(portFile) is False, 'portFile %r exists; stop.' % portFile

    tree = ElementTree.ElementTree()
    rootNode = tree.getroot()

    a = ElementTree.Element('time-sequence')
    a.set('name','dissolver-state')

    b = ElementTree.SubElement(a,'comment')
    today = datetime.datetime.today()
    b.set('author','cortix.modules.native.dissolver')
    b.set('version','0.1')

    b = ElementTree.SubElement(a,'comment')
    today = datetime.datetime.today()
    b.set('today',str(today))

    b = ElementTree.SubElement(a,'time')
    b.set('unit','minute')

    # first variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Fuel Loaded')
    if self.__GetFuelLoadMass() is not None:
      (massFuelLoad,unit) = self.__GetFuelLoadMass()
    else:
      massFuelLoad = 0.0
    unit = 'gram'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')

    # second variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Fuel Loaded')
    if self.__GetFuelLoadVolume() is not None:
      (volumeFuelLoad,unit) = self.__GetFuelLoadVolume()
    else:
      volumeFuelLoad = 0.0
    unit = 'cc'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')

    # third variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','I2 Liquid')
    if len(self.__historyI2MassLiquid.keys()) > 0:
      massI2Liquid = self.__historyI2MassLiquid[ atTime ]
    else:
      massI2Liquid = 0.0
    unit = 'gram'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')

    # values for all variables
    b = ElementTree.SubElement(a,'timeStamp')
    b.set('value',str(atTime))
    massFuelLoad   = round(massFuelLoad,gDec)
    volumeFuelLoad = round(volumeFuelLoad,ccDec)
    massI2Liquid   = round(massI2Liquid,gDec)
    b.text = str(massFuelLoad)+','+\
             str(volumeFuelLoad)+','+\
             str(massI2Liquid)

    tree = ElementTree.ElementTree(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  # if not the first time step then parse the existing history file and append
  else:

    tree = ElementTree.parse( portFile )
    rootNode = tree.getroot()
    a = ElementTree.Element('timeStamp')
    a.set('value',str(atTime))

    if self.__GetFuelLoadMass() is not None:
      (massFuelLoad,unit) = self.__GetFuelLoadMass()
      (volumeFuelLoad,unit) = self.__GetFuelLoadVolume()
    else:
      massFuelLoad = 0.0
      volumeFuelLoad = 0.0

    if len(self.__historyI2MassLiquid.keys()) > 0:
      massI2Liquid = self.__historyI2MassLiquid[ atTime ]
    else:
      massI2Liquid = 0.0

    a.text = str(round(massFuelLoad,gDec))+','+\
             str(round(volumeFuelLoad,ccDec))+','+\
             str(round(massI2Liquid,gDec))

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#---------------------------------------------------------------------------------
 def __Dissolve( self, facilityTime, timeStep ):

  #..........
  # new start
  #..........
  if facilityTime == self.__startDissolveTime: # this is the beginning of a duty cycle

    s = '__Dissolve(): starting new duty cycle at ' + str(facilityTime) + ' [min]'
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

    self.__loadedSpecies = self.__GetFuelLoadSpecies()

    self.__fuelSegmentsLoad = None # clear the load

    # set initial concentrations in the liquid phase to zero
    self.__historyI2MassLiquid[ facilityTime ] = 0.0

    s = '__Dissolve(): begin dissolving...' 
    self.__log.info(s)

    #................................................
    self.__UpdateStateVariables( facilityTime, timeStep )
    #................................................

  #.....................
  # continue dissolving
  #.....................
  elif facilityTime > self.__startDissolveTime and self.__loadedFuelMass is not None:

    s = '__Dissolve(): continue dissolving...' 
    self.__log.info(s)

    #................................................
    self.__UpdateStateVariables( facilityTime, timeStep )
    #................................................
  
    if  facilityTime + timeStep >= self.__startDissolveTime + self.__dutyPeriod: # prepare for a new load in the next time step

      s = '__Dissolve(): signal new duty cycle for ' + str(facilityTime+timeStep)+' [min]'
      self.__log.info(s)

      self.__ready2LoadFuel   = True
      self.__loadedFuelMass   = None
      self.__loadedFuelVolume = None
      self.__loadedSpecies = None

  #.............................
  # do nothing in this time step
  #.............................
  else: 

    s = '__Dissolve(): idle and ready ' + str(facilityTime)+' [min]'
    self.__log.info(s)

    # set initial concentrations in the liquid phase to zero
    self.__historyI2MassLiquid[ facilityTime ] = 0.0

    #................................................
    self.__UpdateStateVariables( facilityTime, timeStep )
    #................................................

  return

#---------------------------------------------------------------------------------
 def __UpdateStateVariables( self, facilityTime, timeStep ):
  
  if self.__loadedSpecies is not None:

    # place holder for evolving species in dissolution; 
    # modeling as a log-normal distribution with positive skewness (right-skewness)

    # here is the mass packet entering the system at facilityTime

    for key in self.__loadedSpecies:

      (mass, massUnit) = self.__loadedSpecies[ key ] 

      t0 = self.__startDissolveTime 
      tf = t0 + self.__dutyPeriod
      sigma = 0.7  # right-skewness
      mean = math.log(10) + sigma**2

      t = facilityTime - t0

      if t == 0: 
        logNormalPDF = 0.0
      else:
        logNormalPDF = 1.0/t/sigma/math.sqrt(2.0*math.pi) * \
                       math.exp( - (math.log(t) - mean)**2 / 2/ sigma**2 )

      if key == 'Xe':
        variability = 1.0 - random.random() * 0.15
        self.__historyXeMassVapor[ facilityTime + timeStep ] = mass * logNormalPDF * variability

      if key == 'Kr':
        variability = 1.0 - random.random() * 0.15
        self.__historyKrMassVapor[ facilityTime + timeStep ] = mass * logNormalPDF * variability

      if key == 'I2':
        massSplit = 0.85
        mass *= massSplit
#        variability = 1.0 - random.random() * 0.10
        variability = 1.0 
        self.__historyI2MassVapor[ facilityTime + timeStep ] = mass * logNormalPDF * variability
#        print(' self.__historyI2MassVapor = ', self.__historyI2MassVapor)
#        print(' self.__historyI2MassLiquid = ', self.__historyI2MassLiquid)
        self.__historyI2MassLiquid[ facilityTime + timeStep ] = \
             self.__historyI2MassLiquid[ facilityTime ] + \
             self.__historyI2MassVapor[ facilityTime + timeStep ] * (1.0-massSplit) * timeStep

      if key == 'RuO4':
        variability = 1.0 - random.random() * 0.15
        self.__historyRuO4MassVapor[ facilityTime + timeStep ] = mass * logNormalPDF * variability

      if key == 'CO2':
        variability = 1.0 - random.random() * 0.15
        self.__historyCO2MassVapor[ facilityTime + timeStep ] = mass * logNormalPDF * variability

  else:

    self.__historyXeMassVapor[ facilityTime + timeStep ] = 0.0
    self.__historyKrMassVapor[ facilityTime + timeStep ] = 0.0
    self.__historyI2MassVapor[ facilityTime + timeStep ] = 0.0
    self.__historyI2MassLiquid[ facilityTime + timeStep ] = 0.0
    self.__historyRuO4MassVapor[ facilityTime + timeStep ] = 0.0
    self.__historyCO2MassVapor[ facilityTime + timeStep ] = 0.0

#---------------------------------------------------------------------------------
 def __GetFuelLoadMass( self ):

  mass = 0.0
  massUnit = 'null'

  if self.__fuelSegmentsLoad is None: return None

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

  if self.__fuelSegmentsLoad is None: return None

  segmentsGeoData = self.__fuelSegmentsLoad[0]

  for segmentData in segmentsGeoData:
    for (name,unit,value) in segmentData:
      if name=='length': 
        length = value
        lengthUnit = unit
      if name=='innerDiameter': 
        iD = value
        iDUnit = unit
    volume += length * math.pi * iD * iD / 4.0

  if lengthUnit=='mm' and iDUnit=='mm': 
     volumeUnit = 'cc'
     volume /= 1000.0
  else:
     assert True, 'invalid unit'

  return (volume,volumeUnit)

#---------------------------------------------------------------------------------
# "Derive" species from elemental composition from fuel load
# vfda: will be changed
 def __GetFuelLoadSpecies( self ):

  species = dict()

  if self.__fuelSegmentsLoad is None: return
 
  massI  = 0.0
  massKr = 0.0
  massXe = 0.0
  mass3H = 0.0
  massRu = 0.0
  massC  = 0.0

  segmentsCompData = self.__fuelSegmentsLoad[1]

  for segmentData in segmentsCompData:

    for (name,unit,value) in segmentData:
      if name=='I': 
         massI    += value
         massIUnit = unit
         species['I2'] = ( massI/2.0, massIUnit )
      if name=='Kr': 
         massKr    += value
         massKrUnit = unit
         species['Kr'] = ( massKr, massKrUnit )
      if name=='Xe': 
         massXe    += value
         massXeUnit = unit
         species['Xe'] = ( massXe, massXeUnit )
      if name=='Ru': 
         massRu    += value
         massRuUnit = unit
         species['RuO4'] = ( massRu + massRu/101.07*4.0*16.0, massRuUnit )
      if name=='C': 
         massC    += value
         massCUnit = unit
         species['CO2'] = ( massC + massC/14.0*2.0*16.0, massCUnit )

  return species

#---------------------------------------------------------------------------------
 def __GetCondensate( self, portFile, facilityTime ):

  found = False

  while found is False:

    s = '__GetCondensate(): checking for condensate at '+str(facilityTime)
    self.__log.debug(s)

    try:
      tree = ElementTree.parse( portFile )
    except ElementTree.ParseError as error:
      s = '__GetCondensate(): '+portFile+' unavailable. Error code: '+str(error.code)+' File position: '+str(error.position)+'. Retrying...'
      self.__log.debug(s)
      continue

    rootNode = tree.getroot()
    assert rootNode.tag == 'time-sequence', 'invalid format.' 

    timeNode = rootNode.find('time')
    timeUnit = timeNode.get('unit').strip()
    assert timeUnit == "minute"

    varNodes = rootNode.findall('var')
    varNames = list()
    for v in varNodes:
      name = v.get('name').strip()
#      assert v.get('name').strip() == 'I2 Condensate', 'invalid variable.'
      assert v.get('unit').strip() == 'gram/min', 'invalid mass unit'
      varNames.append(name)

    timeStampNodes = rootNode.findall('timeStamp')

    for tsn in timeStampNodes:

      timeStamp = float(tsn.get('value').strip())
 
      # get data at timeStamp facilityTime
      if timeStamp == facilityTime:

         found = True

         varValues = tsn.text.strip().split(',')
         assert len(varValues) == len(varNodes), 'inconsistent data; stop.'

         for varName in varNames:
           if varName == 'I2 Condensate':
              ivar = varNames.index(varName)
              mass = float(varValues[ivar])
 #             if facilityTime in self.__historyI2MassLiquid.keys():
              self.__historyI2MassLiquid[ facilityTime ] += mass
 #             else:
 #                self.__historyI2MassLiquid[ facilityTime ] = mass

              s = '__GetCondensate(): received condensate at '+str(facilityTime)+' [min]; I2 mass [g] = '+str(round(mass,3))
              self.__log.debug(s)
           # end of: if varName == 'I2 Condensate':
           if varName == 'Xe Condensate':
              ivar = varNames.index(varName)
              mass = float(varValues[ivar])
 #             if facilityTime in self.__historyI2MassLiquid.keys():
              self.__historyXeMassVapor[ facilityTime ] += mass
 #             else:
 #                self.__historyXeMassLiquid[ facilityTime ] = mass

              s = '__GetCondensate(): received condensate at '+str(facilityTime)+' [min]; Xe mass [g] = '+str(round(mass,3))
              self.__log.debug(s)
           # end of: if varName == 'Xe Condensate':

    # end for n in nodes:

    if found is False: time.sleep(1) 

  # end of while found is False:

  return 

#*********************************************************************************
# Usage: -> python dissolver.py
if __name__ == "__main__":
 print('Unit testing for Dissolver')
