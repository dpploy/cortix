# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/...
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/COPYRIGHT
#
# Licensed under the GNU General Public License v. 3, please see LICENSE file.
# https://www.gnu.org/licenses/gpl-3.0.txt
"""
Cortix driver for guest modules.
Module developers must implement the public methods in this driver.
Ideally, this implementation should be minimal.         
Developers should use this class to wrap their module (MyModule) implemented in a
file named my_module.py. This file will be placed inside the developer's module
directory which is pointed to in the Cortix config.xml file.
"""
#*********************************************************************************
import os
import sys
import io
import time
import datetime
import math
import random
import logging

from .my_module import MyModule
#*********************************************************************************

class CortixDriver():
 """
  Cortix driver for guest modules.
 """

 def __init__( self,
               slotId,
               inputFullPathFileName,
               execFullPathFileName,
               workDir,
               ports=list(),
               startTime=0.0,
               finalTime=0.0  
             ):

  # Sanity test
  assert isinstance(slotId, int), '-> slotId type %r is invalid.' % type(slotId)
  assert isinstance(ports, list), '-> ports type %r is invalid.'  % type(ports)
  assert len(ports) > 0
  assert isinstance(startTime,float), '-> time type %r is invalid.' % type(startTime)
  assert isinstance(finalTime, float), '-> time type %r is invalid.' % type(finalTime)

  # Logging
  self.log = logging.getLogger( 'launcher-mymodule'+str(slotId)+'.cortixdriver' )
  self.log.info( 'initializing an object of CortixDriver()' )

  self.my_module = MyModule( slotId, inputFullPathFileName, workDir, ports, 
                             startTime, finalTime )

  return
#---------------------- end def __init__():---------------------------------------

 def call_ports( self, facilityTime=0.0 ):
  """
  Call all ports at facilityTime
  """

  s = '=========================================================='
  self.log.debug(s)
  s = 'CORTIX::DRIVER->***->DRIVER->***->DRIVER->***->DRIVER->***'
  self.log.debug(s)
  s = '=========================================================='
  self.log.debug(s)

  s = 'call_ports('+str(round(facilityTime,2))+'[mytimeunit]):'
  self.log.debug(s)

  startTime = time.time()
 
  self.my_module.call_ports( facilityTime ) 

  endTime = time.time()

  s = 'call_ports('+str(round(facilityTime,2))+'[mytimeunit]): '
  m = 'elapsed time (s): '+str(round(endTime-startTime,2))
  self.log.debug(s+m)

  return
#---------------------- end def call_ports():-------------------------------------

 def execute( self, facilityTime=0.0, timeStep=0.0 ):
  """
  Evolve system from facilityTime to facilityTime + timeStep
  """

  s = '=========================================================='
  self.log.debug(s)
  s = 'CORTIX::DRIVER->***->DRIVER->***->DRIVER->***->DRIVER->***'
  self.log.debug(s)
  s = '=========================================================='
  self.log.debug(s)

  s = 'execute('+str(round(facilityTime,2))+'[mytimeunit]:)'
  self.log.debug(s)

  startTime = time.time()

  self.my_module.execute( facilityTime, timeStep )

  endTime = time.time()

  s = 'execute('+str(round(facilityTime,2))+'[mytimeunit]): '
  m = 'elapsed time (s): '+str(round(endTime-startTime,2))
  self.log.debug(s+m)

  return
#---------------------- end def execute():----------------------------------------

#====================== end class CortixDriver: ==================================
