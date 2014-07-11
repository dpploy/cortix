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
import matplotlib.gridspec as gridspec
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

  self.__timeSeriesData = dict(list()) # [(varName,varUnit,timeUnit,title,legend)] = (time,varValue)

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

  if evolTime % 60.0 == 0.0: self.__PlotTimeSeries() # updata plot every 10 min

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

#    tree = ElementTree.parse(portFile)

    try:
      tree = ElementTree.parse( portFile )
    except ElementTree.ParseError as error:
      s = '__GetTimeSeries(): '+portFile+' unavailable. Error code: '+str(error.code)+' File position: '+str(error.position)+'. Retrying...'
      self.__log.debug(s)
      continue

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

#      s = '__GetTimeSeries(): timeStamp '+str(timeStamp)
#      self.__log.debug(s)
 
      # must check for timeStamp 
      if timeStamp == evolTime:

         found = True  

         varSpec = (varName,varUnit,timeUnit)

         if timeStamp == 0.0: self.__timeSeriesData[varSpec] = list()

         data = self.__timeSeriesData[varSpec]

         varValue = float(n.text.strip())

         data.append( (evolTime, varValue) )

#        s = '__GetTimeSeries(): '+varName+' at '+str(evolTime)+' [min]; value ['+varUnit+'] = '+str(varValue)
#        self.__log.debug(s)

      # end of if timeStamp == evolTime:

    # end of for n in nodes:

    if found is False: time.sleep(1)

  # while found is False:

  return

#---------------------------------------------------------------------------------
 def __PlotTimeSeries( self ):

#  s = '__PlotVarTimeSeries(): __timeSeriesData keys = '+str(self.__timeSeriesData.keys())
#  self.__log.debug(s)
#  s = '__PlotVarTimeSeries(): __timeSeriesData keys = '+str(self.__timeSeriesData.items())
#  self.__log.debug(s)

  nVariables = len(self.__timeSeriesData.keys())

  assert nVariables <= 9, 'exceeded # of variables'

  fig = plt.figure()

  gs = gridspec.GridSpec(3,3)
  gs.update(left=0.08,right=0.98,wspace=0.4,hspace=0.4)

  axlst = list()
  axlst.append(fig.add_subplot(gs[0, 0]))
  axlst.append(fig.add_subplot(gs[0, 1]))
  axlst.append(fig.add_subplot(gs[0, 2]))
  axlst.append(fig.add_subplot(gs[1, 0]))
  axlst.append(fig.add_subplot(gs[1, 1]))
  axlst.append(fig.add_subplot(gs[1, 2]))
  axlst.append(fig.add_subplot(gs[2, 0]))
  axlst.append(fig.add_subplot(gs[2, 1]))
  axlst.append(fig.add_subplot(gs[2, 2]))
  axes = np.array(axlst)
  axes = np.array(axlst)

  text = 'Cortix::PyPlot Module'
  fig.text(.5,.95,text,horizontalalignment='center',fontsize=16)

  for (varSpec,ax) in zip( self.__timeSeriesData , axes.flat ):

    varName  = varSpec[0]
    varUnit  = varSpec[1]; 

    if varUnit == 'gram': 
       varUnit = 'g'

    timeUnit = varSpec[2]

    data = self.__timeSeriesData[varSpec]
    data = np.array(data)
    x = data[:,0]/60.0
    y = data[:,1]
  
    ax.set_xlabel('Time [h]',fontsize=10)
    ax.set_ylabel(varName+' ['+varUnit+']',fontsize=10)

    ymax  = y.max()
    dy    = ymax * .1
    ymax += dy
    ymin  = y.min()
    ymin -= dy

    ax.set_ylim(ymin,ymax)

#  for l in axis.get_xticklabels(): l.set_fontsize('x-small')
#  for l in axis.get_yticklabels(): l.set_fontsize('x-small')
#  color  = parameters['plot-color']
#  marker = parameters['plot-marker']+'-'
#  axis.set_xlim(2e-3, 2)
#  axis.set_aspect(1)
#  axis.set_title("adjustable = box")
#  legend = parameters['plot-legend']

#  for key,value in self.__timeSeriesData.items():
#   print(key)
#   print(value)

  
    ax.plot( x, y, 's-', color='black', linewidth=0.5, markersize=2,  \
             markeredgecolor='black' )
#              markeredgecolor='black', label='dissolver request' )

# if index == 0:
#    axis.set_xscale("log")
#    axis.set_yscale("log")
#    axis.plot( Q, haloI_fit, marker, color='red', linewidth=0.5, markersize=3, markeredgecolor=color, label=legend )

#    ax.legend( loc='best', prop={'size':8} )

#  fig.show()
 
  # end of for (varSpec,ax) in zip( self.__timeSeriesData , axes.flat ):

  fig.savefig('pyplot.png',dpi=200,fomat='png')
  plt.close('all')

#  fig.savefig(outputfilename+'.png',dpi=200,fomat='png')

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
