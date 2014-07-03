#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix Dissolver module wrapper

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time
import datetime
import xml.etree.ElementTree as ElementTree
#*********************************************************************************

#*********************************************************************************
class Dissolver(object):

# Private member data
# __slots__ = [

 def __init__( self,
               ports 
             ):

  assert type(ports) is list, '-> ports type %r is invalid.' % type(ports)

  self.__ports = ports

  self.__solidsMassLoadMax = 250.0 # gram
  self.__dutyPeriod        = 120.0 # minute
  self.__ready2LoadFuel    = True 

  self.__fuelSegmentsLoad = list()

  self.__startDissolveTime = 0.0

#---------------------------------------------------------------------------------
 def CallPorts( self, evolTime=0.0 ):

  self.__ProvideData( providePortName='solids-request', evolTime=evolTime )     

  self.__UseData( usePortName='solids', evolTime=evolTime )     

#---------------------------------------------------------------------------------
 def Execute( self, evolTime=0.0, timeStep=1.0 ):

#  print('Dissolver::Execute: start dissolve time = ', self.__startDissolveTime)

  if len(self.__fuelSegmentsLoad) != 0:

     print('\n')
     print('********************************************************')
     print('Dissolver::Execute: evolTime = ',evolTime )
     print('Dissolver::Execute: ready to load? = ', self.__ready2LoadFuel)
     print('Dissolver::Execute: fuel load: # fuel segments = ', len(self.__fuelSegmentsLoad) )
     print('********************************************************')

     if self.__startDissolveTime != 0.0:
        assert evolTime >= self.__startDissolveTime + self.__dutyPeriod

     self.__ready2LoadFuel = False
     self.__startDissolveTime = evolTime

     time.sleep(1) # RUN the Dissolver for a "timeStep" time; place holder

     self.__fuelSegmentsLoad = list()

  if evolTime >= self.__startDissolveTime + self.__dutyPeriod: 
     self.__ready2LoadFuel = True

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

    maxNTrials = 5
    nTrials    = 0
    while not os.path.isfile(portFile) and nTrials < maxNTrials:
      nTrials += 1
#      print('Dissolver::__GetPortFile: waiting for port:',portFile)
      time.sleep(1)

    assert os.path.isfile(portFile) is True, 'portFile %r not available' % portFile
    time.sleep(1) # allow for file to finish writing

  if providePortName is not None:

    assert usePortName is None

    for port in self.__ports:
     if port[0] == providePortName and port[1] == 'provide': portFile = port[2]
 

  assert portFile is not None, 'portFile is invalid.'

  return portFile

#---------------------------------------------------------------------------------
 def __ProvideSolidsRequest( self, portFile, evolTime ):

  fout = open( portFile, 'w')
  s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
  s = '<!-- Written by Dissolver.py -->\n'; fout.write(s)
  s = '<dissolutionFuelRequest>\n'; fout.write(s)
  s = ' <timeStamp value="'+str(evolTime)+'" unit="minute">\n'; fout.write(s)

#  print('Dissolver::__ProvideSolidsRequest(): evolTime = ',evolTime)
#  print('Dissolver::__ProvideSolidsRequest(): ready to load = ',self.__ready2LoadFuel)

  if  self.__ready2LoadFuel is True:
 
    if self.__startDissolveTime != 0.0:
      assert evolTime >= self.__startDissolveTime + self.__dutyPeriod

    s = '  <fuelLoad unit="gram">'+str(self.__solidsMassLoadMax)+'</fuelLoad>\n';fout.write(s)

  s = ' </timeStamp>\n'; fout.write(s)
  s = '</dissolutionFuelRequest>\n'; fout.write(s)
  fout.close()

#    tree = ElementTree.parse( portFile )
#    rootNode = tree.getroot()
#    a = ElementTree.Element('timeStamp')
#    a.set('value',str(evolTime))
#    a.set('unit','minute')
#    if  self.__ready2LoadFuel == True:
#      b = ElementTree.SubElement(a, 'fuelLoad')
#      b.set('unit','gram')
#      b.text = str(self.__solidsMassLoadMax)
#    rootNode.append(a)
#
#    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

#---------------------------------------------------------------------------------
 def __GetSolids( self, portFile, evolTime ):

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
       if child.tag == 'FP':
          segFP            = float(child.text.strip())
          attributes       = child.items()
          assert len(attributes) == 1
          assert attributes[0][0] == 'unit'
          segFPUnit = attributes[0][1]

#     os.system( 'cp ' + portFile + ' /tmp/.')
     fuelSegment = ( segTimeStamp, segMass, segLength, segID, 
                     segU,         segPu,   segI,      segFP  )

     fuelSegmentsLoad.append( fuelSegment )

  # remove the data file after reading it 
#  os.system( 'cp ' + portFile + ' /tmp/.')
  os.system( 'rm -f ' + portFile )

#  print('Dissolver::__GetSolids: len(fuelSegmentsLoad)',len(fuelSegmentsLoad))

  return  fuelSegmentsLoad

#*********************************************************************************
# Usage: -> python dissolver.py
if __name__ == "__main__":
 print('Unit testing for Dissolver')
