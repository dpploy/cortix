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
import numpy as np
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
  self.__solidsMassLoadMax     = 670.0 # gram
  self.__dissolverVolume       = 4.0  # liter
  self.__dutyPeriod            = 120.0 # minute

  self.__molarMassU            = 238.0
  self.__molarMassPu           = 239.0
  self.__molarMassFP           = 135.34-16*1.18
  self.__molarMassH2O          = 18.0    # g/mole
  self.__molarMassHNO3         = 63.0    # g/mole
  self.__molarMassNO           = 30.01   # g/mole
  self.__molarMassNO2          = 46.0055 # g/mole
  self.__molarMassUO2          = 270.05
  self.__molarMassPuO2         = 271.17
  self.__molarMassFPO1dot18    = 135.34
  self.__molarMassUO2NO3_2     = self.__molarMassUO2 + 62.0*2.0 # g/mole
  self.__molarMassPuNO3_4      = self.__molarMassPu  + 62.0*4.0 # g/mole
  self.__molarMassFPNO3_2dot36 = 328.22

  self.__roughnessF = 4.0

  self.__rho_uo2       =  8.300  # g/cc
  self.__rho_puo2      = 11.460
  self.__rho_fpo1dot18 = 12.100

  self.__gramDecimals = 7 # tenth of a microgram significant digits
  self.__mmDecimals   = 3 # micrometer significant digits
  self.__ccDecimals   = 3 # cubic centimeter significant digits
  self.__pyplotScale = 'linear' # linear, linear-linear, log, log-log, linear-log, log-linear

  self.__startingHNO3Molarity = 10 # Molar

  # Member data 
  self.__ports = ports

  self.__ready2LoadFuel    = True   # major control variable
  self.__dissolutionStartedTime = -1.0   # major control variable

  self.__fuelSegments = None # major data: dissolving solids  (time-dependent)

#  self.__stateHistory = list(dict())

  self.__historyXeMassVapor   = dict()  # persistent variable
  self.__historyXeMassVapor[0.0] = 0.0 

  self.__historyKrMassVapor   = dict()  # persistent variable
  self.__historyKrMassVapor[0.0] = 0.0

  self.__historyI2MassVapor   = dict()  # persistent variable
  self.__historyHTOMassVapor  = dict()  # persistent variable
  self.__historyRuO4MassVapor = dict()  # persistent variable
  self.__historyCO2MassVapor  = dict()  # persistent variable

  self.__historyI2MassLiquid = dict()  # persistent variable
  self.__historyI2MassLiquid[0.0] = 0.0

  self.__historyHTOMassLiquid = dict()  # persistent variable
  self.__historyHTOMassLiquid[0.0] = 0.0

  self.__historyHNO3MolarLiquid = dict()  # persistent variable
  self.__historyHNO3MolarLiquid[0.0] = self.__startingHNO3Molarity 

  self.__historyH2OMassLiquid = dict()  # persistent variable
  self.__historyH2OMassLiquid[0.0] = 1000.0 * self.__dissolverVolume - self.__startingHNO3Molarity * self.__molarMassHNO3 * self.__dissolverVolume

  self.__historyUNMassConcLiquid = dict()  # persistent variable
  self.__historyUNMassConcLiquid[0.0] = 0.0

  self.__historyPuNMassConcLiquid = dict()  # persistent variable
  self.__historyPuNMassConcLiquid[0.0] = 0.0

  self.__historyFPNMassConcLiquid = dict()  # persistent variable
  self.__historyFPNMassConcLiquid[0.0] = 0.0

  self.__historyNOMassVapor   = dict()  # persistent variable
  self.__historyNOMassVapor[0.0] = 0.0 

  self.__historyNO2MassVapor   = dict()  # persistent variable
  self.__historyNO2MassVapor[0.0] = 0.0 

  self.__volatileSpecies0 = None 

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
        tmp = self.__GetSolids( portFile, atTime )
        if tmp is not None:  # if fuel load was successful
          self.__fuelSegments = tmp
          self.__ready2LoadFuel         = False
          self.__dissolutionStartedTime = atTime

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

          if self.__dissolutionStartedTime >= 0.0:
             assert facilityTime >= self.__dissolutionStartedTime + self.__dutyPeriod, 'sanity check failed.'

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
  else:                    nSegments = len(fuelSegments[0])

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
    b.set('unit','gram')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.__pyplotScale)

    # second variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Kr Vapor')
    b.set('unit','gram')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.__pyplotScale)

    # third variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','I2 Vapor')
    b.set('unit','gram')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.__pyplotScale)

    # fourth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','RuO4 Vapor')
    b.set('unit','gram')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.__pyplotScale)

    # fifth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','CO2 Vapor')
    b.set('unit','gram')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.__pyplotScale)

    # sixth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','HTO Vapor')
    b.set('unit','gram')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.__pyplotScale)

    # seventh variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','NO Vapor')
    b.set('unit','gram')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.__pyplotScale)

    # eight variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','NO2 Vapor')
    b.set('unit','gram')
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

    if len(self.__historyNOMassVapor.keys()) > 0:
      massNO = round(self.__historyNOMassVapor[atTime],gDec)
    else:
      massNO = 0.0

    if len(self.__historyNO2MassVapor.keys()) > 0:
      massNO2 = round(self.__historyNO2MassVapor[atTime],gDec)
    else:
      massNO2 = 0.0

    a.text = str(massXe)   +','+ \
             str(massKr)   +','+ \
             str(massI2)   +','+ \
             str(massRuO4) +','+ \
             str(massCO2)  +','+ \
             str(massHTO)  +','+ \
             str(massNO)   +','+ \
             str(massNO2)

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#---------------------------------------------------------------------------------
 def __ProvideState( self, portFile, atTime ):
 
  gDec  = self.__gramDecimals
  ccDec = self.__ccDecimals   
 
  pyplotScale = 'linear'

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
    b.set('name','Fuel')
    tmp = self.__GetFuelMass()
    if tmp is not None:
      (fuelMass,unit) = tmp
    else:
      fuelMass = 0.0
      unit = 'gram'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',pyplotScale)

    # second variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Fuel')
    tmp = self.__GetFuelVolume()
    if tmp is not None:
      (fuelVolume,unit) = tmp
    else:
      fuelVolume = 0.0
      unit = 'cc'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',pyplotScale)

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
    b.set('scale',pyplotScale)

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
    b.set('scale',pyplotScale)

    # fifth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','HNO3 Liquid')
    if len(self.__historyHNO3MolarLiquid.keys()) > 0:
      molarHNO3Liquid = self.__historyHNO3MolarLiquid[ atTime ]
    else:
      molarHNO3Liquid = 0.0
    unit = 'M'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',pyplotScale)

    # sixth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','UO2(NO3)2 Liquid')
    if len(self.__historyUNMassConcLiquid.keys()) > 0:
      massConcUNLiquid = self.__historyUNMassConcLiquid[ atTime ]
    else:
      massConcUNLiquid = 0.0
    unit = 'g/L'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',pyplotScale)

    # seventh variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Pu(NO3)4 Liquid')
    if len(self.__historyPuNMassConcLiquid.keys()) > 0:
      massConcPuNLiquid = self.__historyPuNMassConcLiquid[ atTime ]
    else:
      massConcPuNLiquid = 0.0
    unit = 'g/L'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',pyplotScale)

    # eighth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','FP(NO3)2.36 Liquid')
    if len(self.__historyFPNMassConcLiquid.keys()) > 0:
      massConcFPNLiquid = self.__historyFPNMassConcLiquid[ atTime ]
    else:
      massConcFPNLiquid = 0.0
    unit = 'g/L'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',pyplotScale)

    # values for all variables
    b = ElementTree.SubElement(a,'timeStamp')
    b.set('value',str(atTime))
    fuelMass   = round(fuelMass,gDec)
    fuelVolume = round(fuelVolume,ccDec)
    massI2Liquid  = round(massI2Liquid,gDec)
    massHTOLiquid = round(massHTOLiquid,gDec)
    b.text = str(fuelMass)+','+\
             str(fuelVolume)+','+\
             str(massI2Liquid)+','+\
             str(massHTOLiquid)+','+\
             str(molarHNO3Liquid)+','+\
             str(massConcUNLiquid)+','+\
             str(massConcPuNLiquid)+','+\
             str(massConcFPNLiquid)

    tree = ElementTree.ElementTree(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  # if not the first time step then parse the existing history file and append
  else:

    tree = ElementTree.parse( portFile )
    rootNode = tree.getroot()
    a = ElementTree.Element('timeStamp')
    a.set('value',str(atTime))

    # all variables
    tmp = self.__GetFuelMass()
    if tmp is not None:
       (fuelMass,unit) = tmp
    else:
      fuelMass = 0.0

    tmp = self.__GetFuelVolume()
    if tmp is not None:
       (fuelVolume,unit) = tmp
    else:
      fuelVolume = 0.0

    if len(self.__historyI2MassLiquid.keys()) > 0:
      massI2Liquid = self.__historyI2MassLiquid[ atTime ]
    else:
      massI2Liquid = 0.0

    if len(self.__historyHTOMassLiquid.keys()) > 0:
      massHTOLiquid = self.__historyHTOMassLiquid[ atTime ]
    else:
      massHTOLiquid = 0.0

    if len(self.__historyHNO3MolarLiquid.keys()) > 0:
      molarHNO3Liquid = self.__historyHNO3MolarLiquid[ atTime ]
    else:
      molarHNO3Liquid = 0.0

    if len(self.__historyUNMassConcLiquid.keys()) > 0:
      massConcUNLiquid = self.__historyUNMassConcLiquid[ atTime ]
    else:
      massConcUNLiquid = 0.0

    if len(self.__historyPuNMassConcLiquid.keys()) > 0:
      massConcPuNLiquid = self.__historyPuNMassConcLiquid[ atTime ]
    else:
      massConcPuNLiquid = 0.0

    if len(self.__historyFPNMassConcLiquid.keys()) > 0:
      massConcFPNLiquid = self.__historyFPNMassConcLiquid[ atTime ]
    else:
      massConcFPNLiquid = 0.0

    if len(self.__historyNOMassVapor.keys()) > 0:
      massNOVapor = self.__historyNOMassVapor[ atTime ]
    else:
      massNOVapor = 0.0

    if len(self.__historyNO2MassVapor.keys()) > 0:
      massNO2Vapor = self.__historyNO2MassVapor[ atTime ]
    else:
      massNO2Vapor = 0.0

    a.text = str(round(fuelMass,3))+','+\
             str(round(fuelVolume,ccDec))+','+\
             str(round(massI2Liquid,gDec))+','+\
             str(round(massHTOLiquid,gDec))+','+\
             str(round(molarHNO3Liquid,3))+','+\
             str(round(massConcUNLiquid,3))+','+\
             str(round(massConcPuNLiquid,3))+','+\
             str(round(massConcFPNLiquid,3))

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#---------------------------------------------------------------------------------
 def __Dissolve( self, facilityTime, timeStep ):

  #..........
  # new start
  #..........
  if facilityTime == self.__dissolutionStartedTime: # this is the beginning of a duty cycle

    s = '__Dissolve(): starting new duty cycle at ' + str(facilityTime) + ' [min]'
    self.__log.info(s)
    (mass,unit) = self.__GetFuelMass()
    s = '__Dissolve(): loaded mass ' + str(round(mass,3)) + ' [' + unit + ']'
    self.__log.info(s)
    (volume,unit) = self.__GetFuelVolume()
    s = '__Dissolve(): loaded volume ' + str(round(volume,3)) + ' [' + unit + ']'
    self.__log.info(s)
    nSegments = len(self.__fuelSegments[0])
    s = '__Dissolve(): new fuel load # segments = ' + str(nSegments)
    self.__log.info(s)

    self.__volatileSpecies0 = self.__GetVolatileSpecies()

    # set initial concentrations in the liquid phase to zero
    self.__historyHNO3MolarLiquid[ facilityTime ] = self.__startingHNO3Molarity
    self.__historyH2OMassLiquid[ facilityTime ] = 1000.0 * self.__dissolverVolume - self.__startingHNO3Molarity * self.__molarMassHNO3 * self.__dissolverVolume
    self.__historyUNMassConcLiquid[ facilityTime ] = 0.0
    self.__historyPuNMassConcLiquid[ facilityTime ] = 0.0
    self.__historyFPNMassConcLiquid[ facilityTime ] = 0.0
    self.__historyI2MassLiquid[ facilityTime ] = 0.0
    self.__historyHTOMassLiquid[ facilityTime ] = 0.0

    self.__historyNOMassVapor[ facilityTime ] = 0.0
    self.__historyNO2MassVapor[ facilityTime ] = 0.0

    s = '__Dissolve(): begin dissolving...' 
    self.__log.info(s)

    #................................................
    self.__UpdateStateVariables( facilityTime, timeStep )
    #................................................

  #.....................
  # continue dissolving
  #.....................
  elif facilityTime > self.__dissolutionStartedTime and self.__GetFuelMass() is not None:

    s = '__Dissolve(): continue dissolving...' 
    self.__log.info(s)

    #................................................
    self.__UpdateStateVariables( facilityTime, timeStep )
    #................................................

    (mass,unit) = self.__GetFuelMass()
    s = '__Dissolve(): solid mass ' + str(round(mass,3)) + ' [' + unit + ']'
    self.__log.info(s)
  
    if  facilityTime + timeStep >= self.__dissolutionStartedTime + self.__dutyPeriod: # prepare for a new load in the next time step

      s = '__Dissolve(): signal new duty cycle for ' + str(facilityTime+timeStep)+' [min]'
      self.__log.info(s)

      self.__ready2LoadFuel = True

      # send everything to accumulationTank...to be done...
      # for now clear the data
      self.__volatileSpecies0 = None
      self.__fuelSegments    = None 

  #.............................
  # do nothing in this time step
  #.............................
  else: 

    s = '__Dissolve(): idle and ready ' + str(facilityTime)+' [min]'
    self.__log.info(s)

    # set initial concentrations in the liquid phase to zero
    self.__historyI2MassLiquid[ facilityTime ] = 0.0
    self.__historyHTOMassLiquid[ facilityTime ] = 0.0
    self.__historyHNO3MolarLiquid[ facilityTime ] = self.__startingHNO3Molarity 
    self.__historyH2OMassLiquid[facilityTime] = 1000.0 * self.__dissolverVolume - self.__startingHNO3Molarity * self.__molarMassHNO3 * self.__dissolverVolume
    self.__historyUNMassConcLiquid[ facilityTime ] = 0.0
    self.__historyPuNMassConcLiquid[ facilityTime ] = 0.0
    self.__historyFPNMassConcLiquid[ facilityTime ] = 0.0

    self.__historyI2MassLiquid[ facilityTime + timeStep ]  = 0.0
    self.__historyHTOMassLiquid[ facilityTime + timeStep ]  = 0.0

    self.__historyNOMassVapor[ facilityTime ] = 0.0
    self.__historyNO2MassVapor[ facilityTime ] = 0.0

    self.__historyXeMassVapor[ facilityTime + timeStep ]   = 0.0
    self.__historyKrMassVapor[ facilityTime + timeStep ]   = 0.0
    self.__historyI2MassVapor[ facilityTime + timeStep ]   = 0.0
    self.__historyHTOMassVapor[ facilityTime + timeStep ]   = 0.0
    self.__historyRuO4MassVapor[ facilityTime + timeStep ] = 0.0
    self.__historyCO2MassVapor[ facilityTime + timeStep ]  = 0.0

    #................................................
    self.__UpdateStateVariables( facilityTime, timeStep )
    #................................................

  return

#---------------------------------------------------------------------------------
 def __UpdateStateVariables( self, facilityTime, timeStep ):
  
  """
  if self.__volatileSpecies is not None:

    # place holder for evolving species in dissolution; 
    # modeling as a log-normal distribution with positive skewness (right-skewness)

    # here is the mass packet entering the system at facilityTime

    for key in self.__volatileSpecies:

      (mass, massUnit) = self.__volatileSpecies[ key ] 

      t0 = self.__dissolutionStartedTime 
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

  """

  if self.__fuelSegments is not None:


    self.__LeachFuel( facilityTime, timeStep )

    species = self.__GetVolatileSpecies()

    for key in species:

      (mass, massUnit) = species[ key ] 

      if key == 'Xe':
        self.__historyXeMassVapor[ facilityTime + timeStep ] = \
             self.__volatileSpecies0[key][0] - mass

      if key == 'Kr':
        self.__historyKrMassVapor[ facilityTime + timeStep ] = \
             self.__volatileSpecies0[key][0] - mass 

      if key == 'I2':
        massSplit = 0.85
        self.__historyI2MassVapor[ facilityTime + timeStep ] =  \
             (self.__volatileSpecies0[key][0] - mass) * massSplit
        self.__historyI2MassLiquid[ facilityTime + timeStep ] = \
             (self.__volatileSpecies0[key][0] - mass) * (1.0-massSplit)
#        print(' **************************** ')
#        print(' self.__volatileSpecies0   = ',  self.__volatileSpecies0[key][0])
#        print(' self.__historyI2MassVapor = ',  self.__historyI2MassVapor[facilityTime+timeStep])
#        print(' self.__historyI2MassLiquid = ', self.__historyI2MassLiquid[facilityTime+timeStep])
#        print(' **************************** ')

      if key == 'HTO':
        massSplit = 0.20
        self.__historyHTOMassVapor[ facilityTime + timeStep ] = \
             (self.__volatileSpecies0[key][0] - mass) * massSplit
        self.__historyHTOMassLiquid[ facilityTime + timeStep ] = \
             (self.__volatileSpecies0[key][0] - mass) * (1.0-massSplit)

      if key == 'RuO4':
        self.__historyRuO4MassVapor[ facilityTime + timeStep ] = \
             self.__volatileSpecies0[key][0] - mass

      if key == 'CO2':
        self.__historyCO2MassVapor[ facilityTime + timeStep ] = \
             self.__volatileSpecies0[key][0] - mass

  else:

      self.__historyXeMassVapor[ facilityTime + timeStep ]   = 0.0
      self.__historyKrMassVapor[ facilityTime + timeStep ]   = 0.0
      self.__historyI2MassVapor[ facilityTime + timeStep ]   = 0.0
      self.__historyHTOMassVapor[ facilityTime + timeStep ]   = 0.0
      self.__historyRuO4MassVapor[ facilityTime + timeStep ] = 0.0
      self.__historyCO2MassVapor[ facilityTime + timeStep ]  = 0.0

      self.__historyI2MassLiquid[ facilityTime + timeStep ]  = 0.0
      self.__historyHTOMassLiquid[ facilityTime + timeStep ]  = 0.0

      self.__historyHNO3MolarLiquid[ facilityTime + timeStep ]  = self.__startingHNO3Molarity 
      self.__historyH2OMassLiquid[facilityTime] = 1000.0 * self.__dissolverVolume - self.__startingHNO3Molarity * self.__molarMassHNO3 * self.__dissolverVolume
      self.__historyUNMassConcLiquid[ facilityTime + timeStep ] = 0.0
      self.__historyPuNMassConcLiquid[ facilityTime + timeStep ] = 0.0
      self.__historyFPNMassConcLiquid[ facilityTime + timeStep ] = 0.0

      self.__historyNOMassVapor[ facilityTime + timeStep ]   = 0.0
      self.__historyNO2MassVapor[ facilityTime + timeStep ]   = 0.0

      self.__historyRuO4MassVapor[ facilityTime + timeStep ] = 0.0
      self.__historyCO2MassVapor[ facilityTime + timeStep ]  = 0.0

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
 def __GetVolatileSpecies( self ):

  species = dict()

  if self.__fuelSegments is None: return None
 
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

  species['I2']   = ( massI2, massI2Unit )
  species['Kr']   = ( massKr, massKrUnit )
  species['Xe']   = ( massXe, massXeUnit )
  species['RuO4'] = ( massRuO4, massRuO4Unit )
  species['CO2']  = ( massCO2, massCO2Unit )
  species['HTO']  = ( massHTO, massHTOUnit )

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
#      assert v.get('unit').strip() == 'gram/min', 'invalid mass unit'
      assert v.get('unit').strip() == 'gram', 'invalid mass unit'
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
           if varName == 'Kr Condensate':
              ivar = varNames.index(varName)
              mass = float(varValues[ivar])
 #             if facilityTime in self.__historyI2MassLiquid.keys():
              self.__historyKrMassVapor[ facilityTime ] += mass
 #             else:
 #                self.__historyKrMassLiquid[ facilityTime ] = mass

              s = '__GetCondensate(): received condensate at '+str(facilityTime)+' [min]; Kr mass [g] = '+str(round(mass,3))
              self.__log.debug(s)
           # end of: if varName == 'Kr Condensate':

    # end for n in nodes:

    if found is False: time.sleep(1) 

  # end of while found is False:

  return 

#---------------------------------------------------------------------------------
 def __LeachFuel( self, facilityTime, timeStep ):

  if self.__fuelSegments is None: return 

  dissolverVolume = self.__dissolverVolume
  roughnessF = self.__roughnessF 

  molarityHNO3 = self.__historyHNO3MolarLiquid[ facilityTime ]

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

  #----------------------------------------------------------
  # begin assembly of the ODE system; x is the unknown vector
  #----------------------------------------------------------

  x        = list()
  x0       = list()
  varNames = list()

  #...................................................
  # data for each fuel segment
  #...................................................

  segParams = list()

  segId = 0
  for (segGeoData,segCompData) in zip(segmentsGeoData,segmentsCompData):

    for (name,unit,value) in segGeoData:
      if name=='mass': 
        mass = value
      if name=='massDensity': 
        dens = value
      if name=='innerDiameter': 
        iD = value
      if name=='length': 
        length = value

    segDissolArea = 2.0 * math.pi * iD * iD / 4.0 + \
                    length * 0.2 * math.pi * iD  # add 20% cladding infiltration

    for (name,unit,value) in segCompData:
      if name=='U':
         uMass = value
      if name=='Pu':
         puMass = value
      if name=='FP':
         fpMass = value

    mUO2       = uMass  + uMass/uMolarMass*2.0*16.0
    mPuO2      = puMass + puMass/puMolarMass*2.0*16.0
    mFPO1dot18 = fpMass + fpMass/fpMolarMass*1.18*16.0

    addedMass  = uMass/uMolarMass*2.0*16.0
    addedMass += puMass/puMolarMass*2.0*16.0
    addedMass += fpMass/fpMolarMass*1.18*16.0

    originalMass = mass
    mass += addedMass

    wUO2       = 0.0
    wPuO2      = 0.0
    wFPO1dot18 = 0.0

    if mass > 0.0: wUO2       = mUO2 / mass
    if mass > 0.0: wPuO2      = mPuO2 / mass
    if mass > 0.0: wFPO1dot18 = mFPO1dot18 / mass

    molesUO2       = mUO2/uo2MolarMass
    molesPuO2      = mPuO2/puo2MolarMass
    molesFPO1dot18 = mFPO1dot18/fpo1dot18MolarMass

    molesTotal = molesUO2 + molesPuO2 + molesFPO1dot18
  
    xUO2       = 0.0
    xPuO2      = 0.0
    xFPO1dot18 = 0.0

    if molesTotal > 0.0: xUO2       = molesUO2/molesTotal
    if molesTotal > 0.0: xPuO2      = molesPuO2/molesTotal
    if molesTotal > 0.0: xFPO1dot18 = molesFPO1dot18/molesTotal

    mReactOrder = 2.0*(2.0-xUO2)

    rhoPrime = 0.0
    denom = xUO2 * rhoUO2 + xPuO2 * rhoPuO2 + xFPO1dot18 * rhoFPO1dot18 
    if denom > 0.0: rhoPrime = 100.0 * dens / denom

    rateCte = ( 0.48 * math.exp(-0.091*rhoPrime) )**(xUO2) * \
              ( 5.0 * math.exp(-0.27*rhoPrime) )**(1-xUO2)

    dissolMassRate = - rateCte * molarityHNO3**mReactOrder * roughnessF * segDissolArea
 
    """
    print('*********** segment ***********')
    print('timeStep min = ', timeStep)
    print('dissolMassRate g/s = ', dissolMassRate)
    print('dissolv mass g/min = ', dissolMassRate*60.0)
    print('rateCte = ', rateCte)
    print('molarityHNO3 M = ', molarityHNO3)
    print('mReactOrder = ', mReactOrder)
    print('rhoPrime % = ', rhoPrime)
    print('dens  g/cc= ', dens)
    print('xUO2 = ', xUO2)
    print('xPuO2 = ', xPuO2)
    print('xFPO1dot18 = ', xFPO1dot18)
    print('wUO2 = ', wUO2)
    print('wPuO2 = ', wPuO2)
    print('wFPO1dot18 = ', wFPO1dot18)
    print('segDissolArea mm^2 = ', segDissolArea)
    print('seg mass g = ', mass)
    """
    a = dict()
    a['rateCte']            = rateCte
    a['roughnessF']         = roughnessF
    a['segDissolArea']      = segDissolArea
    a['mReactOrder']        = mReactOrder
    a['uo2MolarMass']       = uo2MolarMass
    a['puo2MolarMass']      = puo2MolarMass
    a['fpo1dot18MolarMass'] = fpo1dot18MolarMass
    a['wUO2']               = wUO2
    a['wPuO2']              = wPuO2
    a['wFPO1dot18']         = wFPO1dot18

    segParams.append(a)

    x0.append(originalMass)

    varNames.append('seg'+'-'+str(segId))
    segId += 1

  # end of: for (segGeoData,segCompData) in zip(segmentsGeoData,segmentsCompData):

#  print('****** initial values ******')
#  print(x0)

  #...................................................
  # data for nitric acid 
  #...................................................

  hno3Params = dict()

  hno3Params['molarMassHNO3'] = self.__molarMassHNO3

  massHNO3 = molarityHNO3 * self.__molarMassHNO3 * dissolverVolume

  x0.append(massHNO3)

  varNames.append('hno3')

  #...................................................
  # data for UN 
  #...................................................

  unParams = dict()

  unParams['molarMassUO2NO3_2'] = self.__molarMassUO2NO3_2

  massConc = self.__historyUNMassConcLiquid[ facilityTime ] 
  mass = massConc * dissolverVolume
  
  x0.append(mass)

  varNames.append('un')

  #...................................................
  # data for PuN
  #...................................................

  punParams = dict()

  punParams['molarMassPuNO3_4'] = self.__molarMassPuNO3_4

  massConc = self.__historyPuNMassConcLiquid[ facilityTime ] 
  mass = massConc * dissolverVolume

  x0.append(mass)

  varNames.append('pun')

  #...................................................
  # data for FPN
  #...................................................

  fpnParams = dict()

  fpnParams['molarMassFPNO3_2dot36'] = self.__molarMassFPNO3_2dot36

  massConc = self.__historyFPNMassConcLiquid[ facilityTime ] 
  mass = massConc * dissolverVolume

  x0.append(mass)

  varNames.append('fpn')

  #...................................................
  # data for H2O
  #...................................................

  h2oParams = dict()

  h2oParams['molarMassH2O'] = self.__molarMassH2O

  massH2O = self.__historyH2OMassLiquid[ facilityTime ] 

  x0.append(massH2O)

  varNames.append('h2o')

  #...................................................
  # data for NO  
  #...................................................

  noParams = dict()

  noParams['molarMassNO'] = self.__molarMassNO

  massNO = self.__historyNOMassVapor[ facilityTime ] 

  x0.append(massNO)

  varNames.append('no')

  #...................................................
  # data for NO2
  #...................................................

  no2Params = dict()

  no2Params['molarMassNO2'] = self.__molarMassNO2

  massNO2 = self.__historyNO2MassVapor[ facilityTime ] 

  x0.append(massNO2)

  varNames.append('no2')

  #-----------------------------
  # Solve mass balance equations
  #-----------------------------

  t = np.arange(0.0,timeStep*60.0) # two output times

  x = odeint( self.__fx, x0, t, 
              args=( varNames, 
                     dissolverVolume,
                     segParams, hno3Params, unParams, punParams, fpnParams, h2oParams,
                     noParams, no2Params ) )

#  print('******* solution vector *******')
#  print(x[0,:])
#  print(x[1,:])

  #----------------------------------------------------------
  # Update the solid mass in the system (history is not saved)
  #----------------------------------------------------------

  # Reduce the mass in the solids inventory

  newSegmentsGeoData  = list()
  newSegmentsCompData = list()

  for varName in varNames:

    if varName.split('-')[0] == 'seg':
      index = varNames.index(varName)
#      print('index = ',index)
      reducedMass = x[1,:][index]
      if reducedMass < 0.0: reducedMass = 0.0
#      print('reducedMass = ',reducedMass)
      segGeoData = segmentsGeoData[index]
      for (name,unit,value) in segGeoData:
        if name=='mass': 
          mass = value
          massUnit = unit
        if name=='massDensity': 
          dens = value
          densUnit = unit
        if name=='innerDiameter': 
          iD = value
          iDUnit = unit
        if name=='length': 
          lengthUnit = unit
      # end of: for (name,unit,value) in segGeoData:
#      print('mass = ',mass)
      reducedVol = reducedMass/dens
      area = math.pi * iD * iD / 4.0
      reducedLength = 0.0
      if area > 0.0: reducedLength = reducedVol*1000.0 / area
      if reducedVol == 0.0: iD = 0.0; reducedLength = 0.0
#      print('reducedLength = ',reducedLength)
#      print('length = ',length)
      newSegGeoData = list()
      newSegGeoData.append( ('mass',massUnit,reducedMass) )
      newSegGeoData.append( ('massDensity',densUnit,dens) )
      newSegGeoData.append( ('innerDiameter',iDUnit,iD) )
      newSegGeoData.append( ('length',lengthUnit,reducedLength) )
      newSegmentsGeoData.append( newSegGeoData )

      massReduction = 0.0
      if mass > 0.0:
        massReduction = reducedMass/mass
#      print('massReduction = ', massReduction)

      segCompData = segmentsCompData[index]
      newSegCompData = list()
      for (name,unit,value) in segCompData:
        newSegCompData.append( (name,unit,value*massReduction) )
      newSegmentsCompData.append( newSegCompData )

    # end of: if varName.split('-')[0] == 'seg':

  # end of: for (name,value) in zip(varNames,x[1,:]):

  self.__fuelSegments = (newSegmentsGeoData,newSegmentsCompData)

  #----------------------------------------------------------
  # Update molarity of nitric acid in the liquid (save history)
  #----------------------------------------------------------

  index = varNames.index('hno3')
  massHNO3 = x[1,:][index]
  molarityHNO3 = massHNO3 / self.__molarMassHNO3 / dissolverVolume

  self.__historyHNO3MolarLiquid[ facilityTime + timeStep ] = molarityHNO3

  #----------------------------------------------------------
  # Update UN mass concentration 
  #----------------------------------------------------------

  index = varNames.index('un')
  massUN = x[1,:][index]
  massConcUN = massUN / dissolverVolume

  self.__historyUNMassConcLiquid[ facilityTime + timeStep ] = massConcUN

  #----------------------------------------------------------
  # Update PuN mass concentration 
  #----------------------------------------------------------

  index = varNames.index('pun')
  massPuN = x[1,:][index]
  massConcPuN = massPuN / dissolverVolume

  self.__historyPuNMassConcLiquid[ facilityTime + timeStep ] = massConcPuN

  #----------------------------------------------------------
  # Update PuN mass concentration 
  #----------------------------------------------------------

  index = varNames.index('fpn')
  massFPN = x[1,:][index]
  massConcFPN = massFPN / dissolverVolume

  self.__historyFPNMassConcLiquid[ facilityTime + timeStep ] = massConcFPN

  #----------------------------------------------------------
  # Update mass of H2O in the liquid (save history)
  #----------------------------------------------------------

  index = varNames.index('h2o')
  massH2O = x[1,:][index]

  self.__historyH2OMassLiquid[ facilityTime + timeStep ] = massH2O       

  #----------------------------------------------------------
  # Update mass of NO in the vapor (save history)
  #----------------------------------------------------------

  index = varNames.index('no')
  massNO = x[1,:][index]

#  if abs( massNO - self.__historyNOMassVapor[ facilityTime ] ) < 1.0e-4:
#     self.__historyNOMassVapor[ facilityTime + timeStep ] = 0.0
#  else:
#     self.__historyNOMassVapor[ facilityTime + timeStep ] = massNO

  self.__historyNOMassVapor[ facilityTime + timeStep ] = massNO

  #----------------------------------------------------------
  # Update mass of NO2 in the vapor (save history)
  #----------------------------------------------------------

  index = varNames.index('no2')
  massNO2 = x[1,:][index]

#  if abs( massNO2 - self.__historyNO2MassVapor[ facilityTime ] ) < 1.0e-4:
#     self.__historyNO2MassVapor[ facilityTime + timeStep ] = 0.0
#  else:
#     self.__historyNO2MassVapor[ facilityTime + timeStep ] = massNO2

  self.__historyNO2MassVapor[ facilityTime + timeStep ] = massNO2

  #----------------------------------------------------------
  # Apply gas-liquid phase equilibrium for NOx after the fact; FIX THIS LATER
  #----------------------------------------------------------

  if facilityTime > 0.0:

     """
     massNO   = self.__historyNOMassVapor[ facilityTime + timeStep ] 
     molesNO  = massNO / self.__molarMassNO

     massH2O  = self.__historyH2OMassLiquid[ facilityTime + timeStep ] 
     molesH2O = massH2O / self.__molarMassH2O

     massNO2  = self.__historyNO2MassVapor[ facilityTime + timeStep ] 
     molesNO2 = massNO2 / self.__molarMassNO2

     molesHNO3 = self.__historyHNO3MolarLiquid[ facilityTime + timeStep ] * self.__dissolverVolume

     molesNOproduced = excess * 1.0/3.0
     molesHNO3produced = excess * 1.0/2.0
     massNOproduced = molesNOproduced * molesH20 * self.__molarMassNO
     self.__historyNOMassVapor[ facilityTime + timeStep ] += massNOproduced
     totalMolesHNO3 = molesHNO3produced + molesHNO3
     self.__historyHNO3MolarLiquid[ facilityTime + timeStep ] = totalMolesHNO3 / self.__dissolverVolume

     """

#     if massNO == 0.0 and massNO2 != 0.0: 

#     eqFactor = random.random() * 1.0/100.0
     eqFactor = 5.0/100.0
     massNO   = eqFactor * abs(massNO2-self.__historyNO2MassVapor[facilityTime])
     massNO2  -= massNO
     self.__historyNOMassVapor[ facilityTime + timeStep ]  += massNO
     self.__historyNO2MassVapor[ facilityTime + timeStep ] = massNO2
     molesNO2 = massNO2 / self.__molarMassNO2
     massH2O = 1.0/3.0 * molesNO2 * self.__molarMassH2O
     # liquid water consumed to form NO in the vapor
     self.__historyH2OMassLiquid[ facilityTime + timeStep ] -= massH2O
     molesNO = massNO / self.__molarMassNO
     massHNO3 = 2.0 * molesNO * self.__molarMassHNO3
     totalMassHNO3 = self.__historyHNO3MolarLiquid[ facilityTime + timeStep ] * self.__dissolverVolume * self.__molarMassHNO3 
     # nitric acid formed 
     totalMassHNO3 += massHNO3
     self.__historyHNO3MolarLiquid[ facilityTime + timeStep ] = totalMassHNO3 / self.__molarMassHNO3 / self.__dissolverVolume

#     if massNO != 0.0 and massNO2 == 0.0: 

#     eqFactor = random.random() * 99.0/100.0
#     eqFactor = 1.0/100.0
#     massNO2  = eqFactor * massNO
#     massNO  *= (1.0-eqFactor)
#     self.__historyNOMassVapor[ facilityTime + timeStep ]  = massNO
#     self.__historyNO2MassVapor[ facilityTime + timeStep ] = massNO2
#     molesNO = massNO / self.__molarMassNO
#     massH2O = molesNO * self.__molarMassH2O
#     # liquid water produced when consuming NO
#     self.__historyH2OMassLiquid[ facilityTime + timeStep ] += massH2O
#     massHNO3 = 2.0 * molesNO * self.__molarMassHNO3
#     totalMassHNO3 = self.__historyHNO3MolarLiquid[ facilityTime + timeStep ] * self.__dissolverVolume * self.__molarMassHNO3 
#     # nitric acid consumed
#     totalMassHNO3 -= massHNO3
#     self.__historyHNO3MolarLiquid[ facilityTime + timeStep ] = totalMassHNO3 / self.__molarMassHNO3 / self.__dissolverVolume
#     """
 
#--------------------------------------------------------------------------------
 def __fx( self, x, t,     
          varNames, 
          dissolverVolume,  
          segParams, hno3Params, unParams, punParams, fpnParams, h2oParams,
          noParams, no2Params ):

  fvec = list()

  #...................................................
  # equations for fuel segments
  #...................................................

  index         = varNames.index('hno3')
  massHNO3      = x[index]
  molarMassHNO3 = hno3Params['molarMassHNO3']
  molarityHNO3  = massHNO3 / molarMassHNO3 / dissolverVolume

  molesRateUO2  = 0.0
  molesRatePuO2 = 0.0
  molesRateFPO1dot18 = 0.0
  
  for p in segParams:

    index = segParams.index(p)
    
    rateCte            =  p['rateCte']             
    roughnessF         =  p['roughnessF']          
    segDissolArea      =  p['segDissolArea']       
    mReactOrder        =  p['mReactOrder']         
    uo2MolarMass       =  p['uo2MolarMass']        
    puo2MolarMass      =  p['puo2MolarMass']       
    fpo1dot18MolarMass =  p['fpo1dot18MolarMass']  
    wUO2               =  p['wUO2']                
    wPuO2              =  p['wPuO2']               
    wFPO1dot18         =  p['wFPO1dot18']          

    f = - rateCte * roughnessF * segDissolArea * molarityHNO3 ** mReactOrder

    molesRateUO2       += abs(f) / uo2MolarMass       * wUO2
    molesRatePuO2      += abs(f) / puo2MolarMass      * wPuO2
    molesRateFPO1dot18 += abs(f) / fpo1dot18MolarMass * wFPO1dot18
 
    fvec.append(f)

  # end of: for p in segParams:

  #...................................................
  # equation for nitric acid
  #...................................................

  if molarityHNO3 <= 8.0:
     f = - ( 2.7*molesRateUO2 + 4.0*molesRatePuO2 + 2.36*molesRateFPO1dot18 ) * molarMassHNO3
  else:
     f = - ( 4.0*molesRateUO2 + 4.0*molesRatePuO2 + 2.36*molesRateFPO1dot18 ) * molarMassHNO3

  fvec.append(f)

  #...................................................
  # equation for UN 
  #...................................................

  molarMassUO2NO3_2 = unParams['molarMassUO2NO3_2']

  f = molesRateUO2 * molarMassUO2NO3_2 

  fvec.append(f)

  #...................................................
  # equation for PuN 
  #...................................................

  molarMassPuNO3_4 = punParams['molarMassPuNO3_4'] 

  f = molesRatePuO2 * molarMassPuNO3_4 

  fvec.append(f)

  #...................................................
  # equation for FPN 
  #...................................................

  molarMassFPNO3_2dot36 = fpnParams['molarMassFPNO3_2dot36'] 

  f = molesRateFPO1dot18 * molarMassFPNO3_2dot36 

  fvec.append(f)

  #...................................................
  # equation for H2O 
  #...................................................

  molarMassH2O = h2oParams['molarMassH2O']

  if molarityHNO3 <= 8.0:
     f = ( 1.3*molesRateUO2 + 2.0*molesRatePuO2 + 1.18*molesRateFPO1dot18 ) * molarMassH2O
  else:
     f = ( 2.0*molesRateUO2 + 2.0*molesRatePuO2 + 1.18*molesRateFPO1dot18 ) * molarMassH2O

  fvec.append(f)

  #...................................................
  # equation for NO  
  #...................................................

  index = varNames.index('no2')

  molarMassNO = noParams['molarMassNO']

  if molarityHNO3 <= 8.0:
     f = 0.7*molesRateUO2 * molarMassNO
  else:
     f = 0.0

  fvec.append(f)

  #...................................................
  # equation for NO2
  #...................................................

#  index = varNames.index('hno3')

  molarMassNO2 = no2Params['molarMassNO2']

  if molarityHNO3 <= 8.0:
     f = 0.0
  else:
     f = 2.0*molesRateUO2 * molarMassNO2

  fvec.append(f)

  #...................................................

  return fvec

#*********************************************************************************
# Usage: -> python dissolver.py
if __name__ == "__main__":
 print('Unit testing for Dissolver')
