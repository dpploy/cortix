#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Nitrino module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
from .getportfile   import GetPortFile
from .getsolids     import GetSolids
from .getcondensate import GetCondensate
#*********************************************************************************

#---------------------------------------------------------------------------------
def UseData( self, usePortName=None, atTime=0.0 ):

# Access the port file
  portFile = GetPortFile( self, usePortName = usePortName )

# Get data from port files
  if usePortName == 'solids': 

     if self.ready2LoadFuel is True:
        tmp = GetSolids( self, portFile, atTime )
        if tmp is not None:  # if fuel load was successful
          self.fuelSegments = tmp
          self.ready2LoadFuel         = False
          self.dissolutionStartedTime = atTime

  if usePortName == 'condensate': GetCondensate( self, portFile, atTime )

#*********************************************************************************
