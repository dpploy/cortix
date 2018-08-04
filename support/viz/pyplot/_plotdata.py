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


  if facilityTime % self.plotInterval == 0.0 and facilityTime < self.finalTime: 

    s = '_PlotData(): facility time [min] = ' + str(facilityTime)
    self.log.debug(s)

    fromTime = max(0.0, facilityTime-self.plotSlideWindow)
    toTime   = facilityTime

    s = '_PlotData(): fromTime [min] = ' + str(fromTime)
    self.log.debug(s)
    s = '_PlotData(): toTime [min] = ' + str(toTime)
    self.log.debug(s)

    _PlotTimeSeqDashboard(self, fromTime, toTime) #  plot with slide window history

    _PlotTimeTables(self, fromTime, toTime) # plot with slide window history

  elif facilityTime >= self.finalTime: 

    s = '_PlotData(): facility time [min] = ' + str(facilityTime)
    self.log.debug(s)

    _PlotTimeSeqDashboard(self, 0.0, self.finalTime)  # plot all history

    _PlotTimeTables(self, 0.0, self.finalTime) # plot all history

#*********************************************************************************
