"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

PyPlot module.

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
from   .timesequence import TimeSequence
#*********************************************************************************

#---------------------------------------------------------------------------------
# Constructor

def _PyPlot( self,
             slotId,
             inputFullPathFileName,
             workDir,
             ports=list(),
             startTime  = 0.0,
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
  self.plotSlideWindow = 5*60.0 # minutes  (width of the sliding window)

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

#*********************************************************************************
