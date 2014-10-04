#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Condenser module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import math, random
import logging
import xml.etree.ElementTree as ElementTree
#*********************************************************************************

#*********************************************************************************
class Condenser(object):

# Private member data
# __slots__ = [

 def __init__( self,
               ports
             ):

# Sanity test
  assert type(ports) is list, '-> ports type %r is invalid.' % type(ports)

# Member data 

  self.__ports = ports

  self.__historyXeMassVapor = dict()
  self.__historyI2MassVapor = dict()
  self.__historyRuO4MassVapor = dict()
  self.__historyKrMassVapor = dict()

  self.__historyXeMassGas   = dict()
  self.__historyI2MassGas   = dict()
  self.__historyRuO4MassGas = dict()
  self.__historyKrMassGas   = dict()

  self.__historyI2MassLiquid   = dict()
  self.__historyXeMassLiquid   = dict()  # entrainment
  self.__historyRuO4MassLiquid = dict()  # entrainment
  self.__historyKrMassLiquid   = dict()  # entrainment

  self.__log = logging.getLogger('condensation.condenser')
  self.__log.info('initializing an instance of Condenser')

  self.__gramDecimals = 4 # tenth of a milligram significant digits
  self.__mmDecimals   = 3 # micrometer significant digits
  self.__pyplotScale  = 'log-linear'

#---------------------------------------------------------------------------------
 def CallPorts( self, facilityTime=0.0 ):

  self.__UseData( usePortName='vapor', atTime=facilityTime )     

  self.__ProvideData( providePortName='off-gas', atTime=facilityTime )     
  self.__ProvideData( providePortName='condensate', atTime=facilityTime )     

#---------------------------------------------------------------------------------
# Evolve system from facilityTime to facilityTime+timeStep
 def Execute( self, facilityTime=0.0, timeStep=0.0 ):

  s = 'Execute(): facility time [min] = ' + str(facilityTime)
  self.__log.info(s)

  self.__Condense( facilityTime, timeStep ) # starting at facilityTime to facilityTime + timeStep
 
#---------------------------------------------------------------------------------
 def __UseData( self, usePortName=None, atTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( usePortName = usePortName )

# Get data from port files
  if usePortName == 'vapor': self.__GetVapor( portFile, atTime )

#---------------------------------------------------------------------------------
 def __ProvideData( self, providePortName=None, atTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( providePortName = providePortName )

# Send data to port files
  if providePortName == 'off-gas': self.__ProvideOffGas( portFile, atTime )

  if providePortName == 'condensate': self.__ProvideCondensate( portFile, atTime )

#---------------------------------------------------------------------------------
 def __GetPortFile( self, usePortName=None, providePortName=None ):

  portFile = None

  #..........
  # Use ports
  #..........
  if usePortName is not None:

    assert providePortName is None

    for port in self.__ports:
      (portName,portType,thisPortFile) = port
      if portName == usePortName and portType == 'use': portFile = thisPortFile

    assert portFile is not None

    maxNTrials = 50
    nTrials    = 0
    while not os.path.isfile(portFile) and nTrials < maxNTrials:
      nTrials += 1
      time.sleep(1)

    if nTrials >= 10:
      s = '__GetPortFile(): waited ' + str(nTrials) + ' trials for port: ' + portFile
      self.__log.warn(s)

    assert os.path.isfile(portFile) is True, 'portFile %r not available; stop.' % portFile
  #..............
  # Provide ports
  #..............
  if providePortName is not None:

    assert usePortName is None

    for port in self.__ports:
      (portName,portType,thisPortFile) = port
      if portName == providePortName and portType == 'provide': portFile = thisPortFile

    assert portFile is not None, 'portFile is invalid.'

  return portFile

#---------------------------------------------------------------------------------
 def __Condense( self, facilityTime, timeStep ):

  gDec = self.__gramDecimals 

  entrained = random.random() * 0.08
  massXeVapor = self.__historyXeMassVapor[ facilityTime ]  
  self.__historyXeMassGas[ facilityTime + timeStep ] = massXeVapor * (1.0 - entrained)
  self.__historyXeMassLiquid[ facilityTime + timeStep ] = massXeVapor * entrained
  s = '__Condense(): Xe entrained '+str(round(massXeVapor*entrained,gDec))+' [g] at ' + str(facilityTime)+' [min]'
  self.__log.info(s)

  entrained = random.random() * 0.06
  massKrVapor = self.__historyKrMassVapor[ facilityTime ]  
  self.__historyKrMassGas[ facilityTime + timeStep ] = massKrVapor * (1.0 - entrained)
  self.__historyKrMassLiquid[ facilityTime + timeStep ] = massKrVapor * entrained
  s = '__Condense(): Kr entrained '+str(round(massKrVapor*entrained,gDec))+' [g] at ' + str(facilityTime)+' [min]'
  self.__log.info(s)

  absorbed = random.random() * 0.05
  massI2Vapor = self.__historyI2MassVapor[ facilityTime ]  
  self.__historyI2MassGas[ facilityTime + timeStep ] = massI2Vapor * (1.0 - absorbed)
  self.__historyI2MassLiquid[ facilityTime + timeStep ] = massI2Vapor * absorbed
  s = '__Condense(): I2 absorbed '+str(round(massI2Vapor*absorbed,gDec))+' [g] at ' + str(facilityTime)+' [min]'
  self.__log.info(s)

  entrained = random.random() * 0.18
  massRuO4Vapor = self.__historyRuO4MassVapor[ facilityTime ]  
  self.__historyRuO4MassGas[ facilityTime + timeStep ] = massRuO4Vapor * (1.0 - entrained)
  self.__historyRuO4MassLiquid[ facilityTime + timeStep ] = massRuO4Vapor * entrained
  s = '__Condense(): RuO4 entrained '+str(round(massRuO4Vapor*entrained,gDec))+' [g] at ' + str(facilityTime)+' [min]'
  self.__log.info(s)

  return

#---------------------------------------------------------------------------------
 def __GetVapor( self, portFile, atTime ):

  found = False

  while found is False:

    s = '__GetVapor(): checking for vapor at '+str(atTime)
    self.__log.debug(s)

    try:
      tree = ElementTree.parse( portFile )
    except ElementTree.ParseError as error:
      s = '__GetVapor(): '+portFile+' unavailable. Error code: '+str(error.code)+' File position: '+str(error.position)+'. Retrying...'
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
#      assert v.get('name').strip() == 'Xe Vapor', 'invalid variable.'
      assert v.get('unit').strip() == 'gram/min', 'invalid mass unit'
      varNames.append(name)

    timeStampNodes = rootNode.findall('timeStamp')

    for tsn in timeStampNodes:

      timeStamp = float(tsn.get('value').strip())
 
      # get data at timeStamp atTime
      if timeStamp == atTime:

         found = True

         varValues = tsn.text.strip().split(',')
         assert len(varValues) == len(varNodes), 'inconsistent data; stop.'

         for varName in varNames:
           if varName == 'Xe Vapor':
              ivar = varNames.index(varName)
              mass = float(varValues[ivar])
              self.__historyXeMassVapor[ atTime ] = mass

              s = '__GetVapor(): received vapor at '+str(atTime)+' [min]; Xe mass [g] = '+str(round(mass,3))
              self.__log.debug(s)
           # end of: if varName == 'Xe Vapor':
           if varName == 'I2 Vapor':
              ivar = varNames.index(varName)
              mass = float(varValues[ivar])
              self.__historyI2MassVapor[ atTime ] = mass

              s = '__GetVapor(): received vapor at '+str(atTime)+' [min]; I2 mass [g] = '+str(round(mass,3))
              self.__log.debug(s)
           # end of: if varName == 'I2 Vapor':
           if varName == 'RuO4 Vapor':
              ivar = varNames.index(varName)
              mass = float(varValues[ivar])
              self.__historyRuO4MassVapor[ atTime ] = mass

              s = '__GetVapor(): received vapor at '+str(atTime)+' [min]; RuO4 mass [g] = '+str(round(mass,3))
              self.__log.debug(s)
           # end of: if varName == 'RuO4 Vapor':
           if varName == 'Kr Vapor':
              ivar = varNames.index(varName)
              mass = float(varValues[ivar])
              self.__historyKrMassVapor[ atTime ] = mass

              s = '__GetVapor(): received vapor at '+str(atTime)+' [min]; Kr mass [g] = '+str(round(mass,3))
              self.__log.debug(s)
           # end of: if varName == 'Kr Vapor':

    # end for n in nodes:

    if found is False: time.sleep(1) 

  # end of while found is False:

  return 

#---------------------------------------------------------------------------------
 def __ProvideOffGas( self, portFile, atTime ):

  # if the first time step, write the header of a time-sequence data file
  if atTime == 0.0:

    assert os.path.isfile(portFile) is False, 'portFile %r exists; stop.' % portFile

    tree = ElementTree.ElementTree()
    rootNode = tree.getroot()

    a = ElementTree.Element('time-sequence')
    a.set('name','condenser-offgas')

    b = ElementTree.SubElement(a,'comment')
    b.set('author','cortix.modules.native.condenser')
    b.set('version','0.1')

    b = ElementTree.SubElement(a,'comment')
    today = datetime.datetime.today()
    b.set('today',str(today))

    b = ElementTree.SubElement(a,'time')
    b.set('unit','minute')

    # first variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Xe Off-Gas')
    b.set('unit','gram/min')
    b.set('legend','Condenser-offgas')
    b.set('scale',self.__pyplotScale)

    # second variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','I2 Off-Gas')
    b.set('unit','gram/min')
    b.set('legend','Condenser-offgas')
    b.set('scale',self.__pyplotScale)

    # third variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','RuO4 Off-Gas')
    b.set('unit','gram/min')
    b.set('legend','Condenser-offgas')
    b.set('scale',self.__pyplotScale)

    # fourth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Kr Off-Gas')
    b.set('unit','gram/min')
    b.set('legend','Condenser-offgas')
    b.set('scale',self.__pyplotScale)

    # values for all variables
    b = ElementTree.SubElement(a,'timeStamp')
    b.set('value',str(atTime))
    b.text = str('0.0') + ',' + \
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

    if len(self.__historyXeMassGas.keys()) > 0:
      massXe = round(self.__historyXeMassGas[atTime],gDec)
    else:
      massXe = 0.0

    if len(self.__historyXeMassGas.keys()) > 0:
      massI2 = round(self.__historyI2MassGas[atTime],gDec)
    else:
      massI2 = 0.0

    if len(self.__historyXeMassGas.keys()) > 0:
      massRuO4 = round(self.__historyRuO4MassGas[atTime],gDec)
    else:
      massRuO4 = 0.0

    if len(self.__historyXeMassGas.keys()) > 0:
      massKr = round(self.__historyKrMassGas[atTime],gDec)
    else:
      massKr = 0.0

    a.text = str(massXe) +','+ \
             str(massI2) +','+ \
             str(massRuO4) +','+ \
             str(massKr)  

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#---------------------------------------------------------------------------------
 def __ProvideCondensate( self, portFile, atTime ):

  # if the first time step, write the header of a time-sequence data file
  if atTime == 0.0:

    assert os.path.isfile(portFile) is False, 'portFile %r exists; stop.' % portFile

    tree = ElementTree.ElementTree()
    rootNode = tree.getroot()

    a = ElementTree.Element('time-sequence')
    a.set('name','condenser-condensate')

    b = ElementTree.SubElement(a,'comment')
    b.set('author','cortix.modules.native.condenser')
    b.set('version','0.1')

    b = ElementTree.SubElement(a,'comment')
    today = datetime.datetime.today()
    b.set('today',str(today))

    b = ElementTree.SubElement(a,'time')
    b.set('unit','minute')

    # first variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Xe Condensate')
    b.set('unit','gram/min')
    b.set('legend','Condenser-condensate')
    b.set('scale',self.__pyplotScale)

    # second variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','I2 Condensate')
    b.set('unit','gram/min')
    b.set('legend','Condenser-condensate')
    b.set('scale',self.__pyplotScale)

    # third variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','RuO4 Condensate')
    b.set('unit','gram/min')
    b.set('legend','Condenser-condensate')
    b.set('scale',self.__pyplotScale)

    # fourth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Kr Condensate')
    b.set('unit','gram/min')
    b.set('legend','Condenser-condensate')
    b.set('scale',self.__pyplotScale)

    # values for all variables
    b = ElementTree.SubElement(a,'timeStamp')
    b.set('value',str(atTime))
    b.text = str('0.0') + ',' + \
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

    if len(self.__historyXeMassLiquid.keys()) > 0:
      massXe = round(self.__historyXeMassLiquid[atTime],gDec)
    else:
      massXe = 0.0

    if len(self.__historyI2MassLiquid.keys()) > 0:
      massI2 = round(self.__historyI2MassLiquid[atTime],gDec)
    else:
      massI2 = 0.0

    if len(self.__historyRuO4MassLiquid.keys()) > 0:
      massRuO4 = round(self.__historyRuO4MassLiquid[atTime],gDec)
    else:
      massRuO4 = 0.0

    if len(self.__historyKrMassLiquid.keys()) > 0:
      massKr = round(self.__historyKrMassLiquid[atTime],gDec)
    else:
      massKr = 0.0

    a.text = str(massXe) +','+ \
             str(massI2) +','+ \
             str(massRuO4) +','+ \
             str(massKr)  

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#*********************************************************************************
# Usage: -> python condenser.py
if __name__ == "__main__":
 print('Unit testing for Condenser')
