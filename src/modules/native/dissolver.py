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

  self.__roughnessF = 0.8

  self.__rho_uo2       =  8.300  # g/cc
  self.__rho_puo2      = 11.460
  self.__rho_fpo1dot18 = 12.100

  self.__gramDecimals = 6 # microgram significant digits
  self.__mmDecimals   = 3 # micrometer significant digits
  self.__ccDecimals   = 3 # cubic centimeter significant digits
  self.__pyplotScale = 'log-linear' # linear, linear-linear, log, log-log, linear-log, log-linear

  # Core dissolver module
  self.__nitron = Nitron()

  self.__HNO3molarity = 9  # Molar

  # Member data 
  self.__ports = ports

  self.__ready2LoadFuel    = True   # major control variable
  self.__startDissolveTime = -1.0   # major control variable

  self.__fuelSegments = None # major data: dissolving solids  (time-dependent)
  self.__fuelMass     = None # major control variable (time-dependent)
  self.__fuelVolume   = None # major control variable (time-dependent)

#  self.__stateHistory = list(dict())

  self.__historyXeMassVapor   = dict()  # persistent variable
  self.__historyXeMassVapor[0.0] = 0.0 

  self.__historyKrMassVapor   = dict()  # persistent variable
  self.__historyI2MassVapor   = dict()  # persistent variable
  self.__historyHTOMassVapor  = dict()  # persistent variable
  self.__historyRuO4MassVapor = dict()  # persistent variable
  self.__historyCO2MassVapor  = dict()  # persistent variable

  self.__historyI2MassLiquid = dict()  # persistent variable
  self.__historyI2MassLiquid[0.0] = 0.0

  self.__historyHTOMassLiquid = dict()  # persistent variable
  self.__historyHTOMassLiquid[0.0] = 0.0

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
        self.__fuelSegments = self.__GetSolids( portFile, atTime )

     if self.__fuelSegments is not None: 
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
    b.set('scale','linear')

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
# Reads the solids (in the form of fuel segments) from an existing history file
 def __GetSolids( self, portFile, facilityTime ):

  fuelSegments = None

  found = False

  while found is False:

    try:
      tree = ElementTree.parse( portFile )
    except ElementTree.ParseError as error:
      s = '__GetSolids(): '+portFile+' unavailable. Error code: '+str(error.code)+' File position: '+str(error.position)+'. Retrying...'
      self.__log.debug(s)
      continue

    rootNode = tree.getroot()

    assert rootNode.tag == 'time-variable-packet', 'invalid cortix file format; stop.'

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

          #............................................
          # read the header information into Spec lists
          #............................................

          timeElem = rootNode.find('time')
          timeStampUnit = timeElem.get('unit').strip()
          assert timeStampUnit == "minute"

          # pack1
          pack1Spec = rootNode.findall('pack1')
          assert len(pack1Spec) == 1, 'sanity check failed.'
          pack1Spec = rootNode.find('pack1')
 
          pack1Name = pack1Spec.get('name').strip()
          assert pack1Name == 'Geometry'

          # [(name,unit),(name,unit),...]
          segmentGeometrySpec = list()

          for var in pack1Spec:
            attributes = var.items()
            assert len(attributes) == 2
            for attribute in attributes:
              if   attribute[0] == 'name': name = attribute[1]
              elif attribute[0] == 'unit': unit = attribute[1]
              else: assert True
            segmentGeometrySpec.append( (name, unit) )

          # pack2
          pack2Spec = rootNode.findall('pack2')
          assert len(pack2Spec) == 1, 'sanity check failed.'
          pack2Spec = rootNode.find('pack2')
 
          pack2Name = pack2Spec.get('name').strip()
          assert pack2Name == 'Composition'

          # [(name,unit),(name,unit),...]
          segmentCompositionSpec = list()

          for var in pack2Spec:
            attributes = var.items()
            assert len(attributes) == 2
            for attribute in attributes:
              if   attribute[0] == 'name': name = attribute[1]
              elif attribute[0] == 'unit': unit = attribute[1]
              else: assert True
            segmentCompositionSpec.append( (name,unit) )

          #........................................
          # read the timeStamp data into Data lists
          #........................................

          # geometry data: list of a list of triples
          # first level: one entry for each fuel segment
          # second level: one entry (triple) for each geometry field
          # [ [(name,unit,val), (name,unit,val),...], [(name,unit,val),..], ... ]
          segmentsGeometryData = list()

          for pack in pack1: # each pack is a fuel segment
            packData = pack.text.strip().split(',')
            assert len(packData) == len(segmentGeometrySpec)
            for i in range(len(packData)): packData[i] = float(packData[i])
            segGeomData = list()
            for ((name,unit),val) in zip(segmentGeometrySpec,packData):
              segGeomData.append( (name,unit,val) )
            segmentsGeometryData.append( segGeomData )

          # composition data: list of a list of triples
          # first level: one entry for each fuel segment
          # second level: one entry (triple) for each elemental specie field
          # [ [(name,unit,val), (name,unit,val),...], [(name,unit,val),..], ... ]
          segmentsCompositionData = list()

          for pack in pack2: # each pack is a segment
            packData = pack.text.strip().split(',')
            assert len(packData) == len(segmentCompositionSpec)
            for i in range(len(packData)): packData[i] = float(packData[i])
            segCompData = list()
            for ((name,unit),val) in zip(segmentCompositionSpec,packData):
              segCompData.append( (name,unit,val) )
            segmentsCompositionData.append( segCompData )

          assert len(segmentsGeometryData) == len(segmentsCompositionData)

          fuelSegments = (segmentsGeometryData, segmentsCompositionData) 

        # end of: if len(pack1) != 0 or len(pack2) != 0:

      # end of: if timeStamp == facilityTime:

    # end of: for n in nodes:

    if found is False: 
      time.sleep(1)
      s = '__GetSolids(): did not find time stamp '+str(facilityTime)+' [min] in '+portFile
      self.__log.debug(s)

  # end of: while found is False:

  if fuelSegments is None: nSegments = 0
  else:                        nSegments = len(fuelSegments[0])

  s = '__GetSolids(): got fuel load at '+str(facilityTime)+' [min], with '+str(nSegments)+' segments'
  self.__log.debug(s)

  return  fuelSegments

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
    b.set('scale',self.__pyplotScale)

    # second variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Kr Vapor')
    b.set('unit','gram/min')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.__pyplotScale)

    # third variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','I2 Vapor')
    b.set('unit','gram/min')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.__pyplotScale)

    # fourth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','RuO4 Vapor')
    b.set('unit','gram/min')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.__pyplotScale)

    # fifth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','CO2 Vapor')
    b.set('unit','gram/min')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.__pyplotScale)

    # sixth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','HTO Vapor')
    b.set('unit','gram/min')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.__pyplotScale)

    # values for all variables
    b = ElementTree.SubElement(a,'timeStamp')
    b.set('value',str(atTime))
    b.text = str('0.0') + ',' + \
             str('0.0') + ',' + \
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

    if len(self.__historyHTOMassVapor.keys()) > 0:
      massHTO = round(self.__historyHTOMassVapor[atTime],gDec)
    else:
      massHTO = 0.0

    a.text = str(massXe)   +','+ \
             str(massKr)   +','+ \
             str(massI2)   +','+ \
             str(massRuO4) +','+ \
             str(massCO2)  +','+ \
             str(massHTO)

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
    if self.__GetFuelMass() is not None:
      (massFuelLoad,unit) = self.__GetFuelMass()
    else:
      massFuelLoad = 0.0
    unit = 'gram'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',self.__pyplotScale)

    # second variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Fuel Loaded')
    if self.__GetFuelVolume() is not None:
      (volumeFuelLoad,unit) = self.__GetFuelVolume()
    else:
      volumeFuelLoad = 0.0
    unit = 'cc'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',self.__pyplotScale)

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
    b.set('scale',self.__pyplotScale)

    # fourth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','HTO Liquid')
    if len(self.__historyHTOMassLiquid.keys()) > 0:
      massHTOLiquid = self.__historyHTOMassLiquid[ atTime ]
    else:
      massHTOLiquid = 0.0
    unit = 'gram'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',self.__pyplotScale)

    # values for all variables
    b = ElementTree.SubElement(a,'timeStamp')
    b.set('value',str(atTime))
    massFuelLoad   = round(massFuelLoad,gDec)
    volumeFuelLoad = round(volumeFuelLoad,ccDec)
    massI2Liquid   = round(massI2Liquid,gDec)
    massHTOLiquid   = round(massHTOLiquid,gDec)
    b.text = str(massFuelLoad)+','+\
             str(volumeFuelLoad)+','+\
             str(massI2Liquid)+','+\
             str(massHTOLiquid)

    tree = ElementTree.ElementTree(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  # if not the first time step then parse the existing history file and append
  else:

    tree = ElementTree.parse( portFile )
    rootNode = tree.getroot()
    a = ElementTree.Element('timeStamp')
    a.set('value',str(atTime))

    # all variables
    if self.__GetFuelMass() is not None:
      (massFuelLoad,unit) = self.__GetFuelMass()
      (volumeFuelLoad,unit) = self.__GetFuelVolume()
    else:
      massFuelLoad = 0.0
      volumeFuelLoad = 0.0

    if len(self.__historyI2MassLiquid.keys()) > 0:
      massI2Liquid = self.__historyI2MassLiquid[ atTime ]
    else:
      massI2Liquid = 0.0

    if len(self.__historyHTOMassLiquid.keys()) > 0:
      massHTOLiquid = self.__historyHTOMassLiquid[ atTime ]
    else:
      massHTOLiquid = 0.0

    a.text = str(round(massFuelLoad,gDec))+','+\
             str(round(volumeFuelLoad,ccDec))+','+\
             str(round(massI2Liquid,gDec))+','+\
             str(round(massHTOLiquid,gDec))

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
    self.__fuelMass = (mass,unit) = self.__GetFuelMass()
    s = '__Dissolve(): loaded mass ' + str(round(mass,3)) + ' [' + unit + ']'
    self.__log.info(s)
    self.__fuelVolume = (volume,unit) = self.__GetFuelVolume()
    s = '__Dissolve(): loaded volume ' + str(round(volume,3)) + ' [' + unit + ']'
    self.__log.info(s)
    nSegments = len(self.__fuelSegments[0])
    s = '__Dissolve(): new fuel load # segments = ' + str(nSegments)
    self.__log.info(s)

    self.__loadedSpecies = self.__GetFuelLoadSpecies()

    self.__fuelSegments = None # clear the load

    # set initial concentrations in the liquid phase to zero
    self.__historyI2MassLiquid[ facilityTime ] = 0.0
    self.__historyHTOMassLiquid[ facilityTime ] = 0.0

    s = '__Dissolve(): begin dissolving...' 
    self.__log.info(s)

    #................................................
    self.__UpdateStateVariables( facilityTime, timeStep )
    #................................................

  #.....................
  # continue dissolving
  #.....................
  elif facilityTime > self.__startDissolveTime and self.__fuelMass is not None:

    s = '__Dissolve(): continue dissolving...' 
    self.__log.info(s)

    #................................................
    self.__UpdateStateVariables( facilityTime, timeStep )
    #................................................
  
    if  facilityTime + timeStep >= self.__startDissolveTime + self.__dutyPeriod: # prepare for a new load in the next time step

      s = '__Dissolve(): signal new duty cycle for ' + str(facilityTime+timeStep)+' [min]'
      self.__log.info(s)

      self.__ready2LoadFuel = True
      self.__fuelMass       = None
      self.__fuelVolume     = None
      self.__loadedSpecies  = None

  #.............................
  # do nothing in this time step
  #.............................
  else: 

    s = '__Dissolve(): idle and ready ' + str(facilityTime)+' [min]'
    self.__log.info(s)

    # set initial concentrations in the liquid phase to zero
    self.__historyI2MassLiquid[ facilityTime ] = 0.0
    self.__historyHTOMassLiquid[ facilityTime ] = 0.0

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

      if key == 'HTO':
        massSplit = 0.50
        mass *= massSplit
        variability = 1.0 
        self.__historyHTOMassVapor[ facilityTime + timeStep ] = mass * logNormalPDF * variability
        self.__historyHTOMassLiquid[ facilityTime + timeStep ] = \
             self.__historyHTOMassLiquid[ facilityTime ] + \
             self.__historyHTOMassVapor[ facilityTime + timeStep ] * (1.0-massSplit) * timeStep

      if key == 'RuO4':
        variability = 1.0 - random.random() * 0.15
        self.__historyRuO4MassVapor[ facilityTime + timeStep ] = mass * logNormalPDF * variability

      if key == 'CO2':
        variability = 1.0 - random.random() * 0.15
        self.__historyCO2MassVapor[ facilityTime + timeStep ] = mass * logNormalPDF * variability

  else:

    self.__historyXeMassVapor[ facilityTime + timeStep ]   = 0.0
    self.__historyKrMassVapor[ facilityTime + timeStep ]   = 0.0
    self.__historyI2MassVapor[ facilityTime + timeStep ]   = 0.0
    self.__historyHTOMassVapor[ facilityTime + timeStep ]   = 0.0
    self.__historyI2MassLiquid[ facilityTime + timeStep ]  = 0.0
    self.__historyHTOMassLiquid[ facilityTime + timeStep ]  = 0.0
    self.__historyRuO4MassVapor[ facilityTime + timeStep ] = 0.0
    self.__historyCO2MassVapor[ facilityTime + timeStep ]  = 0.0

#  if self.__fuelSegments is not None:
#
#    self.__LeachFuel( timeStep )

#---------------------------------------------------------------------------------
 def __GetFuelMass( self ):

  mass = 0.0
  massUnit = 'null'

  if self.__fuelSegments is None: return None

  segmentsGeoData = self.__fuelSegments[0]
  for segmentData in segmentsGeoData:
    for (name,unit,value) in segmentData:
      if name=='mass': 
        mass += value
        massUnit = unit

  return (mass,massUnit)

#---------------------------------------------------------------------------------
 def __GetFuelVolume( self ):

  volume = 0.0
  volumeUnit = 'null'

  if self.__fuelSegments is None: return None

  segmentsGeoData = self.__fuelSegments[0]

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
# vfda: this will be changed
# Call this only one time!!!
 def __GetFuelLoadSpecies( self ):

  species = dict()

  if self.__fuelSegments is None: return
 
  massI2   = 0.0
  massKr   = 0.0
  massXe   = 0.0
  massHTO  = 0.0
  massRuO4 = 0.0
  massCO2  = 0.0

  segmentsCompData = self.__fuelSegments[1]

  for segmentData in segmentsCompData:

    for (name,unit,value) in segmentData:
      if name=='I': 
         massI2    += value/2.0
         massI2Unit = unit
      if name=='Kr': 
         massKr    += value
         massKrUnit = unit
      if name=='Xe': 
         massXe    += value
         massXeUnit = unit
      if name=='Ru': 
         massRuO4   += value + value/101.07*4.0*16.0
         massRuO4Unit = unit
      if name=='C': 
         massCO2    += value + value/14.0*2.0*16.0
         massCO2Unit = unit
      if name=='3H': 
         massHTO   += value + value/3.0*1.0*(16.0+1.0)
         massHTOUnit = unit
    # end of: for (name,unit,value) in segmentData:

  # end of: for segmentData in segmentsCompData:

  species['I2'] = ( massI2, massI2Unit )
  species['Kr'] = ( massKr, massKrUnit )
  species['Xe'] = ( massXe, massXeUnit )
  species['RuO4'] = ( massRuO4, massRuO4Unit )
  species['CO2'] = ( massCO2, massCO2Unit )
  species['HTO'] = ( massHTO, massHTOUnit )

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

#---------------------------------------------------------------------------------
 def __LeachFuel( self, timeStep ):

  if self.__fuelSegments is None: return 

  molarityHNO3 = self.__HNO3molarity

  uMolarMass  = self.__molarMassU
  puMolarMass = self.__molarMassPu
  fpMolarMass = self.__molarMassFP
 
  uo2MolarMass       = self.__molarMassUO2
  puo2MolarMass      = self.__molarMassPuO2
  fpo1dot18MolarMass = self.__molarMassFPO1dot18

  rhoUO2       = self.__rho_uo2
  rhoPuO2      = self.__rho_puo2
  rhoFPO1dot18 = self.__rho_fpo1dot18

  segmentsGeoData  = self.__fuelSegments[0]
  segmentsCompData = self.__fuelSegments[1]

  for (segData,segCompData) in zip(segmentsGeoData,segmentsCompData):

    for (name,unit,value) in segData:
      if name=='mass': 
        mass = value
      if name=='massDensity': 
        dens = value
      if name=='innerDiameter': 
        iD = value
      if name=='length': 
        length = value

    segDissolArea = 2.0 * math.pi * iD * iD / 4.0

    for (name,unit,value) in segComp:
      if name=='U':
         uMass = value
      if name=='Pu':
         puMass = value
      if name=='FP':
         fpMass = value

    mUO2       = uMass  + uMass/uMolarMass*2.0*16.0
    mPuO2      = puMass + puMass/puMolarMass*2.0*16.0
    mFPO1dot18 = fpMass + fpMass/fpMolarMass*1.18*16.0

    molesUO2       = mUO2/uo2MolarMass
    molesPuO2      = mPuO2/puo2MolarMass
    molesFPO1dot18 = mFPO1dot18/fpo1dot18MolarMass

    molesTotal = molesUO2 + molesPuO2 + molesFPO1dot18
  
    xUO2 = molesUO2/molesTotal
    xPuO2 = molesPuO2/molesTotal
    xFPO1dot18 = molesFPO1dot18/molesTotal

    mReactOrder = 2*(2-xUO2)

    rhoPrime = 100.0 * dens / ( xUO2 * rhoUO2 + xPuO2 * rhoPuO2 + xFPO1dot18 * rhoFPO1dot18)

    rateCte = ( 0.48 * math.exp(-0.091*rhoPrime) )**(xUO2) * \
              ( 5.0 * math.exp(-0.27*rhoPrime) )**(1-xUO2)

    dissolMassRate = - rateCte * molarityHNO3**mReactOrder * roughnessF * segArea

    print('*********** segment ***********')
    print('timeStep min = ', timeStep)
    print('dissolMassRate g/s = ', dissolMassRate)
    print('rateCte = ', rateCte)
    print('molarityHNO3 M = ', molarityHNO3)
    print('mReactOrder = ', mReactOrder)
    print('rhoPrime g/cc = ', rhoPrime)
    print('dens  g/cc= ', dens)
      

#*********************************************************************************
# Usage: -> python dissolver.py
if __name__ == "__main__":
 print('Unit testing for Dissolver')
