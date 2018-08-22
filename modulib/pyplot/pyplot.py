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
Author: Valmor F. de Almeida dealmeidav@ornl.gov; vfda

PyPlot module.

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime

# constructor helper
from ._pyplot import _PyPlot

# internal methods
from ._getportfile import _GetPortFile

from ._gettimesequence import _GetTimeSequence
from ._gettimetables   import _GetTimeTables
from ._plotdata        import _PlotData
#*********************************************************************************

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

  # Constructor
  _PyPlot( self, slotId, inputFullPathFileName, workDir, ports, startTime, finalTime )

#---------------------------------------------------------------------------------
# Transfer data at facilityTime

 def CallPorts( self, facilityTime=0.0 ):

  if (facilityTime % self.plotInterval == 0.0 and \
      facilityTime < self.finalTime) or facilityTime >= self.finalTime : 

    # use ports in PyPlot have infinite multiplicity (implement multiplicity later)
    assert len(self.timeSequences_tmp) == 0
    for port in self.ports:
      (portName,portType,thisPortFile) = port
      if portType == 'use':
         assert portName == 'time-sequence' or portName == 'time-tables' or \
                portName == 'time-sequence-input'
         self.__UseData( usePortName=portName, usePortFile=thisPortFile, atTime=facilityTime  )

#---------------------------------------------------------------------------------
 def Execute( self, facilityTime=0.0 , timeStep=0.0 ):

   s = 'Execute(): facility time [min] = ' + str(round(facilityTime,3))
   self.log.debug(s)

   _PlotData( self, facilityTime, timeStep )

#---------------------------------------------------------------------------------
# This operates on a given use port;
 def __UseData( self, usePortName=None, usePortFile=None, atTime=0.0 ):

  if (atTime % self.plotInterval == 0.0 and atTime < self.finalTime) or \
      atTime >= self.finalTime :

# Access the port file
    portFile = _GetPortFile( self, usePortName = usePortName, usePortFile=usePortFile )

# Get data from port files
    if usePortName == 'time-sequence' or usePortName == 'time-sequence-input' and \
       portFile is not None:
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
