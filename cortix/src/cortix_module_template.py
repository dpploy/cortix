#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/cortix/blob/master/COPYRIGHT.txt
#
# Licensed under the University of Massachusetts Lowell LICENSE:
# https://github.com/dpploy/cortix/blob/master/LICENSE.txt
'''
Simple MyModule module template for developers.
'''
#*********************************************************************************
import os, sys, io, time
import logging
#*********************************************************************************

class MyModule():
 r'''
  MyModule template for Cortix.
 '''

 def __init__( self,
               slot_id,
               input_full_path_file_name,
               manifesto_full_path_file_name,
               work_dir,
               ports = list(),
               cortix_start_time = 0.0,
               cortix_final_time = 0.0,
               cortix_time_step = 0.0,
               cortix_time_unit = None 
             ):

#.................................................................................
# Sanity test

  assert isinstance(slot_id, int), '-> slot_id type %r is invalid.' % type(slot_id)
  assert isinstance(ports, list), '-> ports type %r is invalid.'  % type(ports)
  assert len(ports) > 0
  assert isinstance(cortix_start_time,float), '-> time type %r is invalid.' % \
          type(cortix_start_time)
  assert isinstance(cortix_final_time, float), '-> time type %r is invalid.' % \
          type(cortix_final_time)
  assert isinstance(cortix_time_step, float), '-> time step type %r is invalid.' % \
          type(cortix_time_step)
  assert isinstance(cortix_time_unit, str), '-> time unit type %r is invalid.' % \
          type(cortix_time_unit)
        # Read the manisfest 
        self.__read_manifesto( manifesto_full_path_file_name )
        self.__log.info(self.__port_diagram)

  # Logging
  self.__log = logging.getLogger('launcher-mymodule_'+str(slot_id)+'.cortix_driver.mymodule')
  self.__log.info('initializing an object of MyModule()')

  # Read the manisfesto
  self.__read_manifesto( manifesto_full_path_file_name )
  self.__log.info(self.__port_diagram)

#.................................................................................
# Member data 

  self.__slot_id = slot_id
  self.__ports  = ports

  if work_dir[-1] != '/': work_dir = work_dir + '/'
  self.__wrkDir = work_dir

  # Signal to start operation
  self.__goSignal = True    # start operation immediately
  for port in self.__ports: # if there is a signal port, start operation accordingly
      (portName,portType,thisPortFile) = port
      if portName == 'go-signal' and portType == 'use': self.__goSignal = False

  self.__setup_time = 1.0  # min; a delay time before starting to run

#.................................................................................
# Input ports
# Read input information if any

  #fin = open(input_full_path_file_name,'r')

#---------------------- end def __init__():---------------------------------------

 def call_ports( self, cortix_time=0.0 ):
  '''
  Developer must implement this method.
  Transfer data at cortix_time
  '''

  # provide data using the 'provide-port-name' of the module
  #self.__provide_data( provide_port_name='provide-port-name', at_time=cortix_time )

  # use data using the 'use-port-name' of the module
  #self.__use_data( use_port_name='use-port-name', at_time=cortix_time )

  return
#---------------------- end def call_ports():---------------------------------------

 def execute( self, cortix_time=0.0, cortix_time_step=0.0 ):
  '''
  Developer must implement this method.
  Evolve system from cortix_time to cortix_time + cortix_time_step
  '''

  s = 'execute('+str(round(cortix_time,2))+'[min]): '
  self.__log.debug(s)

  # Developer implements helper method, for example
  #self.__evolve( self, cortix_time, cortix_time_step ):

  return
#---------------------- end def execute():----------------------------------------

#*********************************************************************************
# Private helper functions (internal use: __)

 def __provide_data( self, provide_port_name=None, at_time=0.0 ):
  '''
  Example of how this internal method would look like
  '''

# Access the port file
  port_file = self.__get_port_file( provide_port_name = provide_port_name )

# Provide data to port files
  #if provide_port_name == 'provide-port-name' and port_file is not None: 
  #   self.__provide_mymodule_method( port_file, at_time )

  return
#---------------------- end def __provide_data():---------------------------------

 def __use_data( self, use_port_name=None, at_time=0.0 ):
  '''
  Example of how this internal method would look like
  '''

# Access the port file
  port_file = self.__get_port_file( use_port_name = use_port_name )
 
# Use data from port file
  #if use_port_name == 'use-port-name' and port_file is not None:  
  #   self.__use_mymodule_method( port_file, at_time )

  return
#---------------------- end def __use_data():-------------------------------------

 def __get_port_file( self, use_port_name=None, provide_port_name=None ):
   '''
   This may return a None port_file
   '''

   port_file = None

   #..........
   # Use ports
   #..........
   if use_port_name is not None:

     assert provide_port_name is None

     for port in self.__ports:
       (portName,portType,thisPortFile) = port
       if portName == use_port_name and portType == 'use': port_file = thisPortFile

     if port_file is None: return None

     max_n_trials = 50
     n_trials     = 0
     while os.path.isfile(port_file) is False and n_trials <= max_n_trials:
       n_trials += 1
       time.sleep(0.1)

     if n_trials > max_n_trials:
         s = '__get_port_file(): waited ' + str(n_trials) + ' trials for port: ' +\
             port_file
         self.__log.warn(s)

     assert os.path.isfile(port_file) is True, \
            'port_file %r not available; stop.' % port_file

   #..............
   # Provide ports
   #..............
   if provide_port_name is not None:

     assert use_port_name is None

     for port in self.__ports:
       (portName,portType,thisPortFile) = port
       if portName == provide_port_name and portType == 'provide': port_file = thisPortFile

   return port_file
#---------------------- end def __get_port_file():--------------------------------

#======================= end class MyModule: =====================================
