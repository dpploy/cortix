#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

PyPlot module.

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime

# constructor helper
from ._pyplot import _PyPlot

from ._getportfile import _GetPortFile

from ._gettimesequence import _GetTimeSequence
from ._gettimetables  import _GetTimeTables
from ._plotdata import _PlotData
#*********************************************************************************

#*********************************************************************************
class PyPlot():

 def __init__( self,
               slotId,
               inputFullPathFileName,
               ports = list(),
               evolveTime = 0.0  # total evolution time
             ):

  # Constructor
  _PyPlot( self, slotId, inputFullPathFileName, ports, evolveTime )

#---------------------------------------------------------------------------------
# Transfer data at facilityTime

 def CallPorts( self, facilityTime=0.0 ):

   self.__UseData( usePortName='time-sequence', atTime=facilityTime )
   self.__UseData( usePortName='time-tables', atTime=facilityTime )
 
#---------------------------------------------------------------------------------
 def Execute( self, facilityTime=0.0 , timeStep=0.0 ):

   s = 'Execute(): facility time [min] = ' + str(facilityTime)
   self.log.info(s)

   _PlotData( self, facilityTime, timeStep )

#---------------------------------------------------------------------------------
 def __UseData( self, usePortName=None, atTime=0.0 ):

  if atTime % self.plotInterval != 0.0: return

# Access the port file
  portFile = _GetPortFile( self, usePortName = usePortName )

# Get data from port files
  if usePortName == 'time-sequence' and portFile is not None:
     _GetTimeSequence( self, portFile, atTime )

  if usePortName == 'time-tables' and portFile is not None:
     _GetTimeTables( self, portFile, atTime )

  return

#---------------------------------------------------------------------------------
# Nothing planned to provide at this time; but could change
 def __ProvideData( self, providePortName=None, atTime=0.0 ):

  return

#*********************************************************************************
# Usage: -> python pyplot.py
if __name__ == "__main__":
 print('Unit testing for PyPlot')
