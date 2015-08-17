#!/usr/bin/env python
"""
Author: Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix driver for guest module.
Module developer must implement its public methods.

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import logging

from .pyplot  import PyPlot
#*********************************************************************************

#*********************************************************************************
class CortixDriver():

 def __init__( self,
               slotId,
               inputFullPathFileName,
               execFullPathFileName,
               workDir,
               ports=list(),
               evolveTime=0.0  # total evolution time
             ):

  # Sanity test
  assert type(slotId) is int, '-> slotId type %r is invalid.' % type(slotId)
  assert type(ports)  is list, '-> ports type %r is invalid.' % type(ports)
  assert len(ports) > 0
  assert type(evolveTime) is float, '-> time type %r is invalid.' % type(evolveTime)

  # Logging
  self.__log = logging.getLogger('launcher-viz.pyplot_'+str(slotId)+'.cortixdriver.pyplot')
  self.__log.debug('initializing an object of CortixDriver()' )

  self.__pyPlot = PyPlot( slotId, 
                          inputFullPathFileName, 
                          workDir,
                          ports, 
                          evolveTime )

  return

#---------------------------------------------------------------------------------
# Call all ports at facilityTime

 def CallPorts( self, facilityTime=0.0 ):

  s = 'CallPorts(): facility time [min] = ' + str(facilityTime)
  self.__log.debug(s)
 
  self.__pyPlot.CallPorts( facilityTime ) 

  return
 
#---------------------------------------------------------------------------------
# Evolve system from facilityTime to facilityTime + timeStep

 def Execute( self, facilityTime=0.0 , timeStep=0.0 ):

  s = 'Execute(): facility time [min] = ' + str(facilityTime)
  self.__log.debug(s)

  self.__pyPlot.Execute( facilityTime, timeStep )

  return

#*********************************************************************************
# Usage: -> python cortix-driver.py
if __name__ == "__main__":
 print('Unit testing for CortixDriver')
