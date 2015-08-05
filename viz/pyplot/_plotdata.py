"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Pyplot module.

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime

from ._plottimeseqdashboard import _PlotTimeSeqDashboard
from ._plottimetables       import _PlotTimeTables
#*********************************************************************************

#---------------------------------------------------------------------------------
def _PlotData( self, facilityTime=0.0 , timeStep=0.0):

  s = '_PlotData(): facility time [min] = ' + str(facilityTime)
  self.log.info(s)

  if facilityTime % self.plotInterval == 0.0 and facilityTime < self.evolveTime: 

    fromTime = max(0.0, facilityTime-self.plotSlideWindow)
    toTime   = facilityTime

    _PlotTimeSeqDashboard(self, fromTime, toTime) #  plot with slide window history

    _PlotTimeTables(self, fromTime, toTime) # plot with slide window history

  elif facilityTime >= self.evolveTime: 

    _PlotTimeSeqDashboard(self, 0.0, self.evolveTime)  # plot all history

    _PlotTimeTables(self, 0.0, self.evolveTime) # plot all history

#*********************************************************************************
