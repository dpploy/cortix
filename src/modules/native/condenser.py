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
  self.__historyXeMassGas   = dict()

  self.__log = logging.getLogger('condenser')
  self.__log.info('initializing an instance of Condenser')

  self.__gramDecimals = 3 # milligram significant digits
  self.__mmDecimals   = 3 # micrometer significant digits

#---------------------------------------------------------------------------------
 def CallPorts( self, evolTime=0.0 ):

  self.__UseData( usePortName='vapor', evolTime=evolTime )     

  self.__ProvideData( providePortName='off-gas', evolTime=evolTime )     

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
  if providePortName == 'off-gas': self.__ProvideXeGas( portFile, evolTime )

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
    assert rootNode.tag == 'time-series', 'invalid format.' 

    node = rootNode.find('time')
    timeUnit = node.get('unit').strip()
    assert timeUnit == "minute"

    # vfda to do: check for single var element
    node = rootNode.find('var')
    assert node.get('name').strip() == 'Xe Vapor Flow', 'invalid variable.'
    assert node.get('unit').strip() == 'gram', 'invalid mass unit'

    nodes = rootNode.findall('timeStamp')

    for n in nodes:

      timeStamp = float(n.get('value').strip())
 
      # get data at timeStamp evolTime
      if timeStamp == evolTime:

         found = True

         mass = 0.0
         mass = float(n.text.strip())
         self.__historyXeMassVapor[ evolTime ] = mass

         s = '__GetVapor(): received vapor at '+str(evolTime)+' [min]; mass [g] = '+str(round(mass,3))
         self.__log.debug(s)

    # end for n in nodes:

    if found is False: time.sleep(1) 

  # end of while found is False:

  return 

#---------------------------------------------------------------------------------
 def __ProvideXeGas( self, portFile, evolTime ):

  # if the first time step, write the header of a time-series data file
  if evolTime == 0.0:

    fout = open( portFile, 'w')

    s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
    s = '<time-series name="XeGas-condenser">\n'; fout.write(s) 
    s = ' <comment author="cortix.modules.native.condenser" version="0.1"/>\n'; fout.write(s)
    today = datetime.datetime.today()
    s = ' <comment today="'+str(today)+'"/>\n'; fout.write(s)
    s = ' <time unit="minute"/>\n'; fout.write(s)
    s = ' <var name="Xe Off-Gas Flow" unit="gram" legend="condenser"/>\n'; fout.write(s)
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
    if len(self.__historyXeMassGas.keys()) > 0:
      mass = round(self.__historyXeMassGas[evolTime],gDec)
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
