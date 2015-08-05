"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

PyPlot module.

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
from   .timesequence import TimeSequence
#*********************************************************************************

#---------------------------------------------------------------------------------
# This uses a use portFile which is guaranteed to exist at this point

def _GetTimeSequence( self, portFile, atTime ):

  s = '_GetTimeSequence(): will get data in portfile: '+portFile
  self.log.debug(s)

  if atTime >= self.evolveTime: 
    initialTime = 0.0
  else:
    initialTime = max( 0.0, atTime-self.plotSlideWindow )

  timeSequence = TimeSequence( portFile, 'xml', initialTime, atTime, self.log )

  self.timeSequences_tmp.append( timeSequence )

  return

#*********************************************************************************
