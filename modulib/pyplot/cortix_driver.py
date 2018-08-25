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

from .pyplot import PyPlot
#*********************************************************************************

class CortixDriver():

 def __init__( self,
               slot_id,
               input_full_path_file_name,
               exec_full_path_file_name,
               work_dir,
               ports=list(),
               cortix_start_time = 0.0,
               cortix_final_time = 0.0  # evolution time
             ):

  # Sanity test
  assert isinstance(slot_id, int), '-> slot_id type %r is invalid.' % type(slot_id)
  assert isinstance(ports, list), '-> ports type %r is invalid.'  % type(ports)
  assert len(ports) > 0
  assert isinstance(cortix_start_time,float), '-> time type %r is invalid.' % type(cortix_start_time)
  assert isinstance(cortix_final_time, float), '-> time type %r is invalid.' % type(cortix_final_time)

  # Logging
  self.__log = logging.getLogger('launcher-viz.pyplot_'+str(slot_id)+'.cortixdriver')
  self.__log.debug('initializing an object of CortixDriver()' )

  self.__pyplot = PyPlot( slot_id, 
                          input_full_path_file_name, 
                          work_dir,
                          ports, 
                          cortix_start_time, 
                          cortix_final_time )

  self.time_stamp = None # temporary

  return
#---------------------- end def __init__():---------------------------------------

 def call_ports( self, cortix_time=0.0 ):
  """
  Call all ports at cortix_time
  """

  self.__log_debug(cortix_time, 'call_ports')

  self.__pyplot.call_ports( cortix_time ) 

  self.__log_debug(cortix_time, 'call_ports')

  return
#---------------------- end def call_ports():-------------------------------------
 
 def execute( self, cortix_time=0.0 , time_step=0.0 ):
  """
  Evolve system from cortix_time to cortix_time + time_step
  """

  self.__log_debug(cortix_time, 'execute')

  self.__pyplot.execute( cortix_time, time_step )

  self.__log_debug(cortix_time, 'execute')

  return
#---------------------- end def execute():----------------------------------------

 def __log_debug(self, cortix_time=0.0, caller='null-function-name'):

   if self.time_stamp == None:
       s = ''
       self.__log.debug(s)
       s = '=========================================================='
       self.__log.debug(s)
       s = 'CORTIX::DRIVER->***->DRIVER->***->DRIVER->***->DRIVER->***'
       self.__log.debug(s)
       s = '=========================================================='
       self.__log.debug(s)
 
       s = caller+'('+str(round(cortix_time,2))+'[min]):'
       self.__log.debug(s)
 
       self.time_stamp = time.time()
 
   else:
 
       end_time = time.time()
 
       s = caller+'('+str(round(cortix_time,2))+'[min]): '
       m = 'elapsed time (s): '+str(round(end_time-self.time_stamp,2))
       self.__log.debug(s+m)
 
       self.time_stamp = None
 
   return
#---------------------- end def __log_debug():------------------------------------

#====================== end class CortixDriver: ==================================
