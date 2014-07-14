#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Plume module 

Sun Jul 13 23:33:23 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import math, random
import pandas
import logging
import xml.etree.ElementTree as ElementTree
#*********************************************************************************

#*********************************************************************************
class Plume(object):

# Private member data
# __slots__ = [

 def __init__( self,
               ports
             ):

# Sanity test
  assert type(ports) is list, '-> ports type %r is invalid.' % type(ports)

# Member data 

  self.__ports = ports

  self.__historyXeMassOffGas = dict()

  self.__radioactivity = 1.5311e-4 # Ci/gram

  self.__log = logging.getLogger('plume')
  self.__log.info('initializing an instance of Plume')

  self.__gramDecimals = 3 # milligram significant digits
  self.__mmDecimals   = 3 # micrometer significant digits

#---------------------------------------------------------------------------------
 def CallPorts( self, evolTime=0.0 ):

  self.__UseData( usePortName='off-gas', evolTime=evolTime )     

  self.__ProvideData( providePortName='time-puff', evolTime=evolTime )     

#---------------------------------------------------------------------------------
# Evolve system from evolTime to evolTime+timeStep
 def Execute( self, evolTime=0.0, timeStep=1.0 ):

  s = 'Execute(): facility time [min] = ' + str(evolTime)
  self.__log.info(s)

  self.__Puff( evolTime, timeStep ) # starting at evolTime to evolTime + timeStep
 
#---------------------------------------------------------------------------------
 def __UseData( self, usePortName=None, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( usePortName = usePortName )

# Get data from port files
  if usePortName == 'off-gas': self.__GetOffGas( portFile, evolTime )

#---------------------------------------------------------------------------------
 def __ProvideData( self, providePortName=None, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( providePortName = providePortName )

# Send data to port files
  if providePortName == 'time-puff': self.__ProvidePuff( portFile, evolTime )

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
 def __Puff( self, evolTime, timeStep ):

  inputFile = '/home/dealmeida/mac-fvu/gentoo-home/work/codes/reprocessing/cortix/plume.input'
  
  self.__WritePlumeInput( inputFile, evolTime )

  outputFile = '/home/dealmeida/mac-fvu/gentoo-home/work/codes/reprocessing/cortix/plume.output'

  hostExec = '/home/dealmeida/mac-fvu/gentoo-home/work/codes/reprocessing/facility_pfpl/pfpl'
  
  os.system( 'time '+ hostExec + ' ' + inputFile + ' ' + outputFile + ' &' )

  s = '__Puff(): done puffing at ' + str(evolTime)+' [min]'
  self.__log.info(s)

  return

#---------------------------------------------------------------------------------
 def __GetOffGas( self, portFile, evolTime ):

  found = False

  while found is False:

    s = '__GetOffGas(): checking for off-gas at '+str(evolTime)
    self.__log.debug(s)

    try:
      tree = ElementTree.parse( portFile )
    except ElementTree.ParseError as error:
      s = '__GetOffGas(): '+portFile+' unavailable. Error code: '+str(error.code)+' File position: '+str(error.position)+'. Retrying...'
      self.__log.debug(s)
      continue

    rootNode = tree.getroot()
    assert rootNode.tag == 'time-series', 'invalid format.' 

    node = rootNode.find('time')
    timeUnit = node.get('unit').strip()
    assert timeUnit == "minute"

    # vfda to do: check for single var element
    node = rootNode.find('var')
    assert node.get('name').strip() == 'Xe Off-Gas Flow', 'invalid variable.'
    assert node.get('unit').strip() == 'gram', 'invalid mass unit'

    nodes = rootNode.findall('timeStamp')

    for n in nodes:

      timeStamp = float(n.get('value').strip())
 
      # get data at timeStamp evolTime
      if timeStamp == evolTime:

         found = True

         mass = 0.0
         mass = float(n.text.strip())
         self.__historyXeMassOffGas[ evolTime ] = mass

         s = '__GetOffGas(): received off-gas at '+str(evolTime)+' [min]; mass [g] = '+str(round(mass,3))
         self.__log.debug(s)

    # end for n in nodes:

    if found is False: time.sleep(1) 

  # end of while found is False:

  return 

#---------------------------------------------------------------------------------
 def __ProvidePuff( self, portFile, evolTime ):

  # if the first time step, write the header of a time-series data file
  if evolTime == 0.0:

    fout = open( portFile, 'w')

    s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
    s = '<time-tables name="XeGas-plume">\n'; fout.write(s) 
    s = ' <comment author="cortix.modules.native.plume" version="0.1"/>\n'; fout.write(s)
    today = datetime.datetime.today()
    s = ' <comment today="'+str(today)+'"/>\n'; fout.write(s)
    s = ' <timeStamp unit="minute" value="'+str(evolTime)+'">\n';fout.write(s)

    s = '  <column name="Plume Distance" unit="km" legend="plume">0.0</column>\n'; fout.write(s)

    s = '  <column name="Plume 1/2 Width" unit="km" legend="plume">0.0</column>\n'; fout.write(s)

    s = '  <column name="Plume 1/2 Height" unit="km" legend="plume">0.0</column>\n'; fout.write(s)

    s = '  <column name="Center Line Conc." unit="pCi/m3" legend="center line">0.0</column>\n'; fout.write(s)

    s = '  <column name="2 Sigma Conc." unit="pCi/m3" legend="2 sigma">0.0</column>\n'; fout.write(s)

    s = ' </timeStamp>\n'; fout.write(s)
    s = '</time-tables>\n'; fout.write(s)
    fout.close()

  # if not the first time step then parse the existing history file and append
  else:

    outputFile = '/home/dealmeida/mac-fvu/gentoo-home/work/codes/reprocessing/cortix/plume.output'

    time.sleep(1)

    data = pandas.read_fwf(outputFile,skiprows=9,nrows=119,widths=[16,8,7,7,11,11,11,7],names=['A','Distance [km]','1/2 Width [km]','1/2 Height [km]','Center Conc. [pCi/m3]','2Sigma Center Conc. [pCi/m3]','G','H'])

    tree = ElementTree.parse( portFile )
    rootNode = tree.getroot()

    a = ElementTree.Element('timeStamp')
    a.set('value',str(evolTime))
    a.set('unit',"minute")

    b = ElementTree.SubElement(a, 'column')
    b.set('name','Plume Distance')
    b.set('unit','km')
    b.set('legend','plume')
    s = ''
    for var in data['Distance [km]']:
      s += str(var)+','
    s = s[:-1]
    b.text = s

    c = ElementTree.SubElement(a, 'column')
    c.set('name','Plume 1/2 Width')
    c.set('unit','km')
    c.set('legend','plume')
    s = ''
    for var in data['1/2 Width [km]']:
      s += str(var)+','
    s = s[:-1]
    c.text = s

    d = ElementTree.SubElement(a, 'column')
    d.set('name','Plume 1/2 Height')
    d.set('unit','km')
    d.set('legend','plume')
    s = ''
    for var in data['1/2 Height [km]']:
      s += str(var)+','
    s = s[:-1]
    d.text = s

    e = ElementTree.SubElement(a, 'column')
    e.set('name','Center Line Conc.')
    e.set('unit','pCi/m3')
    e.set('legend','center line')
    s = ''
    for var in data['Center Conc. [pCi/m3]']:
      s += str(var)+','
    s = s[:-1]
    e.text = s

    f = ElementTree.SubElement(a, 'column')
    f.set('name','2 Sigma Conc.')
    f.set('unit','pCi/m3')
    f.set('legend','2 sigma')
    s = ''
    for var in data['2Sigma Center Conc. [pCi/m3]']:
      s += str(var)+','
    s = s[:-1]
    f.text = s

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#---------------------------------------------------------------------------------
 def __WritePlumeInput( self, inputFile, evolTime ):

  fout = open( inputFile, 'w')

  mass = self.__historyXeMassOffGas[ evolTime ]
  
  releaseRate = self.__radioactivity * mass / 60.0

  s = '2                  ! Simulation duration (hrs)\n'; fout.write(s)
  s = '60                 ! Timestep for conc calcs (sec)\n'; fout.write(s)
  s = '33.25 -81.625 10.0 ! Source Lat(N),Long(E),Height(m)\n'; fout.write(s)
  s = '3.048 3.048        ! Initial horiz. & vert. cloud dim (m)\n'; fout.write(s)
  s = '0                  ! Release type: 0=radiooactive, 1=chemical\n'; fout.write(s)
  s = "X133               ! name ('----' for interactive choice)\n"; fout.write(s)
  s = '1                  ! Dep.Vel calc choice: 0=code, 1=manual input\n'; fout.write(s)
  s = '0.01               ! Input dep.Vel(cm/s) if manual input\n'; fout.write(s)
  s = '0.1                ! Input fall vel (cm/s) if manual input\n'; fout.write(s)
  s = '293.0              ! For Chemical, gas temperature\n'; fout.write(s)
  s = '60.0               ! Release Durat(sec): >60s=>PLUME, <60s=>PUFF\n'; fout.write(s)

  s = '%18.12e%50s\n'
  t = (releaseRate,'! Release rate (Ci/s if rad, gm/s if chem)')
  fout.write(s%t)

  s = '0                  ! Rain intensity (0=none,1=light,2=heavy)\n'; fout.write(s)
  s = '2014 2 28 10 0 0   ! Release start (yr,mo,dy,hr,min,sec)--UTC!\n'; fout.write(s)
  s = '270.0 3.0 30000.0 0.0 -9999.0 -9999.0 -9999.0   ! Winddir,spd(m/s),ceiling(feet),cloudfract 0...1,siga,sige,Mixht(m) each time\n'; fout.write(s)
  s = '270.0 3.0 30000.0 0.0 -9999.0 -9999.0 -9999.0\n'; fout.write(s)
  s = '225.0 3.0 30000.0 0.0 -9999.0 -9999.0 -9999.0\n'; fout.write(s)
  s = '10.                ! Elevation of meteo input.\n'; fout.write(s)

  fout.close()
  time.sleep(1)

  s = '__WritePlumeInput(): release rate ' + str(releaseRate)+' [Ci/s]'
  self.__log.info(s)

#*********************************************************************************
# Usage: -> python plume.py
if __name__ == "__main__":
 print('Unit testing for Plume')
