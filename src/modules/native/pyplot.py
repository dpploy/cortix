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
from matplotlib.ticker import MultipleLocator
from   src.modules.native.timesequence import TimeSequence
#*********************************************************************************

#*********************************************************************************
class PyPlot(object):

# Private member data
# __slots__ = [

 def __init__( self,
               ports ,
               evolveTime=0.0
             ):

  # Sanity test
  assert type(ports) is list, '-> ports type %r is invalid.' % type(ports)
  assert type(evolveTime) is float, '-> time type %r is invalid.' % type(evolveTime)

  # Logging
  self.__log = logging.getLogger('pyplot')
  self.__log.info('initializing an instance of PyPlot')

  # Member data
  self.__ports = ports

  self.__evolveTime = evolveTime

  self.__timeTablesData = dict(list()) # [(time,timeUnit)] = [column,column,...]

  self.__plotInterval    = 60.0   # minutes  (1 plot update every 60 min)
  self.__plotSlideWindow = 3*60.0 # minutes  (1 plot update every 60 min)
  self.__gramDecimals    = 3      # milligram significant digits

  self.__timeSequences_tmp = list() # temporary storage

#---------------------------------------------------------------------------------
 def CallPorts(self, facilityTime=0.0):

  for port in self.__ports: # this loops over "ALL" use ports!
    if port[1] == 'use':
      self.__UseData( port, evolTime=facilityTime  )
 
#---------------------------------------------------------------------------------
 def Execute( self, facilityTime=0.0 ):

  s = 'Execute(): facility time [min] = ' + str(facilityTime)
  self.__log.info(s)

  if facilityTime % self.__plotInterval == 0.0 and facilityTime < self.__evolveTime: 
    fromTime = max(0.0, facilityTime-self.__plotSlideWindow)
    toTime   = facilityTime

    self.__PlotTimeSeqDashboard(fromTime, toTime) #  plot with slide window history
    self.__PlotTimeTables(fromTime, toTime) # updata plot every 30 min

  elif facilityTime >= self.__evolveTime: 
    self.__PlotTimeSeqDashboard(0.0, self.__evolveTime)  # plot all history
    self.__PlotTimeTables(0.0, self.__evolveTime) # plot all history

#---------------------------------------------------------------------------------
 def __UseData( self, port, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( usePort = port )

# Get data from port files
  if port[0] == 'time-sequence' and evolTime % self.__plotInterval == 0.0: 
    self.__GetTimeSequence( portFile, evolTime )

  if port[0] == 'time-tables' and evolTime % self.__plotInterval == 0.0: 
    self.__GetTimeTables( portFile, evolTime )

#---------------------------------------------------------------------------------
# Nothing planned to provide at this time; but could change
 def __ProvideData( self, port, evolTime=0.0 ):

# Access the port file
#  portFile = self.__GetPortFile( providePort = port )
  return

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
# This uses a use portFile which is guaranteed to exist at this point
 def __GetTimeSequence( self, portFile, evolTime ):

  s = '__GetTimeSequence(): will get data in portfile: '+portFile
  self.__log.debug(s)

  if evolTime >= self.__evolveTime: 
    initialTime = 0.0
  else:
    initialTime = max(0.0,evolTime-self.__plotSlideWindow)

  timeSequence = TimeSequence( portFile, 'xml', initialTime, evolTime, self.__log )

  self.__timeSequences_tmp.append( timeSequence )

  return

#---------------------------------------------------------------------------------
# This uses a use portFile which is guaranteed at this point
 def __GetTimeTables( self, portFile, evolTime ):

  s = '__GetTimeTables(): will check file: ' + portFile
  self.__log.debug(s)

  found = False

  while found is False:

    s = '__GetTimeTables(): checking for value at ' + str(evolTime)
    self.__log.debug(s)

#    tree = ElementTree.parse(portFile)

    try:
      tree = ElementTree.parse( portFile )
    except ElementTree.ParseError as error:
      s = '__GetTimeTables(): '+portFile+' unavailable. Error code: '+str(error.code)+' File position: '+str(error.position)+'. Retrying...'
      self.__log.debug(s)
      time.sleep(1)
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
 def __PlotTimeTables( self, initialTime=0.0, finalTime=0.0 ):

  nTimeSteps = len(self.__timeTablesData.keys())
  if nTimeSteps == 0: return

  s = '__PlotTimeTables(): plotting tables'
  self.__log.debug(s)

#  s = '__PlotTimeTables(): __timeTablesData keys = '+str(self.__timeTablesData.items())
#  self.__log.debug(s)


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

#---------------------------------------------------------------------------------
 def __PlotTimeSeqDashboard( self, initialTime=0.0, finalTime=0.0 ):

  s = '__PlotTimeSeqDashboard(): from: '+str(initialTime)+' to '+str(finalTime)
  self.__log.debug(s)

  nSequences = len(self.__timeSequences_tmp)

  s = '__PlotTimeSeqDashboard(): # of sequences: '+str(nSequences)
  self.__log.debug(s)

  if nSequences == 0: return

  nVar = 0
  for seq in self.__timeSequences_tmp:
    nVar += seq.GetNVariables()

  s = '__PlotTimeSeqDashboard(): # of variables: '+str(nVar)
  self.__log.debug(s)

  # collect all variables in a list for mapping on the dashboards
  variablesData = list()
  for seq in self.__timeSequences_tmp:
    for (spec,values) in seq.GetVariables().items():
      variablesData.append( (spec,values) )
  assert len(variablesData) == nVar

  today = datetime.datetime.today()
  
  # loop over variables and assign to the dashboards  
  iDash = 0
  for iVar in range(nVar):

    if iVar % 9 == 0: # if a multiple of 8 start a new dashboard

      if iVar != 0: # flush any current figure
        figName = 'timeseq-dashboard-'+str(iDash)+'.png'
        fig.savefig(figName,dpi=200,fomat='png')
        plt.close(str(iDash))
        s = '__PlotTimeSeqDashboard(): created plot: '+figName
        self.__log.debug(s)
        iDash += 1
      # end of if iVar != 0: # flush any current figure

      fig = plt.figure(str(iDash))

      gs = gridspec.GridSpec(3,3)
      gs.update( left=0.08,right=0.98,wspace=0.4,hspace=0.4 )

      axlst = list()

      nPlotsNeeded = nVar - iVar 
      count = 0
      for i in range(3):
        for j in range(3):
          axlst.append( fig.add_subplot(gs[i, j]) )
          count += 1
          if count == nPlotsNeeded: break
        if count == nPlotsNeeded: break

      axes = np.array(axlst)

      text = str(today).split('.')[0]+': Cortix.Modules.Native.PyPlot: Time-Sequence Data'
      fig.text(.5,.95,text,horizontalalignment='center',fontsize=14)

      axs = axes.flat
 
      axId = 0

    # end of if iVar % 9 == 0: # if a multiple of 9 start a new dashboard

    (spec,val) = variablesData[iVar]

    ax = axs[axId]
    axId += 1
 
    varName = spec[0]
    varUnit = spec[1]

    if varUnit == 'gram': varUnit = 'g'
    if varUnit == 'gram/min': varUnit = 'g/min'

    timeUnit  = spec[2]
    varLegend = spec[3]
    varScale  = spec[4]
    assert varScale == 'log' or varScale == 'linear'

    if timeUnit == 'minute': timeUnit = 'min'
 
    data = np.array(val)

#      assert len(data.shape) == 2, 'not a 2-column shape: %r in var %r of %r; stop.' % (data.shape,varName,varLegend)
    if len(data.shape) != 2: 
      s = '__PlotTimeSeqDashboard(): bad data; variable: '+varName+' unit: '+varUnit+' legend: '+varLegend+' shape: '+str(data.shape)+' skipping...'
      self.__log.warn(s)
      continue #  simply skip bad data and log

    x = data[:,0]
    if x.max() >= 120.0:
      x /= 60.0
      if timeUnit == 'min': timeUnit = 'h'

    y = data[:,1]
    if y.max() >= 1000.0: 
      y /= 1000.0
      if varUnit == 'gram' or varUnit == 'g': 
        varUnit = 'kg'
      if varUnit == 'gram/min' or varUnit == 'g/min': 
        varUnit = 'kg/min'
    if y.max() <= .1: 
      y *= 1000.0
      if varUnit == 'gram' or varUnit == 'g': 
        varUnit = 'mg'
      if varUnit == 'gram/min' or varUnit == 'g/min': 
        varUnit = 'mg/min'
  
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

    if timeUnit == 'h' and x.max()-x.min() <= 5.0:
      majorLocator = MultipleLocator(1.0)
      minorLocator = MultipleLocator(0.5)

      ax.xaxis.set_major_locator(majorLocator)
      ax.xaxis.set_minor_locator(minorLocator)

    if varScale == 'log' and y.min() > 0.0: ax.set_yscale('log')

    ax.plot( x, y, 's-', color='black', linewidth=0.5, markersize=2,  \
             markeredgecolor='black', label=varLegend )

    ax.legend( loc='best', prop={'size':8} )

    s = '__PlotTimeSeqDashboard(): plotted '+varName+' from '+varLegend
    self.__log.debug(s)

  # end of for iVar in range(nVar):
  figName = 'timeseq-dashboard-'+str(iDash)+'.png'
  fig.savefig(figName,dpi=200,fomat='png')
  plt.close(str(iDash))
  s = '__PlotTimeSeqDashboard(): created plot: '+figName
  self.__log.debug(s)

  self.__timeSequences_tmp = list()

  s = '__PlotTimeSeqDashboard(): done with plotting'
  self.__log.debug(s)

  return

#*********************************************************************************
# Usage: -> python pyplot.py
if __name__ == "__main__":
 print('Unit testing for PyPlot')
