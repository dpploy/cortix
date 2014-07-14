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

  self.__timeSeriesData = dict(list()) # [(varName,varUnit,timeUnit,title,legend)] = [(time,varValue),(time,varValue),...]

  self.__timeTablesData = dict(list()) # [(time,timeUnit)] = [column,column,...]

  self.__log = logging.getLogger('pyplot')
  self.__log.info('initializing an instance of PyPlot')

  self.__gramDecimals = 3 # milligram significant digits

#---------------------------------------------------------------------------------
 def CallPorts(self, evolTime=0.0):

  for port in self.__ports:
    if port[1] == 'use':
      self.__UseData( port, evolTime=evolTime  )
 
#---------------------------------------------------------------------------------
 def Execute( self, evolTime=0.0, timeStep=1.0 ):

  s = 'Execute(): facility time [min] = ' + str(evolTime)
  self.__log.info(s)

  if evolTime % 30.0 == 0.0 and evolTime != 0.0 : 
    self.__PlotTimeSeries() # updata plot every 30 min

  if evolTime % 30.0 == 0.0 and evolTime != 0.0 : 
    self.__PlotTimeTables() # updata plot every 30 min

#---------------------------------------------------------------------------------
 def __UseData( self, port, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( usePort = port )

# Get data from port files
  if port[0] == 'time-series': self.__GetTimeSeries( portFile, evolTime )

  if port[0] == 'time-tables': self.__GetTimeTables( portFile, evolTime )

#---------------------------------------------------------------------------------
 def __ProvideData( self, port, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( providePortName = providePortName )

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

    timeCutOff = node.get('cut-off')
    if timeCutOff is not None: 
      timeCutOff = float(timeCutOff.strip())
      if evolTime > timeCutOff: return

    # vfda to do: fix this to allow for multiple variables!!!
    node = rootNode.find('var')
    varName = node.get('name').strip() 
    varUnit = node.get('unit').strip() 
    varLegend = node.get('legend').strip() 

    nodes = rootNode.findall('timeStamp')

    for n in nodes:

      timeStamp = float(n.get('value').strip())

#      s = '__GetTimeSeries(): timeStamp '+str(timeStamp)
#      self.__log.debug(s)
 
      # must check for timeStamp 
      if timeStamp == evolTime:

         found = True  

         varSpec = (varName,varUnit,timeUnit,varLegend)

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
# This uses a use portFile which is guaranteed at this point
 def __GetTimeTables( self, portFile, evolTime ):

  s = '__GetTimeTables(): will check file: '+portFile
  self.__log.debug(s)

  found = False

  while found is False:

    s = '__GetTimeTables(): checking for value at '+str(evolTime)
    self.__log.debug(s)

#    tree = ElementTree.parse(portFile)

    try:
      tree = ElementTree.parse( portFile )
    except ElementTree.ParseError as error:
      s = '__GetTimeTables(): '+portFile+' unavailable. Error code: '+str(error.code)+' File position: '+str(error.position)+'. Retrying...'
      self.__log.debug(s)
      continue

    rootNode = tree.getroot()
    assert rootNode.tag == 'time-tables', 'invalid format.'
  
    timeNodes = rootNode.findall('timeStamp')

    for timeNode in timeNodes:

      timeStamp = float(timeNode.get('value').strip())

      if timeStamp == evolTime:

        found = True  

        timeUnit = timeNode.get('unit').strip()

        self.__timeTablesData[(timeStamp,timeUnit)] = list()

        columns = timeNode.findall('column')

        data = list()

        for col in columns: data.append( col )

        self.__timeTablesData[(timeStamp,timeUnit)] = data

        s = '__GetTimeTables(): added '+str(len(data))+' columns of data'
        self.__log.debug(s)

      # end of if timeStamp == evolTime:

    # end of for timeNode in timeNodes:

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

  fig = plt.figure('time-series')

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

  text = 'Cortix.Modules.Native.PyPlot: Time-Sequence Data'
  fig.text(.5,.95,text,horizontalalignment='center',fontsize=16)

  for (varSpec,ax) in zip( self.__timeSeriesData , axes.flat ):

    varName  = varSpec[0]
    varUnit  = varSpec[1]; 

    if varUnit == 'gram': varUnit = 'g'

    timeUnit = varSpec[2]
    varLegend = varSpec[3]

    if timeUnit == 'minute': timeUnit = 'm'

    data = self.__timeSeriesData[varSpec]
    data = np.array(data)

    x = data[:,0]
    if x.max() >= 120.0:
      x /= 60.0
      if timeUnit == 'm': timeUnit = 'h'

    y = data[:,1]
    if y.max() >= 1000.0: 
      y /= 1000.0
      if varUnit == 'gram' or varUnit == 'g': 
        varUnit = 'kg'
    if y.max() <= .1: 
      y *= 1000.0
      if varUnit == 'gram' or varUnit == 'g': 
        varUnit = 'mg'
  
    ax.set_xlabel('Time ['+timeUnit+']',fontsize=10)
    ax.set_ylabel(varName+' ['+varUnit+']',fontsize=10)

    ymax  = y.max()
    dy    = ymax * .1
    ymax += dy
    ymin  = y.min()
    ymin -= dy

    ax.set_ylim(ymin,ymax)

    for l in ax.get_xticklabels(): l.set_fontsize(10)
    for l in ax.get_yticklabels(): l.set_fontsize(10)
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
             markeredgecolor='black', label=varLegend )
#              markeredgecolor='black', label='dissolver request' )

# if index == 0:
#    axis.set_xscale("log")
#    axis.set_yscale("log")

    ax.legend( loc='best', prop={'size':8} )

  # end of for (varSpec,ax) in zip( self.__timeSeriesData , axes.flat ):

  fig.savefig('pyplot-timeseries.png',dpi=200,fomat='png')
  plt.close('time-series')

#---------------------------------------------------------------------------------
 def __PlotTimeTables( self ):

  s = '__PlotVarTimeTables(): plotting tables'
  self.__log.debug(s)

#  s = '__PlotVarTimeTables(): __timeTablesData keys = '+str(self.__timeSeriesData.keys())
#  self.__log.debug(s)

#  s = '__PlotVarTimeTables(): __timeTablesData keys = '+str(self.__timeTablesData.items())
#  self.__log.debug(s)

  nTimeSteps = len(self.__timeTablesData.keys())

#  assert nVariables <= 9, 'exceeded # of variables'

  fig = plt.figure('time-tables')

  gs = gridspec.GridSpec(2,2)
  gs.update(left=0.1,right=0.98,wspace=0.4,hspace=0.4)

  axlst = list()
  axlst.append(fig.add_subplot(gs[0, 0]))
  axlst.append(fig.add_subplot(gs[0, 1]))
  axlst.append(fig.add_subplot(gs[1, 0]))
  axlst.append(fig.add_subplot(gs[1, 1]))
  axes = np.array(axlst)

  text = 'Cortix.Modules.Native.PyPlot: Time-Tables Data'
  fig.text(.5,.95,text,horizontalalignment='center',fontsize=16)

  for (key,val) in self.__timeTablesData.items():
    (timeStamp,timeUnit) = key
    columns              = val

    if timeStamp == 0.0: continue

    distance = columns[0]
    xLabel = distance.get('name').strip()
    xUnit  = distance.get('unit').strip()
    x = distance.text.strip().split(',')
    for i in range(len(x)): x[i] = float(x[i])
    x = np.array(x)
 
    for k in range(len(columns)-1):

      ax = axes.flat[k]

      y = columns[k+1]
      yLabel = y.get('name').strip()
      yUnit  = y.get('unit').strip()
      yLegend= y.get('legend').strip()
      y = y.text.strip().split(',')
      for i in range(len(y)): 
          y[i] = float(y[i])
      y = np.array(y)
 
      if k == 0 or k == 1: 
        y *= 1000.0
        yUnit = 'm'


#    x = data[:,0]
#    if x.max() >= 120.0:
#      x /= 60.0
#      if timeUnit == 'm': timeUnit = 'h'

#    y = data[:,1]
#    if y.max() >= 1000.0: 
#      y /= 1000.0
#      if varUnit == 'gram' or varUnit == 'g': 
#        varUnit = 'kg'
#    if y.max() <= .1: 
#      y *= 1000.0
#      if varUnit == 'gram' or varUnit == 'g': 
#        varUnit = 'mg'
  
      ax.set_xlabel(xLabel+' ['+xUnit+']',fontsize=10)
      ax.set_ylabel(yLabel+' ['+yUnit+']',fontsize=10)

#    ymax  = y.max()
#    dy    = ymax * .1
#    ymax += dy
#    ymin  = y.min()
#    ymin -= dy

#    ax.set_ylim(ymin,ymax)

      for l in ax.get_xticklabels(): l.set_fontsize(10)
      for l in ax.get_yticklabels(): l.set_fontsize(10)
#  color  = parameters['plot-color']
#  marker = parameters['plot-marker']+'-'
#  axis.set_xlim(2e-3, 2)
#  axis.set_aspect(1)
#  axis.set_title("adjustable = box")

      ax.plot( x, y, 's-', color='black', linewidth=0.5, markersize=2,  \
             markeredgecolor='black', label=yLegend )

      if k == 2 or k == 3: ax.set_yscale("log")


#      ax.legend( loc='best', prop={'size':8} )

  # end of for (varSpec,ax) in zip( self.__timeSeriesData , axes.flat ):

  fig.savefig('pyplot-timetables.png',dpi=200,fomat='png')
  plt.close('time-tables')

#*********************************************************************************
# Usage: -> python pyplot.py
if __name__ == "__main__":
 print('Unit testing for PyPlot')
