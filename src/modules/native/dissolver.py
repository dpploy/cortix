#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Dissolver module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import logging
import xml.etree.cElementTree as ElementTree
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

  self.__fuelSegmentsLoad = list()

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

  if len(self.__fuelSegmentsLoad) != 0:

     s = 'Execute(): start new duty cycle at ' + str(evolTime) + ' [min]'
     self.__log.debug(s)
     s = 'Execute(): ready to load? = ' + str(self.__ready2LoadFuel)
     self.__log.debug(s)
     s = 'Execute(): loaded mass [g] = ' + str(round(self.__GetFuelLoadMass(),3))
     self.__log.debug(s)
     s = 'Execute(): new fuel load # segments = ' + str(len(self.__fuelSegmentsLoad))
     self.__log.debug(s)

     if self.__startDissolveTime != 0.0:
        assert evolTime >= self.__startDissolveTime + self.__dutyPeriod

     self.__ready2LoadFuel    = False
     self.__startDissolveTime = evolTime

     self.__Dissolve( )

  if evolTime >= self.__startDissolveTime + self.__dutyPeriod: 
     s = 'Execute(): signal new duty cycle at ' + str(evolTime)+' [min]'
     self.__log.debug(s)
     s = 'Execute(): loaded mass ' + str(round(self.__GetFuelLoadMass(),3))
     self.__log.debug(s)

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

  fuelSegmentsLoad = list()

  found = False

  while found is False:

    tree = ElementTree.parse( portFile )

#  print('Dissolver::__GetSolids: dumping the solids obtained at this point')
#  ElementTree.dump(tree)

    rootNode = tree.getroot()

    nodes = rootNode.findall('timeStamp')

    for n in nodes:

      timeStamp = float(n.get('value').strip())

      # must check for timeStamp
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

      else: # of if timeStamp == evolTime:

        s = '__GetSolids(): did not find time stamp '+str(evolTime)+' [min] in '+portFile
        self.__log.debug(s)

        time.sleep(1)

      # end of if timeStamp == evolTime:

    # end of for n in nodes:

#  os.system( 'cp ' + portFile + ' /tmp/.')

  # end of while found is False:

  s = '__GetSolids(): got fuel load at '+str(evolTime)+' [min], with '+str(len(fuelSegmentsLoad))+' segments'
  self.__log.debug(s)

  return  fuelSegmentsLoad

#---------------------------------------------------------------------------------
# This reads only one time step data and removes the file.
 def __GetSolids_DEPRECATED( self, portFile, evolTime ):

  tree = ElementTree.parse( portFile )

#  print('Dissolver::__GetSolids: dumping the solids obtained at this point')
#  ElementTree.dump(tree)

  rootNode = tree.getroot()

  n         = rootNode.find('timeStamp')
  timeStamp = float(n.get('value').strip())

  assert timeStamp == evolTime, 'timeStamp = %r, evolTime = %r' % (timeStamp,evolTime)

  timeStampUnit = n.get('unit').strip()
  assert timeStampUnit == "minute"

  fuelSegmentsLoad = list()

  subn = n.findall('fuelSegment')

  if len(subn) != 0:

   assert self.__ready2LoadFuel is True
   if self.__startDissolveTime != 0.0:
      assert evolTime >= self.__startDissolveTime + self.__dutyPeriod

   for fuelSegment in subn:
     for child in fuelSegment:
       if child.tag == 'timeStamp':
          segTimeStamp     = float(child.text.strip())
          attributes       = child.items()
          assert len(attributes) == 1
          assert attributes[0][0] == 'unit'
          segTimeStampUnit = attributes[0][1]
       if child.tag == 'mass':
          segMass          = float(child.text.strip())
          attributes       = child.items()
          assert len(attributes) == 1
          assert attributes[0][0] == 'unit'
          segMassUnit = attributes[0][1]
       if child.tag == 'length':
          segLength        = float(child.text.strip())
          attributes       = child.items()
          assert len(attributes) == 1
          assert attributes[0][0] == 'unit'
          segLengthUnit = attributes[0][1]
       if child.tag == 'innerDiameter':
          segID            = float(child.text.strip())
          attributes       = child.items()
          assert len(attributes) == 1
          assert attributes[0][0] == 'unit'
          segIDUnit = attributes[0][1]
       if child.tag == 'U':
          segU             = float(child.text.strip())
          attributes       = child.items()
          assert len(attributes) == 1
          assert attributes[0][0] == 'unit'
          segUUnit = attributes[0][1]
       if child.tag == 'Pu':
          segPu            = float(child.text.strip())
          attributes       = child.items()
          assert len(attributes) == 1
          assert attributes[0][0] == 'unit'
          segPuUnit = attributes[0][1]
       if child.tag == 'I':
          segI             = float(child.text.strip())
          attributes       = child.items()
          assert len(attributes) == 1
          assert attributes[0][0] == 'unit'
          segIUnit = attributes[0][1]
       if child.tag == 'Kr':
          segKr            = float(child.text.strip())
          attributes       = child.items()
          assert len(attributes) == 1
          assert attributes[0][0] == 'unit'
          segKrUnit = attributes[0][1]
       if child.tag == 'Xe':
          segXe            = float(child.text.strip())
          attributes       = child.items()
          assert len(attributes) == 1
          assert attributes[0][0] == 'unit'
          segXeUnit = attributes[0][1]
       if child.tag == 'a3H':
          seg3H            = float(child.text.strip())
          attributes       = child.items()
          assert len(attributes) == 1
          assert attributes[0][0] == 'unit'
          seg3HUnit = attributes[0][1]
       if child.tag == 'FP':
          segFP            = float(child.text.strip())
          attributes       = child.items()
          assert len(attributes) == 1
          assert attributes[0][0] == 'unit'
          segFPUnit = attributes[0][1]

 #    os.system( 'cp ' + portFile + ' /tmp/.')
     fuelSegment = ( segTimeStamp, segMass, segLength, segID, 
                     segU,         segPu,   segI,      segKr,
                     segXe,        seg3H,   segFP  )

     fuelSegmentsLoad.append( fuelSegment )


#  os.system( 'cp ' + portFile + ' /tmp/.')

  s = '__GetSolids(): got fuel load at '+str(evolTime)+' [min], with '+str(len(fuelSegmentsLoad))+' segments'
  self.__log.debug(s)

  # remove the data file after reading it 
  s = 'rm -f ' + portFile 
  os.system(s)
  self.__log.debug('__GetSolids(): '+s)


  return  fuelSegmentsLoad

#---------------------------------------------------------------------------------
 def __GetFuelLoadMass( self ):

  mass = 0.0
  for seg in self.__fuelSegmentsLoad: 
    mass += seg[1]
  
  return mass 

#---------------------------------------------------------------------------------
 def __Dissolve( self ):

#  self.__DissolverSetupSolids()

#  self.__stateHistory
  
  time.sleep(1)
  self.__fuelSegmentsLoad = list()

  return

#*********************************************************************************
# Usage: -> python dissolver.py
if __name__ == "__main__":
 print('Unit testing for Dissolver')
