#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Nitrino module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
from .getportfile   import GetPortFile
from .providesignal import ProvideSignal
from .providevapor  import ProvideVapor
from .providestate  import ProvideState
#*********************************************************************************

def ProvideData( self, providePortName=None, atTime=0.0 ):

# Access the port file
  portFile = GetPortFile( self, providePortName = providePortName )

# Send data to port files
  if providePortName == 'signal' and portFile is not None: 
    ProvideSignal( self, portFile, atTime )

  if providePortName == 'vapor' and portFile is not None: 
    ProvideVapor( self, portFile, atTime )

  if providePortName == 'state' and portFile is not None: 
    ProvideState( self, portFile, atTime )

#*********************************************************************************
