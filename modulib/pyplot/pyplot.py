# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/cortix
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/cortix/blob/master/COPYRIGHT.txt
#
# Licensed under the GNU General Public License v. 3, please see LICENSE file.
# https://www.gnu.org/licenses/gpl-3.0.txt
"""
PyPlot module.

Author: Valmor F. de Almeida dealmeidav@ornl.gov; vfda
Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import logging
import xml.etree.ElementTree as ElementTree
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator

import xml.etree.ElementTree as ElementTree
from threading import Lock

from ._plot_time_seq_dashboard import _plot_time_seq_dashboard
from ._plot_time_tables     import _plot_time_tables

# internal methods
from   .time_sequence import TimeSequence
#*********************************************************************************

# vfda: REVISE ME for multiple use port
class PyPlot():

 def __init__( self,
               slotId,
               inputFullPathFileName,
               workDir,
               ports = list(),
               startTime = 0.0,
               finalTime = 0.0  
             ):

  # Sanity test
  assert type(slotId) is int, '-> slotId type %r is invalid.' % type(slotId)
  assert type(ports) is list, '-> ports type %r is invalid.' % type(ports)
  assert ports is not None, 'fatal.'
  assert type(startTime) is float, '-> time type %r is invalid.' % type(startTime)
  assert type(finalTime) is float, '-> time type %r is invalid.' % type(finalTime)

  # Logger
  self.log = logging.getLogger('launcher-viz.pyplot_'+str(slotId)+'.cortixdriver.pyplot')
  self.log.info('initializing an object of PyPlot()' )

  # Member data
  self.slotId = slotId
  self.ports  = ports

  self.startTime  = startTime
  self.finalTime = finalTime

  self.plotInterval    = 60.0   # minutes  (1 plot update every 60 min)
#  self.plotInterval    = 5.0   # minutes  (1 plot update every 60 min)
  self.plotSlideWindow = 5*60.0 # minutes  (width of the sliding window)
#  self.plotSlideWindow = 6*60.0 # minutes  (width of the sliding window)

  # This holds all time sequences, potentially, one per use port. One time sequence
  # has all the data for one port connection.
  self.timeSequences_tmp = list() # temporary storage

  # tables in xml format
  self.timeTablesData = dict(list()) # [(time,timeUnit)] = [column,column,...]

#.................................................................................
# Input ports (if any)

  fin = open(inputFullPathFileName,'r')
  inputDataFullPathFileNames = list()
  for line in fin:
   inputDataFullPathFileNames.append(line.strip())
  fin.close()

  if len(inputDataFullPathFileNames) == 0: return

  found = False
  for (portName,portType,portFile) in ports: 
    if portName == 'time-sequence-input': # this is the use port connected to the input port
      s = 'cp -f ' + inputDataFullPathFileNames[0] + ' ' + portFile
      os.system(s)
      self.log.debug(s)
      found = True

  if found is True:
     s = 'found time-sequence-input file.'
  else:
     s = 'did not find time-sequence-input file.'

  self.log.warn(s)
#---------------------- end def __init__():---------------------------------------

 def call_ports( self, facilityTime=0.0 ):
  """
  Transfer data at facilityTime
  """

  if (facilityTime % self.plotInterval == 0.0 and \
      facilityTime < self.finalTime) or facilityTime >= self.finalTime : 

    # use ports in PyPlot have infinite multiplicity (implement multiplicity later)
    assert len(self.timeSequences_tmp) == 0
    for port in self.ports:
      (portName,portType,thisPortFile) = port
      if portType == 'use':
         assert portName == 'time-sequence' or portName == 'time-tables' or \
                portName == 'time-sequence-input'
         self.__use_data( usePortName=portName, usePortFile=thisPortFile, atTime=facilityTime  )
#---------------------- end def call_ports():-------------------------------------

 def execute( self, facilityTime=0.0 , timeStep=0.0 ):

   s = 'execute(): facility time [min] = ' + str(round(facilityTime,3))
   self.log.debug(s)

   self.__plot_data( facilityTime, timeStep )
#---------------------- end def execute():----------------------------------------

#*********************************************************************************
# Private helper functions (internal use: __)

 def __use_data( self, usePortName=None, usePortFile=None, atTime=0.0 ):
  """
  This operates on a given use port;
  """

  if (atTime % self.plotInterval == 0.0 and atTime < self.finalTime) or \
      atTime >= self.finalTime :

# Access the port file
    portFile = self.__get_port_file( usePortName = usePortName, usePortFile=usePortFile )

# Get data from port files
    if usePortName == 'time-sequence' or usePortName == 'time-sequence-input' and \
       portFile is not None:
       self.__get_time_sequence( portFile, atTime )

    if usePortName == 'time-tables' and portFile is not None:
       _GetTimeTables( self, portFile, atTime )

  return
#---------------------- end def __use_data():-------------------------------------

 def __provide_data( self, providePortName=None, atTime=0.0 ):
  """
  Nothing planned to provide at this time; but could change
  """

  return
#---------------------- end def __provide_data():---------------------------------

 def __get_port_file( self, usePortName=None, usePortFile=None, providePortName=None ):

  portFile = None

  #..........
  # Use ports
  #..........
  if usePortName is not None:

    assert providePortName is None

    for port in self.ports:
      (portName,portType,thisPortFile) = port
      if portName == usePortName and portType == 'use' and thisPortFile == usePortFile: portFile = thisPortFile

    if portFile is None: return None

    maxNTrials = 50
    nTrials    = 0
    while os.path.isfile(portFile) is False and nTrials <= maxNTrials:
      nTrials += 1
      time.sleep(0.1)

    if nTrials >= 10:
      s = '__get_port_file(): waited ' + str(nTrials) + ' trials for port: ' + portFile
      self.log.warn(s)

    assert os.path.isfile(portFile) is True, 'portFile %r not available; stop.' % portFile

  #..............
  # Provide ports
  #..............
  if providePortName is not None:

    assert usePortName is None

    for port in self.ports:
      (portName,portType,thisPortFile) = port
      if portName == providePortName and portType == 'provide': portFile = thisPortFile

  return portFile
#---------------------- end def __get_port_file():--------------------------------

 def __plot_data( self, facilityTime=0.0 , timeStep=0.0):

  if facilityTime % self.plotInterval == 0.0 and facilityTime < self.finalTime: 

    s = '__plot_data(): facility time [min] = ' + str(facilityTime)
    self.log.debug(s)

    fromTime = max(0.0, facilityTime-self.plotSlideWindow)
    toTime   = facilityTime

    s = '__plot_data(): fromTime [min] = ' + str(fromTime)
    self.log.debug(s)
    s = '__plot_data(): toTime [min] = ' + str(toTime)
    self.log.debug(s)

    _plot_time_seq_dashboard(self, fromTime, toTime) #  plot with slide window history

    _plot_time_tables(self, fromTime, toTime) # plot with slide window history

  elif facilityTime >= self.finalTime: 

    s = '__plot_data(): facility time [min] = ' + str(facilityTime)
    self.log.debug(s)

    _plot_time_seq_dashboard(self, 0.0, self.finalTime)  # plot all history

    _plot_time_tables(self, 0.0, self.finalTime) # plot all history
#---------------------- end def __plot_data():------------------------------------

 def __get_time_sequence( self, portFile, atTime ):
  """
  This uses a use portFile which is guaranteed to exist at this point
  """

  s = '__get_time_sequence(): will get data in portfile: '+portFile
  self.log.debug(s)

  if atTime >= self.finalTime: 
    initialTime = self.startTime
  else:
    initialTime = max( self.startTime, atTime - self.plotSlideWindow )

  timeSequence = TimeSequence( portFile, 'xml', initialTime, atTime, self.log )

  self.timeSequences_tmp.append( timeSequence )

  s = '__get_time_sequence(): loaded ' + timeSequence.get_name()
  self.log.debug(s)

  return
#---------------------- end def __get_time_sequence():----------------------------

 def __get_time_tables( self, portFile, atTime ):
  """
  This uses a use portFile which is guaranteed at this point
  """

  s = '__get_time_tables(): will check file: ' + portFile
  self.log.debug(s)

  found = False

  while found is False:

    s = '__get_time_tables(): checking for value at ' + str(atTime)
    self.log.debug(s)

#    tree = ElementTree.parse(portFile)

    try:
      mutex = Lock()
      mutex.acquire()
      tree = ElementTree.parse( portFile )
    except ElementTree.ParseError as error:
      mutex.release()
      s = '__get_time_tables(): '+portFile+' unavailable. Error code: '+str(error.code)+' File position: '+str(error.position)+'. Retrying...'
      self.log.debug(s)
      time.sleep(0.1)
      continue

    mutex.release()
    rootNode = tree.getroot()
    assert rootNode.tag == 'time-tables', 'invalid format.'
  
    timeNodes = rootNode.findall('timeStamp')

    for timeNode in timeNodes:

      timeStamp = float(timeNode.get('value').strip())

      if timeStamp == atTime:

        found = True  

        timeUnit = timeNode.get('unit').strip()

        self.timeTablesData[ (timeStamp,timeUnit) ] = list()

        columns = timeNode.findall('column')

        data = list()

        for col in columns: 
            data.append( col )

        self.timeTablesData[ (timeStamp,timeUnit) ] = data

        s = '__get_time_tables(): added '+str(len(data))+' columns of data'
        self.log.debug(s)

      # end of if timeStamp == atTime:

    # end of for timeNode in timeNodes:

    if found is False: time.sleep(0.1)

  # while found is False:

  return
#---------------------- end def __get_time_tables():------------------------------


#====================== end class PyPlot: ========================================
