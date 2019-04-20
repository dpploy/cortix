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
Droplet module example in Cortix.
'''
#*********************************************************************************
import os, sys, io, time
import logging
from collections import namedtuple
import math
import numpy as npy

from cortix.src.utils.xmltree import XMLTree
from cortix.support.quantity import Quantity
from cortix.support.specie   import Specie
from cortix.support.phase    import Phase
#*********************************************************************************

class Droplet():
    r'''
    Droplet module used example in Cortix.
    '''

#*********************************************************************************
# Construction
#*********************************************************************************

    def __init__( self,
            slot_id,
            input_full_path_file_name,
            manifesto_full_path_file_name,
            work_dir,
            ports = list(),
            cortix_start_time = 0.0,
            cortix_final_time = 0.0,
            cortix_time_step = 0.0,
            cortix_time_unit=None
                ):

        #.............................................................................
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

        # Logging: access Cortix Launcher logging facility
        self.__log = logging.getLogger('launcher-droplet_'+str(slot_id)+'.cortix_driver.droplet')
        self.__log.info('initializing an object of Droplet()')

        # Read the manisfesto
        self.__read_manifesto( manifesto_full_path_file_name )
        self.__log.info(self.__port_diagram)

        #.............................................................................
        # Member data 

        self.__slot_id = slot_id
        self.__ports   = ports

        # Convert Cortix's time unit to Droplet's internal time unit
        if cortix_time_unit == 'minute':
            self.__time_unit_scale = 60.0
        elif cortix_time_unit == 'second':
            self.__time_unit_scale = 1.0
        elif cortix_time_unit == 'hour':
            self.__time_unit_scale = 60.0*60.0
        else:
            assert False, 'Cortix time_unit: %r not acceptable.' % time_unit

        self.__cortix_time_unit = cortix_time_unit

        self.__start_time = cortix_start_time * self.__time_unit_scale # Droplet time unit
        self.__final_time = cortix_final_time * self.__time_unit_scale # Droplet time unit

        if work_dir[-1] != '/': work_dir = work_dir + '/'
        self.__wrkDir = work_dir

        # Signal to start operation
        self.__goSignal = True     # start operation immediately
        for port in self.__ports:  # if there is a signal port, start operation accordingly
            (port_name, port_type, this_port_file) = port
            if port_name == 'go-signal' and port_type == 'use': self.__go_signal = False

        self.__setup_time = 60.0  # time unit; a delay time before starting to run

        #.............................................................................
        # Input ports
        # Read input information if any

        #fin = open(input_full_path_file_name,'r')

        # Configuration member data   

        self.__pyplot_scale = 'linear'
        #  self.__ode_integrator = 'scikits.odes' # or 'scipy.integrate' 
        self.__ode_integrator = 'scipy.integrate'

        # Domain specific member data 

        gravity = 9.81 # [m/s^2] acceleration of gravity

        Params = namedtuple('Params',['gravity'])
        self.__params = Params( gravity )

        # Setup the material phase as a liquid 
        species = list()

        water = Specie( name='water', formulaName='H2O(l)', phase='liquid', atoms=['2*H','O'] )
        water.massCCUnit = 'g/cc'
        water.molarCCUnit = 'mole/cc'

        species.append(water)

        quantities = list()

        # spatial position
        spatial_position = Quantity( name='spatial-position', formalName='Spatial Pos.', unit='m' )
        quantities.append( spatial_position )
        # velocity
        velocity = Quantity( name='velocity', formalName='Veloc.', unit='m/s' )
        quantities.append( velocity )

        self.__liquid_phase = Phase( self.__start_time, species=species, quantities=quantities)

        # Initialize phase
        water_mass_cc = 0.99965 # [g/cc]
        self.__liquid_phase.SetValue( 'water', water_mass_cc, self.__start_time )

        x_0 = (0.0,0.0,1000.0)  # initial height [m] above ground at 0
        self.__liquid_phase.SetValue( 'spatial-position', x_0, self.__start_time )

        v_0 = (0.0,0.0,0.0)     # initial velocity [m/s]
        self.__liquid_phase.SetValue( 'velocity', v_0, self.__start_time )

        return

#*********************************************************************************
# Public member functions
#*********************************************************************************

    def call_ports( self, cortix_time=0.0 ):
        '''
        Transfer data at cortix_time
        '''

        cortix_time *= self.__time_unit_scale  # convert to Droplet time unit

        # provide data to all provide ports 
        self.__provide_data( provide_port_name='output', at_time=cortix_time )
        self.__provide_data( provide_port_name='state',  at_time=cortix_time )

        # use data using the 'use-port-name' of the module
        #self.__use_data( use_port_name='use-port-name', at_time=cortix_time )

        return

    def execute( self, cortix_time=0.0, cortix_time_step=0.0 ):
        '''
        Evolve system from cortix_time to cortix_time + cortix_time_step
        '''

        cortix_time      *= self.__time_unit_scale  # convert to Droplet time unit
        cortix_time_step *= self.__time_unit_scale  # convert to Droplet time unit

        s = 'execute('+str(round(cortix_time,2))+'[min]): '
        self.__log.debug(s)

        self.__evolve( cortix_time, cortix_time_step )

        return

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

    def __provide_data( self, provide_port_name=None, at_time=0.0 ):

        # Access the port file
        port_file = self.__get_port_file( provide_port_name = provide_port_name )

        # Provide data to port files
        if provide_port_name == 'output' and port_file is not None:
            self.__provide_output( port_file, at_time )

        if provide_port_name == 'state' and port_file is not None:
             self.__provide_state( port_file, at_time )

        return

    def __use_data( self, use_port_name=None, at_time=0.0 ):

        # Access the port file
        port_file = self.__get_port_file( use_port_name = use_port_name )

        # Use data from port file
        #if use_port_name == 'use-port-name' and port_file is not None:  
        #   self.__use_mymodule_method( port_file, at_time )

        return

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

                if port_name == use_port_name and port_type == 'use':
                    port_file = this_port_file

            if port_file is None:
                return None

            max_n_trials = 50
            n_trials     = 0
            while os.path.isfile(port_file) is False and n_trials <= max_n_trials:
                n_trials += 1
                time.sleep(0.1)

            if n_trials > max_n_trials:
                s = '__get_port_file(): waited ' + str(n_trials) + ' trials for port: ' +\
                        port_file
                self.__log.warn(s)

            assert os.path.isfile(port_file) is True,'port_file %r not available; stop.'\
                    % port_file

        #..............
        # Provide ports
        #..............
        if provide_port_name is not None:

            assert use_port_name is None

            for port in self.__ports:
                (port_name,port_type,this_port_file) = port
                if port_name == provide_port_name and port_type == 'provide': \
                        port_file = this_port_file

        return port_file

    def __provide_output( self, port_file, at_time ):
        '''
        Provide data that will remain in disk after the simulation ends.
        '''
        import datetime

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
                if quant.name == 'spatial-position' or quant.name == 'velocity':
                   for i in range(3):
                       fout.write('%18s'%(quant.formalName+str(i+1)+'['+quant.unit+']'))
                else:
                   fout.write('%18s'%(quant.formalName+'['+quant.unit+']'))

            fout.write('\n')
            fout.close()

        # write history data

        fout = open(port_file,'a')

        # Droplet time 
        fout.write('%18.6e' % (at_time))

        # mass density   
        for specie in self.__liquid_phase.GetSpecies():
            rho = self.__liquid_phase.GetValue(specie.name, at_time)
            fout.write('%18.6e'%(rho))
        # quantities     
        for quant in self.__liquid_phase.GetQuantities():
            val = self.__liquid_phase.GetValue(quant.name, at_time)
            if quant.name == 'spatial-position' or quant.name == 'velocity':
                for v in val:
                    fout.write('%18.6e'%(v))
            else:
                fout.write('%18.6e'%(val))

        fout.write('\n')
        fout.close()

        return

    def __provide_state( self, port_file, at_time ):
        '''
        Provide the internal state of the module. This is typically used by another
        module such as '.cortix.modulib.pyplot'; this XML file type is now deprecated.
        However to have a dynamic plotting option, create this history file in the
        time unit of Cortix; that is, undo the time scaling.
        '''
        import datetime
        import xml.etree.ElementTree as ElementTree
        from threading import Lock

        n_digits_precision = 8

        # Write header
        if at_time == self.__start_time:

         assert os.path.isfile(port_file) is False, 'port_file %r exists; stop.'\
                 % port_file

         a = ElementTree.Element('time-sequence')
         a.set('name','droplet_'+str(self.__slot_id)+'-state')

         b = ElementTree.SubElement(a,'comment')
         b.set('author','cortix.examples.modulib.droplet')
         b.set('version','0.1')

         b = ElementTree.SubElement(a,'comment')
         today = datetime.datetime.today()
         b.set('today',str(today))

         b = ElementTree.SubElement(a,'time')
         b.set('unit',self.__cortix_time_unit)

         # setup the headers
         for specie in self.__liquid_phase.species:
             b = ElementTree.SubElement(a,'var')
             formula_name = specie.formulaName
             b.set('name',formula_name)
             unit = specie.massCCUnit
             b.set('unit',unit)
             b.set('legend','Droplet_'+str(self.__slot_id)+'-state')
             b.set('scale',self.__pyplot_scale)

         for quant in self.__liquid_phase.quantities:
             formal_name = quant.formalName
             if quant.name == 'spatial-position' or quant.name == 'velocity':
                 for i in range(3):
                     b = ElementTree.SubElement(a,'var')
                     b.set('name',formal_name+' '+str(i+1))
                     unit = quant.unit
                     b.set('unit',unit)
                     b.set('legend','Droplet_'+str(self.__slot_id)+'-state')
                     b.set('scale',self.__pyplot_scale)
             else:
                 b = ElementTree.SubElement(a,'var')
                 b.set('name',formal_name)
                 unit = quant.unit
                 b.set('unit',unit)
                 b.set('legend','Droplet_'+str(self.__slot_id)+'-state')
                 b.set('scale',self.__pyplot_scale)

         # Write values for all variables
         b = ElementTree.SubElement(a,'timeStamp')
         b.set('value',str(round(at_time/self.__time_unit_scale,n_digits_precision)))

         values = list()

         for specie in self.__liquid_phase.species:
             val = self.__liquid_phase.GetValue( specie.name, at_time )
             values.append( val )

         for quant in self.__liquid_phase.quantities:
             val = self.__liquid_phase.GetValue( quant.name, at_time )
             if quant.name == 'spatial-position' or quant.name == 'velocity':
                for v in val:
                    values.append( math.fabs(v) ) # pyplot can't take negative values
             else:
                values.append( val )

         # Flush out data
         text = str()
         for value in values:
             text += str(round(value,n_digits_precision)) + ','

         text = text[:-1]

         b.text = text

         tree = ElementTree.ElementTree(a)

         tree.write( port_file, xml_declaration=True, encoding="unicode", method="xml" )

        #-------------------------------------------------------------------------
        # if not the first time step then parse the existing history file and append 
        # to it
        else:

            mutex = Lock()
            mutex.acquire()

            tree = ElementTree.parse( port_file )
            root_node = tree.getroot()

            a = ElementTree.Element('timeStamp')
            a.set('value',str(round(at_time/self.__time_unit_scale,n_digits_precision)))

            # All variables values
            values = list()

            for specie in self.__liquid_phase.species:
                val = self.__liquid_phase.GetValue( specie.name, at_time )
                values.append( val )
            for quant in self.__liquid_phase.quantities:
                val = self.__liquid_phase.GetValue( quant.name, at_time )
                if quant.name == 'spatial-position' or quant.name == 'velocity':
                    for v in val:
                        values.append( math.fabs(v) ) # pyplot can't take negative values
                else:
                    values.append( val )

            # Flush out data
            text = str()
            for value in values:
                text += str(round(value,n_digits_precision)) + ','

            text = text[:-1]

            a.text = text

            root_node.append(a)

            tree.write( port_file, xml_declaration=True, encoding="unicode", method="xml" )

            mutex.release()

        return

    def __evolve( self, cortix_time=0.0, cortix_time_step=0.0 ):
        r'''
        ODE IVP problem:
        Given the initial data at :math:`t=0`, :math:`u_1(0) = x_0`,
        :math:`u_2(0) = v_0 = \dot{u}_1(0)`,
        solve :math:`\frac{\text{d}u}{\text{d}t} = f(u)` in the interval
        :math:`0\le t \le t_f`.
        When :math:`u_1(t)` is negative, bounce the droplet to a random height between
        0 and :math:`1.2\,x_0` with no velocity, and continue the time integration until
        :math:`t = t_f`.
        '''
        if self.__ode_integrator == 'scikits.odes':
            from scikits.odes import ode        # this requires the SUNDIALS ODE package 
        elif self.__ode_integrator == 'scipy.integrate':
            from scipy.integrate import odeint  # this ships with scipy 
        else:
            assert False, 'Fatal: invalid ode integrator config. %r'%self.__ode_integrator

        x_0 = self.__liquid_phase.GetValue( 'spatial-position', cortix_time )
        v_0 = self.__liquid_phase.GetValue( 'velocity', cortix_time )

        u_vec_0 = x_0 + v_0 # concatenate tuples

        # rhs function
        if self.__ode_integrator == 'scikits.odes':
            def rhs_fn(t, u_vec, dt_u_vec, params):
                dt_u_vec[0] = u_vec[3]              #  d_t u_1 = u_4
                dt_u_vec[3] = 0.0                   #  d_t u_4 = 0 

                dt_u_vec[1] = u_vec[4]              #  d_t u_2 = u_5
                dt_u_vec[4] = 0.0                   #  d_t u_5 = 0 

                dt_u_vec[2] = u_vec[5]              #  d_t u_3 = u_6
                dt_u_vec[5] = - params.gravity      #  d_t u_6 = -g
                return
        elif self.__ode_integrator == 'scipy.integrate':
            def rhs_fn(u_vec, t, gravity):
                dt_u_0 = u_vec[3]              #  d_t u_1 = u_4
                dt_u_3 = 0.0                   #  d_t u_4 = 0

                dt_u_1 = u_vec[4]              #  d_t u_2 = u_5
                dt_u_4 = 0.0                   #  d_t u_5 = 0 

                dt_u_2 = u_vec[5]              #  d_t u_3 = u_6
                dt_u_5 = - gravity             #  d_t u_6 = -g
                return [dt_u_0, dt_u_1, dt_u_2, dt_u_3, dt_u_4, dt_u_5]
        else:
            assert False, 'Fatal: invalid ode integrator config. %r'%self.__ode_integrator

        t_interval_sec = npy.linspace(0.0, cortix_time_step, num=2)

        if self.__ode_integrator == 'scikits.odes':
            cvode = ode('cvode', rhs_fn, user_data=self.__params, old_api=False)
            solution = cvode.solve( t_interval_sec, u_vec_0 )  # solve for time interval 

            results = solution.values
            message = solution.message

            assert solution.message == 'Successful function return.'
            assert solution.errors.t is None, 'errors.t = %r'%solution.errors.t
            assert solution.errors.y is None, 'errors.y = %r'%solution.errors.y

            u_vec = results.y[1,:] # solution vector at final time step

        elif self.__ode_integrator == 'scipy.integrate':
            ( u_vec_hist, info_dict ) = odeint( rhs_fn,
                                                u_vec_0, t_interval_sec,
                                                args=( self.__params.gravity, ),
                                                full_output=True
                                              )

            assert info_dict['message']=='Integration successful.',\
                   'Fatal: scipy.integrate.odeint failed %r'%info_dict['message']

            u_vec = u_vec_hist[1,:]  # solution vector at final time step
        else:
            assert False, 'Fatal: invalid ode integrator config. %r'%self.__ode_integrator


        values = self.__liquid_phase.GetRow( cortix_time ) # values at previous time

        at_time = cortix_time + cortix_time_step

        self.__liquid_phase.AddRow( at_time, values ) # repeat values for current time

        if u_vec[2] <= 0.0: # ground impact bounces the drop to a different height near original
            position = self.__liquid_phase.GetValue( 'spatial-position', self.__start_time )
            bounced_position = list(position)
            bounced_position[2] *= npy.random.random(1) * 1.2
            u_vec[0:3] = bounced_position[:]
            u_vec[3:]  = 0.0

        self.__liquid_phase.SetValue( 'spatial-position', tuple(u_vec[0:3]), at_time ) # update current values
        self.__liquid_phase.SetValue( 'velocity', tuple(u_vec[3:]), at_time ) # update current values

        return

    def __read_manifesto( self, xml_tree_file ):
        '''
        Parse the manifesto
        '''

        assert isinstance(xml_tree_file, str)

        # Read the manifesto
        xml_tree = XMLTree( xml_tree_file=xml_tree_file )

        assert xml_tree.get_node_tag() == 'module_manifesto'

        assert xml_tree.get_node_attribute('name') == 'droplet'

        # List of (port_name, port_type, port_mode, port_multiplicity)
        __ports = list()

        self.__port_diagram = 'null-module-port-diagram'

        # Get manifesto data  
        for child in xml_tree.get_node_children():
            (elem, tag, attributes, text) = child

            if tag == 'port':

                text = text.strip()

                assert len(attributes) == 3, "only <= 3 attributes allowed."

                tmp = dict()  # store port name and three attributes

                for attribute in attributes:
                    key = attribute[0].strip()
                    val = attribute[1].strip()

                    if key == 'type':
                        assert val == 'use' or val == 'provide' or val == 'input' or \
                            val == 'output', 'port attribute value invalid.'
                        tmp['port_name'] = text  # port_name
                        tmp['port_type'] = val   # port_type
                    elif key == 'mode':
                        file_value = val.split('.')[0]
                        assert file_value == 'file' or file_value == 'directory',\
                            'port attribute value invalid.'
                        tmp['port_mode'] = val
                    elif key == 'multiplicity':
                        tmp['port_multiplicity'] = int(val)  # port_multiplicity
                    else:
                        assert False, 'invalid port attribute: %r=%r. fatal.'%\
                                (key,val)

                assert len(tmp) == 4
                store = (tmp['port_name'], tmp['port_type'], tmp['port_mode'],
                         tmp['port_multiplicity'])

                # (port_name, port_type, port_mode, port_multiplicity)
                __ports.append(store)

                # clear
                tmp   = None
                store = None

            if tag == 'diagram':

                self.__port_diagram = text

            if tag == 'ascii_art':

                self.__ascii_art = text

        return

#======================= end class Droplet: ======================================
