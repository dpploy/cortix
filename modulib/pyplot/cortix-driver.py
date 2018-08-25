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
Cortix driver for guest module.
Module developers must implement its public methods.

Author: Valmor F. de Almeida dealmeidav@ornl.gov; vfda
Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import logging

from .pyplot  import PyPlot
#*********************************************************************************

class CortixDriver():

 def __init__( self,
               slotId,
               inputFullPathFileName,
               execFullPathFileName,
               workDir,
               ports=list(),
               startTime = 0.0,
               finalTime = 0.0  # evolution time
             ):

  # Sanity test
  assert isinstance(slotId, int), '-> slotId type %r is invalid.' % type(slotId)
  assert isinstance(ports, list), '-> ports type %r is invalid.'  % type(ports)
  assert len(ports) > 0
  assert isinstance(startTime,float), '-> time type %r is invalid.' % type(startTime)
  assert isinstance(finalTime, float), '-> time type %r is invalid.' % type(finalTime)

  # Logging
  self.__log = logging.getLogger('launcher-viz.pyplot_'+str(slotId)+'.cortixdriver')
  self.__log.debug('initializing an object of CortixDriver()' )

  self.__pyplot = PyPlot( slotId, 
                          inputFullPathFileName, 
                          workDir,
                          ports, 
                          startTime, 
                          finalTime )

  return
#---------------------- end def __init__():---------------------------------------

 def call_ports( self, facilityTime=0.0 ):
  """
  Call all ports at facilityTime
  """

  s = 'CallPorts(): facility time [min] = ' + str(facilityTime)
  self.__log.debug(s)
 
  self.__pyplot.call_ports( facilityTime ) 

  return
#---------------------- end def call_ports():-------------------------------------
 
 def execute( self, facilityTime=0.0 , timeStep=0.0 ):
  """
  Evolve system from facilityTime to facilityTime + timeStep
  """

  s = 'Execute(): facility time [min] = ' + str(facilityTime)
  self.__log.debug(s)

  self.__pyplot.execute( facilityTime, timeStep )

  return
#---------------------- end def execute():----------------------------------------

#====================== end class CortixDriver: ==================================
