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

  self.__historyXeMassGas   = dict()
  self.__historyI2MassGas   = dict()

  self.__log = logging.getLogger('condensation.condenser')
  self.__log.info('initializing an instance of Condenser')

  self.__gramDecimals = 4 # tenth of a milligram significant digits
  self.__mmDecimals   = 3 # micrometer significant digits

#---------------------------------------------------------------------------------
 def CallPorts( self, evolTime=0.0 ):

  self.__UseData( usePortName='vapor', evolTime=evolTime )     

  self.__ProvideData( providePortName='off-gas', evolTime=evolTime )     
  self.__ProvideData( providePortName='condensate', evolTime=evolTime )     

#---------------------------------------------------------------------------------
# Evolve system from evolTime to evolTime+timeStep
 def Execute( self, evolTime=0.0, timeStep=1.0 ):

  s = 'Execute(): facility time [min] = ' + str(evolTime)
  self.__log.info(s)

  self.__Condense( evolTime, timeStep ) # starting at evolTime to evolTime + timeStep
 
#---------------------------------------------------------------------------------
 def __UseData( self, usePortName=None, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( usePortName = usePortName )

# Get data from port files
  if usePortName == 'vapor': self.__GetVapor( portFile, evolTime )

#---------------------------------------------------------------------------------
 def __ProvideData( self, providePortName=None, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( providePortName = providePortName )

# Send data to port files
  if providePortName == 'off-gas': self.__ProvideOffGas( portFile, evolTime )

  if providePortName == 'condensate': self.__ProvideCondensate( portFile, evolTime )

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
 def __Condense( self, evolTime, timeStep ):

  gDec = self.__gramDecimals 

  sorbed = random.random() * 0.10
  massXeVapor = self.__historyXeMassVapor[ evolTime ]  
  self.__historyXeMassGas[ evolTime + timeStep ] = massXeVapor * (1.0 - sorbed)
  s = '__Condense(): condensed '+str(round(massXeVapor*sorbed,gDec))+' [g] at ' + str(evolTime)+' [min]'
  self.__log.info(s)

  sorbed = random.random() * 0.05
  massI2Vapor = self.__historyI2MassVapor[ evolTime ]  
  self.__historyI2MassGas[ evolTime + timeStep ] = massI2Vapor * (1.0 - sorbed)
  s = '__Condense(): condensed '+str(round(massI2Vapor*sorbed,gDec))+' [g] at ' + str(evolTime)+' [min]'
  self.__log.info(s)

  return

#---------------------------------------------------------------------------------
 def __GetVapor( self, portFile, evolTime ):

  found = False

  while found is False:

    s = '__GetVapor(): checking for vapor at '+str(evolTime)
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
 
      # get data at timeStamp evolTime
      if timeStamp == evolTime:

         found = True

         varValues = tsn.text.strip().split(',')
         assert len(varValues) == len(varNodes), 'inconsistent data; stop.'

         for varName in varNames:
           if varName == 'Xe Vapor':
              ivar = varNames.index(varName)
              mass = float(varValues[ivar])
              self.__historyXeMassVapor[ evolTime ] = mass

              s = '__GetVapor(): received vapor at '+str(evolTime)+' [min]; Xe mass [g] = '+str(round(mass,3))
              self.__log.debug(s)
           # end of: if varName == 'Xe Vapor':
           if varName == 'I2 Vapor':
              ivar = varNames.index(varName)
              mass = float(varValues[ivar])
              self.__historyI2MassVapor[ evolTime ] = mass

              s = '__GetVapor(): received vapor at '+str(evolTime)+' [min]; I2 mass [g] = '+str(round(mass,3))
              self.__log.debug(s)
           # end of: if varName == 'I2 Vapor':

    # end for n in nodes:

    if found is False: time.sleep(1) 

  # end of while found is False:

  return 

#---------------------------------------------------------------------------------
 def __ProvideOffGas( self, portFile, evolTime ):

  # if the first time step, write the header of a time-sequence data file
  if evolTime == 0.0:

    fout = open( portFile, 'w')

    s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
    s = '<time-sequence name="condenser-offgas">\n'; fout.write(s) 
    s = ' <comment author="cortix.modules.native.condenser" version="0.1"/>\n'; fout.write(s)
    today = datetime.datetime.today()
    s = ' <comment today="'+str(today)+'"/>\n'; fout.write(s)
    s = ' <time unit="minute"/>\n'; fout.write(s)
    s = ' <var name="Xe Off-Gas" unit="gram/min" legend="Condenser-offgas"/>\n'; fout.write(s)
    mass = 0.0
    s = ' <timeStamp value="'+str(evolTime)+'">'+str(mass)+'</timeStamp>\n';fout.write(s)

    s = '</time-sequence>\n'; fout.write(s)
    fout.close()

  # if not the first time step then parse the existing history file and append
  else:

    tree = ElementTree.parse( portFile )
    rootNode = tree.getroot()
    a = ElementTree.Element('timeStamp')
    a.set('value',str(evolTime))
    gDec = self.__gramDecimals
    if len(self.__historyXeMassGas.keys()) > 0:
      mass = round(self.__historyXeMassGas[evolTime],gDec)
    else:
      mass = 0.0
    a.text = str(mass)

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#---------------------------------------------------------------------------------
 def __ProvideCondensate( self, portFile, evolTime ):

  # if the first time step, write the header of a time-sequence data file
  if evolTime == 0.0:

    fout = open( portFile, 'w')

    s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
    s = '<time-sequence name="condenser-condensate">\n'; fout.write(s) 
    s = ' <comment author="cortix.modules.native.condenser" version="0.1"/>\n'; fout.write(s)
    today = datetime.datetime.today()
    s = ' <comment today="'+str(today)+'"/>\n'; fout.write(s)
    s = ' <time unit="minute"/>\n'; fout.write(s)
    s = ' <var name="I2 Condensate" unit="gram/min" legend="Condenser-condensate"/>\n'; fout.write(s)
    mass = 0.0
    s = ' <timeStamp value="'+str(evolTime)+'">'+str(mass)+'</timeStamp>\n';fout.write(s)

    s = '</time-sequence>\n'; fout.write(s)
    fout.close()

  # if not the first time step then parse the existing history file and append
  else:

    tree = ElementTree.parse( portFile )
    rootNode = tree.getroot()
    a = ElementTree.Element('timeStamp')
    a.set('value',str(evolTime))
    gDec = self.__gramDecimals
    if len(self.__historyI2MassGas.keys()) > 0:
      mass = round(self.__historyI2MassGas[evolTime],gDec)
    else:
      mass = 0.0
    a.text = str(mass)

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#*********************************************************************************
# Usage: -> python condenser.py
if __name__ == "__main__":
 print('Unit testing for Condenser')
