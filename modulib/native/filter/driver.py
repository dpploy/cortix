#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Filter module 

Sun Jul 13 19:01:09 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import math, random
import logging
import xml.etree.ElementTree as ElementTree
#*********************************************************************************

#*********************************************************************************
class Driver():

# Private member data
# __slots__ = [

 def __init__( self,
               inputFullPathFileName, ports, evolveTime = 0.0
             ):

# Sanity test
  assert type(ports) is list, '-> ports type %r is invalid.' % type(ports)

# Member data 

  self.__ports = ports

  # hardwired for two inflows; fix this later
  self.__historyXeMassInflowGas = list()
  self.__historyXeMassInflowGas.append(dict())

  self.__historyXeMassOffGas = dict()

  self.__log = logging.getLogger('launcher-filter.filter')
  self.__log.info('initializing an instance of Filter')

  self.__gramDecimals = 4 # tenth of a milligram significant digits
  self.__mmDecimals   = 3 # micrometer significant digits

#---------------------------------------------------------------------------------
 def CallPorts( self, evolTime=0.0 ):

  for port in self.__ports:
    (portName,portType,portFile) = port
    if portName == 'inflow-gas' and portType == 'use': 
      self.__UseData( port, evolTime=evolTime )     

  self.__ProvideData( port, evolTime=evolTime )     

#---------------------------------------------------------------------------------
# Evolve system from evolTime to evolTime+timeStep
 def Execute( self, evolTime=0.0, timeStep=1.0 ):

  s = 'Execute(): facility time [min] = ' + str(evolTime)
  self.__log.info(s)

  self.__Filter( evolTime, timeStep ) # starting at evolTime to evolTime + timeStep
 
#---------------------------------------------------------------------------------
 def __UseData( self, port, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( usePort = port )

# Get data from port files
  if port[0] == 'inflow-gas': self.__GetInflowGas( portFile, evolTime )

#---------------------------------------------------------------------------------
 def __ProvideData( self, port=None, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( providePort = port )

# Send data to port files
  if port[0] == 'off-gas': self.__ProvideOffGas( portFile, evolTime )

#---------------------------------------------------------------------------------
 def __GetPortFile( self, usePort=None, providePort=None ):

  portFile = None

  #..........
  # Use ports
  #..........
  if usePort is not None:

    assert providePort is None

    portFile = usePort[2]

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
  if providePort is not None:

    assert usePort is None

    portFile = providePort[2]

  assert portFile is not None, 'portFile is invalid.'

  return portFile

#---------------------------------------------------------------------------------
 def __Filter( self, evolTime, timeStep ):

  gDec = self.__gramDecimals 

  sorbed = 0.10

  massXeInflowGas  = self.__historyXeMassInflowGas[0][ evolTime ]  

  self.__historyXeMassOffGas[ evolTime + timeStep ] = massXeInflowGas * (1.0 - sorbed)

  s = '__Filter(): filtered '+str(round(massXeInflowGas*sorbed,gDec))+' [g] at ' + str(evolTime)+' [min]'
  self.__log.info(s)

  return

#---------------------------------------------------------------------------------
 def __GetInflowGas( self, portFile, evolTime ):

  found = False

  while found is False:

    s = '__GetInflowGas(): checking for inflow gas at '+str(evolTime)+' in '+portFile
    self.__log.debug(s)

    try:
      tree = ElementTree.parse( portFile )
    except ElementTree.ParseError as error:
      s = '__GetInflowGas(): '+portFile+' unavailable. Error code: '+str(error.code)+' File position: '+str(error.position)+'. Retrying...'
      self.__log.debug(s)
      continue

    rootNode = tree.getroot()
    assert rootNode.tag == 'time-sequence', 'invalid format.' 

    inflowGasName = rootNode.get('name')

    node = rootNode.find('time')
    timeUnit = node.get('unit').strip()
    assert timeUnit == "minute"

    timeCutOff = node.get('cut-off')
    if timeCutOff is not None: 
      timeCutOff = float(timeCutOff.strip())
      if evolTime > timeCutOff: 
        if inflowGasName == 'scrubber-offgas':
          self.__historyXeMassInflowGas[0][ evolTime ] = 0.0
        return

    # vfda to do: check for single var element
    node = rootNode.find('var')
    assert node.get('name').strip() == 'Xe Off-Gas', 'invalid variable.'
#    assert node.get('unit').strip() == 'gram/min', 'invalid mass unit'

    nodes = rootNode.findall('timeStamp')

    for n in nodes:

      timeStamp = float(n.get('value').strip())
 
      # get data at timeStamp evolTime
      if timeStamp == evolTime:

         found = True

         mass = 0.0
         mass = float(n.text.strip())
          
         if inflowGasName == 'scrubber-offgas':
            self.__historyXeMassInflowGas[0][ evolTime ] = mass

         s = '__GetInflowGas(): received inflow gas '+inflowGasName+' at '+str(evolTime)+' [min]; mass [g] = '+str(round(mass,3))
         self.__log.debug(s)

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
    s = '<time-sequence name="filter-offgas">\n'; fout.write(s) 
    s = ' <comment author="cortix.modules.native.filter" version="0.1"/>\n'; fout.write(s)
    today = datetime.datetime.today()
    s = ' <comment today="'+str(today)+'"/>\n'; fout.write(s)
    s = ' <time unit="minute"/>\n'; fout.write(s)
    s = ' <var name="Xe Off-Gas" unit="gram" legend="filter-offgas"/>\n'; fout.write(s)
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
    if len(self.__historyXeMassOffGas.keys()) > 0:
      mass = round(self.__historyXeMassOffGas[evolTime],gDec)
    else:
      mass = 0.0
    a.text = str(mass)

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#*********************************************************************************
# Usage: -> python filter.py
if __name__ == "__main__":
 print('Unit testing for Filter')
