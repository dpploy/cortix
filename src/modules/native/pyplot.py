#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native PyPlot module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import logging
import xml.etree.ElementTree as ElementTree
import numpy as np
import matplotlib.pyplot as plt
#*********************************************************************************

#*********************************************************************************
class PyPlot(object):

# Private member data
# __slots__ = [

 def __init__( self,
               ports 
             ):

  assert type(ports) is list, '-> ports type %r is invalid.' % type(ports)

  self.__ports = ports

  self.__timeSeriesData = dict(list())

  self.__log = logging.getLogger('pyplot')
  self.__log.info('initializing an instance of PyPlot')

  self.__gramDecimals = 3 # milligram significant digits

#---------------------------------------------------------------------------------
 def CallPorts(self, evolTime=0.0):

  self.__UseData( usePortName='time-series', evolTime=evolTime  )
 
#---------------------------------------------------------------------------------
 def Execute( self, evolTime=0.0, timeStep=1.0 ):

  s = 'Execute(): facility time [min] = ' + str(evolTime)
  self.__log.info(s)

  self.__PlotTimeSeries( evolTime )

#---------------------------------------------------------------------------------
 def __UseData( self, usePortName=None, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( usePortName = usePortName )

# Get data from port files
  if usePortName == 'time-series': self.__GetTimeSeries( portFile, evolTime )

#---------------------------------------------------------------------------------
 def __ProvideData( self, providePortName=None, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( providePortName = providePortName )

# Send data to port files
#  if providePortName == 'fuel-segments': self.__ProvideFuelSegments( portFile, evolTime )

#---------------------------------------------------------------------------------
 def __GetPortFile( self, usePortName=None, providePortName=None ):

  portFile = None

  if usePortName is not None:

    assert providePortName is None

    for port in self.__ports:
     if port[0] == usePortName and port[1] == 'use': portFile = port[2]

    maxNTrials = 50
    nTrials    = 0
    while not os.path.isfile(portFile) and nTrials < maxNTrials:
      nTrials += 1
      time.sleep(1)

    if nTrials >= 10:
      s = '__GetPortFile(): waited ' + str(nTrials) + ' trials for port: ' + portFile
      self.__log.warn(s)

    assert os.path.isfile(portFile) is True, 'portFile %r not available; stop.' % portFile

  if providePortName is not None:

    assert usePortName is None

    for port in self.__ports:
     if port[0] == providePortName and port[1] == 'provide': portFile = port[2]

  assert portFile is not None, 'portFile is invalid.'

  return portFile

#---------------------------------------------------------------------------------
# This uses a use portFile which is guaranteed at this point
 def __GetTimeSeries( self, portFile, evolTime ):
 
  s = '__GetTimeSeries(): will check file: '+portFile
  self.__log.debug(s)

  found = False

  while found is False:

    s = '__GetTimeSeries(): checking for value at '+str(evolTime)
    self.__log.debug(s)

    tree = ElementTree.parse(portFile)

    time.sleep(1) # slow down the PyPlot module; file racing condition
#    ElementTree.dump(tree)

    rootNode = tree.getroot()
    assert rootNode.tag == 'time-series', 'invalid format.'
  
    node = rootNode.find('time')
    timeUnit = node.get('unit').strip()

    # vfda to do: fix this to allow for multiple variables!!!
    node = rootNode.find('var')
    varName = node.get('name').strip() 
    varUnit = node.get('unit').strip() 

    nodes = rootNode.findall('timeStamp')

    for n in nodes:

     timeStamp = float(n.get('value').strip())

     s = '__GetTimeSeries(): timeStamp '+str(timeStamp)
     self.__log.debug(s)
 
     # must check for timeStamp 
     if timeStamp == evolTime:

        found = True  

        if timeStamp == 0.0: self.__timeSeriesData[(varName,varUnit,timeUnit)] = list()

        data = self.__timeSeriesData[(varName,varUnit,timeUnit)]

        varValue = float(n.text.strip())

        data.append( (evolTime, varValue) )

        s = '__GetTimeSeries(): '+varName+' at '+str(evolTime)+' [min]; value ['+varUnit+'] = '+str(varValue)
        self.__log.debug(s)

     else: 

        time.sleep(1)

  return

#---------------------------------------------------------------------------------
 def __PlotTimeSeries( self, evolTime ):

  s = '__PlotVarTimeSeries(): __timeSeriesData keys = '+str(self.__timeSeriesData.keys())
  self.__log.debug(s)

#  x = np.linspace(0, evolTime)
#  line, = plt.plot(x, np.sin(x), '--', linewidth=2)

#  dashes = [10, 5, 100, 5] # 10 points on, 5 off, 100 on, 5 off
#  line.set_dashes(dashes)
#
#  plt.show()

#*********************************************************************************
# Usage: -> python pyplot.py
if __name__ == "__main__":
 print('Unit testing for PyPlot')