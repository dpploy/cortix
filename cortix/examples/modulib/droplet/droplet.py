# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/cortix
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/COPYRIGHT....
#
# Licensed under the GNU General Public License v. 3, please see LICENSE file.
# https://www.gnu.org/licenses/gpl-3.0.txt
'''
Droplet module example in Cortix.
'''
#*********************************************************************************
import os, sys, io, time
import datetime
import logging

from cortix.support.quantity import Quantity
from cortix.support.specie   import Specie
from cortix.support.phase    import Phase
from collections import namedtuple
#*********************************************************************************

class Droplet():
 r'''
  Droplet module used example in Cortix.
 '''

 def __init__( self,
               slot_id,
               input_full_path_file_name,
               work_dir,
               ports = list(),
               cortix_start_time = 0.0,
               cortix_final_time = 0.0  
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

  # Logging
  self.__log = logging.getLogger('launcher-droplet'+str(slot_id)+'.cortix_driver.droplet')
  self.__log.info('initializing an object of Droplet()')

#.................................................................................
# Member data 

  self.__slot_id = slot_id
  self.__ports  = ports

  self.__start_time = cortix_start_time
  self.__final_time = cortix_final_time

  if work_dir[-1] != '/': work_dir = work_dir + '/'
  self.__wrkDir = work_dir

  # Signal to start operation
  self.__goSignal = True    # start operation immediately
  for port in self.__ports: # if there is a signal port, start operation accordingly
      (port_name,port_type,this_port_file) = port
      if port_name == 'go-signal' and port_type == 'use': self.__go_signal = False

  self.__setup_time = 1.0  # min; a delay time before starting to run

#.................................................................................
# Input ports
# Read input information if any

  #fin = open(input_full_path_file_name,'r')

# Domain specific member data 

  gravity = 9.81 # [m/s^2] acceleration of gravity

  Params = namedtuple('Params',['gravity'])
  self.__params = Params( gravity ) 

  # Setup the material phase as a liquid 
  species = list()

  water = Specie( name='water', formulaName='H2O(l)', phase='liquid' )
  water.massCCUnit = 'g/cc'
  water.molarCCUnit = 'mole/cc'

  species.append(water)

  quantities = list()

  # height
  height = Quantity( name='height', formalName='Height', unit='m' )
  quantities.append( height )
  # speed
  speed = Quantity( name='speed', formalName='Speed', unit='m/s' )
  quantities.append( speed )

  self.__liquid_phase = Phase( cortix_start_time, species=species, quantities=quantities)

  # Initialize phase
  water_mass_cc = 1.00 # [g/cc]
  self.__liquid_phase.SetValue( 'water', water_mass_cc, cortix_start_time )

  x_0 = 1000.0  # initial height [m]
  self.__liquid_phase.SetValue( 'height', x_0, cortix_start_time )

  v_0 = 0.0     # initial speed  [m/s]
  self.__liquid_phase.SetValue( 'speed', v_0, cortix_start_time )

#---------------------- end def __init__():---------------------------------------

 def call_ports( self, cortix_time=0.0 ):
  '''
  Transfer data at cortix_time
  '''

  # provide data to all provide ports 
  self.__provide_data( provide_port_name='output', at_time=cortix_time )

  # use data using the 'use-port-name' of the module
  #self.__use_data( use_port_name='use-port-name', at_time=cortix_time )

  return
#---------------------- end def call_ports():---------------------------------------

 def execute( self, cortix_time=0.0, time_step=0.0 ):
  '''
  Evolve system from cortix_time to cortix_time + time_step
  '''

  s = 'execute('+str(round(cortix_time,2))+'[min]): '
  self.__log.debug(s)

  self.__evolve( cortix_time, time_step )

  return
#---------------------- end def execute():----------------------------------------

#*********************************************************************************
# Private helper functions (internal use: __)

 def __provide_data( self, provide_port_name=None, at_time=0.0 ):

# Access the port file
  port_file = self.__get_port_file( provide_port_name = provide_port_name )

# Provide data to port files
  if provide_port_name == 'output' and port_file is not None: 
   self.__provide_persistent_output( port_file, at_time )

  return
#---------------------- end def __provide_data():---------------------------------

 def __use_data( self, use_port_name=None, at_time=0.0 ):

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
       (port_name,port_type,this_port_file) = port
       if port_name == use_port_name and port_type == 'use': port_file = this_port_file

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
       (port_name,port_type,this_port_file) = port
       if port_name == provide_port_name and port_type == 'provide': port_file = this_port_file
 
   return port_file
#---------------------- end def __get_port_file():--------------------------------

 def __provide_persistent_output( self, port_file, at_time ):
   '''
   This may return a None port_file
   '''
   # if the first time step, write the header of a table data file
   if at_time == self.__start_time:

     assert os.path.isfile(port_file) is False, 'port_file %r exists; stop.' % port_file
     fout = open(port_file,'w')

     fout.write('# name:   '+'droplet_'+str(self.__slot_id)); fout.write('\n')
     fout.write('# author: '+'cortix.examples.modulib.droplet'); fout.write('\n')
     fout.write('# version:'+'0.1'); fout.write('\n')
     today = datetime.datetime.today()
     fout.write('# today:  '+str(today)); fout.write('\n')
     fout.write('#')
# write file header
     fout.write('%17s'%('Time[sec]'))
     # mass density   
     for specie in self.__liquid_phase.GetSpecies():
       fout.write('%18s'%(specie.formulaName+'['+specie.massCCUnit+']'))
     # quantities     
     for quant in self.__liquid_phase.GetQuantities():
       fout.write('%18s'%(quant.formalName+'['+quant.unit+']'))

     fout.write('\n')
     fout.close()

   # write history data

   fout = open(port_file,'a')

   # cortix time 
   fout.write('%18.6e' % (at_time*60.0))

   # mass density   
   for specie in self.__liquid_phase.GetSpecies():
     rho = self.__liquid_phase.GetValue(specie.name, at_time)
     fout.write('%18.6e'%(rho))
     # quantities     
   for quant in self.__liquid_phase.GetQuantities():
     val = self.__liquid_phase.GetValue(quant.name, at_time)
     fout.write('%18.6e'%(val))

   fout.write('\n')
   fout.close()

   return
#---------------------- end def __provide_persistent_output():--------------------

 def __evolve( self, cortix_time=0.0, time_step=0.0 ):

  import numpy as np
  from scikits.odes import ode

# initial data at t=0, u_1(0) = x_0, u_2(0) = v_0 = \dot{u}_1(0)
#                                                    
# problem: d_t u = f(u)
#              ~   ~ ~
  x_0 = self.__liquid_phase.GetValue( 'height', cortix_time )
  v_0 = self.__liquid_phase.GetValue( 'speed', cortix_time )

  u_vec_0 = [x_0, v_0]

  # rhs function
  def rhs_fn(t, u_vec, dt_u_vec, params):
    dt_u_vec[0] = u_vec[1]              #  d_t u_1 = u_2
    dt_u_vec[1] = - params.gravity      #  d_t u_2 = -g
    return

  time_step_sec = time_step * 60.0
  t_interval_sec = np.linspace(0.0, time_step_sec, num=2)

  cvode = ode('cvode', rhs_fn, user_data=self.__params, old_api=False)

  solution = cvode.solve( t_interval_sec, u_vec_0 )  # solve for time interval 

  results = solution.values
  message = solution.message

  assert solution.message == 'Successful function return.'
  assert solution.errors.t is None, 'errors.t = %r'%solution.errors.t
  assert solution.errors.y is None, 'errors.y = %r'%solution.errors.y

  u_vec = results.y[1,:] # solution vector at final time step
  
  values = self.__liquid_phase.GetRow( cortix_time ) # values at previous time

  at_time = cortix_time + time_step 
  self.__liquid_phase.AddRow( at_time, values ) # repeat values for current time

  self.__liquid_phase.SetValue( 'height', u_vec[0], at_time ) # update current values
  self.__liquid_phase.SetValue( 'speed',  u_vec[1], at_time ) # update current values

#  print('u(t=',at_time*60,'[s]) = ',u_1)
  
#---------------------- end def __evolve():---------------------------------------


#======================= end class Droplet: ======================================
