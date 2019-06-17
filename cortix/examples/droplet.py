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
import math
import numpy as npy

from cortix.src.module import Module

#from cortix.src.utils.xmltree import XMLTree
from cortix.support.quantity import Quantity
from cortix.support.specie   import Specie
from cortix.support.phase    import Phase
#*********************************************************************************

class Droplet(Module):
    r'''
    Droplet module used example in Cortix.
    '''

#*********************************************************************************
# Construction
#*********************************************************************************

    def __init__( self ):

        super().__init__()

        # Choice of ODE solvers. This is a temporary fix for running multiple
        # droplets solver. SciPy ode solver is not thread safe. SUNDIALS is thread safe.

        self.__slot_id = 0

        self.__start_time = 0.0

        if self.__slot_id == 0:
            self.__ode_integrator = 'scipy.integrate'
        else:
            self.__ode_integrator = 'scikits.odes' # or 'scipy.integrate' 

        # Domain specific member data.

        self.__ode_params = dict() # hold parameters for the ODE solver

        import scipy.constants as const
        # Create a drop with random diameter up within 5 and 8 mm.
        diam = (npy.random.random(1)*(8 - 5) + 5)[0]
        #diam = 8
        droplet_diameter = diam * const.milli # [m]
        self.__ode_params['droplet-diameter'] = droplet_diameter
        self.__ode_params['droplet-xsec-area'] = math.pi*(droplet_diameter/2.0)**2

        gravity = const.g # acceleration of gravity SI

        self.__ode_params['gravity'] = gravity

        # Setup species in the liquid phase.
        species = list()

        water = Specie( name='water', formula_name='H2O(l)', phase='liquid',
                atoms=['2*H','O'] )

        water_mass_cc     = 0.99965 # [g/cc]
        water.massCCUnit  = 'g/cc'
        water.molarCCUnit = 'mole/cc'
        water.massCC      = water_mass_cc

        droplet_mass = 4/3*math.pi*(droplet_diameter/2)**3 * \
                water.massCC * const.gram / const.centi**3  # [kg]

        self.__ode_params['droplet-mass'] = droplet_mass

        species.append(water)

        # Quantities in the liquid phase.
        quantities = list()

        # Spatial position must be npy.ndarray (see ODE solvers).
        x_0 = npy.zeros(3)
        position = Quantity( name='position', formalName='Pos.', unit='m', value=x_0 )
        quantities.append( position )

        # Velocity must be npy.ndarray (see ODE solvers).
        v_0 = npy.zeros(3)
        velocity = Quantity( name='velocity', formalName='Veloc.', unit='m/s', value=v_0 )
        quantities.append( velocity )

        # Speed is a by-product
        speed = Quantity( name='speed', formalName='Speed', unit='m/s', value=0.0 )
        quantities.append( speed )

        # Radial position
        radial_pos = Quantity( name='radial-position', formalName='Radius', unit='m',
                value=npy.linalg.norm(x_0[0:2]))
        quantities.append( radial_pos )

        # Create Phase.
        self.__liquid_phase = Phase( self.__start_time, time_unit='s', species=species,
                quantities=quantities )

        # Initialize phase.
        self.__liquid_phase.SetValue( 'water', water_mass_cc, self.__start_time )

        # Domain box dimensions: LxLxH m^3 box with given H.
        # Origin of cartesian coordinate system at the bottom of the box. 
        # z coordinate pointing upwards. -L <= x <= L, -L <= y <= L, 
        self.__box_half_length = 250.0 # L [m]
        self.__box_height      = 250.0 # H [m]

        # Random positioning of the droplet. Constraint positioning to a box sub-region.
        x_0 = ( 2*npy.random.random(3) - npy.ones(3) ) * self.__box_half_length/2.0
        #x_0 = npy.array([40,40,0])
        x_0[2] = self.__box_height
        self.__liquid_phase.SetValue( 'position', x_0, self.__start_time )

        # Set the initial velocity of the droplet to zero as the droplet has been
        # placed still in the flow. Flow velocity must be npy.ndarray (see ODE solvers).
        self.__liquid_phase.SetValue( 'velocity', npy.array([0.0,0.0,0.0]),
                self.__start_time )

        # This is a default value for the medium surrounding the droplet
        # Air mass density: 0.1 g/cc
        medium_mass_density = 0.1 * const.gram / const.centi**3 # [kg/m^3]
        self.__ode_params['medium-mass-density'] = medium_mass_density

        medium_displaced_mass = 4/3*math.pi*(droplet_diameter/2)**3 * \
                medium_mass_density # [kg]

        self.__ode_params['medium-displaced-mass'] = medium_displaced_mass

        medium_dyn_viscosity = 1.81e-5 # kg/(m s)
        self.__ode_params['medium-dyn-viscosity'] = medium_dyn_viscosity

        # Vortex model for initial velocity (this is for the sake of testing the droplet
        # motion with flow drag) when there is no flow connection through the velocity
        # port.
        self.__min_core_radius = 2.5 # [m]
        self.__outer_v_theta = 1.0 # m/s # angular speed
        self.__v_z_0 = 0.50 # [m/s]
        # Save the function reference for future dispatch in the ODE solver
        self.__ode_params['flow-velocity-function'] = self.__vortex_velocity

        # Plots for insight on the vortex flow field if there is no external
        # flow data through port connection.
        flow_velocity_port_attached = False

        if flow_velocity_port_attached == False:
            pass
            #self.__plot_vortex_velocity()

        return

#*********************************************************************************
# Public member functions
#*********************************************************************************

    def run( self ):
        '''
        Evolve system from cortix_time to cortix_time + cortix_time_step
        '''

        time = 0.0
        for i in range(10000):

            position = self.__liquid_phase.GetValue( 'position' )
            self.send( (time,position), 'velocity-request')
            (vortex_time,velocity) = self.recv( 'velocity' )

            self.__evolve( time, 0.1 )

            time += 0.1

            radius = self.__liquid_phase.GetValue( 'radial-position' )
            self.send( (time,radius), 'radius')

            speed = self.__liquid_phase.GetValue( 'speed' )
            #self.send( (time,speed), 'speed')

        self.send( 'DONE', 'radius')
        #self.send( 'DONE', 'speed')

        self.__liquid_phase.WriteHTML('dp.html')

        return

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

    def __provide_data( self, provide_port_name=None, at_time=0.0 ):

        # Access the port file.
        port_file = self.__get_port_file( provide_port_name = provide_port_name )

        # Provide data to port files.
        if provide_port_name == 'droplet-position' and port_file is not None:
            self.__provide_droplet_position( port_file, at_time )

        if provide_port_name == 'output' and port_file is not None:
            self.__provide_output( port_file, at_time )

        if provide_port_name == 'state' and port_file is not None:
            self.__provide_state( port_file, at_time )

        return

    def __use_data( self, use_port_name=None, at_time=0.0 ):

        # Access the port file.
        port_file = self.__get_port_file( use_port_name = use_port_name )

        # Use data from port files.
        if use_port_name == 'flow-velocity' and port_file is not None:
            self.__use_flow_velocity( port_file, at_time )

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

                if port_name == provide_port_name and port_type == 'provide':
                    port_file = this_port_file

        return port_file

    def __provide_droplet_position( self, port_file, at_time ):
        '''
        Provide data while other programs may be trying to read the data. This requires
        a lock. The port file may be completely rewritten or appended to.

        Parameters
        ----------
        port_file: str

        at_time: float

        Returns
        -------
        None
        '''

        import pickle
        from threading import Lock

        lock = Lock()

        with lock:

            (position_history, time_unit) = self.__liquid_phase.get_quantity_history(
                    'position')

            pickle.dump( (position_history, time_unit), open(port_file,'wb') )

        #print('*****************************************************************')
        #print('DROPLET: POSITION SENT')
        #print('at_time=',at_time, 'pos_hist=',position_history)
        #print('*****************************************************************')

        s = '__provide_droplet_position('+str(round(at_time,2))+'[s]): '
        m = 'pickle.dumped droplet position.'
        self.__log.debug(s+m)

        return

    def __provide_output( self, port_file, at_time ):
        '''
        Provide data that will remain in disk after the simulation ends.
        This only writes the data at the end of the simulation in a compact form using
        pickle and a phase container.
        '''

        if at_time < self.__final_time:
            return

        import pickle

        assert os.path.isfile(port_file) is False,'port_file %r exists; stop.'%port_file

        pickle.dump( self.__liquid_phase, open(port_file,'wb') )

        return

    def __provide_output_example( self, port_file, at_time ):
        '''
        Provide data that will remain in disk after the simulation ends, persistent
        data. This is an example of how to write a low level plain ASCII table of
        data. This is not used.
        '''
        import datetime

        # If the first time step, write the header of a table data file.
        if at_time == self.__start_time:

            assert os.path.isfile(port_file) is False,'port_file %r exists; stop.'%\
                    port_file

            fout = open(port_file,'w')

            fout.write('# name:   '+'droplet_'+str(self.__slot_id)); fout.write('\n')
            fout.write('# author: '+'cortix.examples.modulib.droplet'); fout.write('\n')
            fout.write('# version:'+'0.1'); fout.write('\n')
            today = datetime.datetime.today()
            fout.write('# today:  '+str(today)); fout.write('\n')
            fout.write(' ')
            # Write file header.
            fout.write('%17s'%('Time[sec]'))
            # Mass density.
            for specie in self.__liquid_phase.GetSpecies():
              fout.write('%18s'%(specie.formula_name+'['+specie.massCCUnit+']'))
            # Quantities.
            for quant in self.__liquid_phase.GetQuantities():
                if quant.name == 'position' or quant.name == 'velocity':
                   for i in range(3):
                       fout.write('%18s'%(quant.formalName+str(i+1)+'['+quant.unit+']'))
                else:
                   fout.write('%18s'%(quant.formalName+'['+quant.unit+']'))

            fout.write('\n')
            fout.close()

        # Write history data.
        fout = open(port_file,'a')

        # Droplet time.
        fout.write('%18.6e' % (at_time))

        # Mass density.  
        for specie in self.__liquid_phase.GetSpecies():
            rho = self.__liquid_phase.GetValue(specie.name, at_time)
            fout.write('%18.6e'%(rho))

        # Quantities.
        for quant in self.__liquid_phase.GetQuantities():
            val = self.__liquid_phase.GetValue(quant.name, at_time)
            if quant.name == 'position' or quant.name == 'velocity':
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

        # Write header.
        if at_time == self.__start_time:

            assert os.path.isfile(port_file) is False, 'port_file %r exists; stop.'%\
                 port_file

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

            # Setup the headers.
            for specie in self.__liquid_phase.species:
                b = ElementTree.SubElement(a,'var')
                formula_name = specie.formula_name
                b.set('name',formula_name)
                unit = specie.massCCUnit
                b.set('unit',unit)
                b.set('legend','Droplet_'+str(self.__slot_id)+'-state')
                b.set('scale',self.__pyplot_scale)

            for quant in self.__liquid_phase.quantities:
                formal_name = quant.formalName
                if quant.name == 'position' or quant.name == 'velocity':
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

            # Write values for all variables.
            b = ElementTree.SubElement(a,'timeStamp')
            b.set('value',str(round(at_time/self.__time_unit_scale,n_digits_precision)))

            values = list()

            for specie in self.__liquid_phase.species:
                val = self.__liquid_phase.GetValue( specie.name, at_time )
                values.append( val )

            for quant in self.__liquid_phase.quantities:
                val = self.__liquid_phase.GetValue( quant.name, at_time )
                if quant.name == 'position' or quant.name == 'velocity':
                   for v in val:
                       #values.append( math.fabs(v) ) # pyplot can't take negative values
                       values.append( v ) # pyplot can't take negative values
                else:
                   values.append( val )

            # Flush out data.
            text = str()
            for value in values:
                text += str(round(value,n_digits_precision)) + ','

            text = text[:-1]

            b.text = text

            tree = ElementTree.ElementTree(a)

            tree.write( port_file, xml_declaration=True, encoding="unicode",
                    method="xml" )

        #-------------------------------------------------------------------------
        # If not the first time step then parse the existing history file and append 
        # to it.
        else:

            mutex = Lock()
            mutex.acquire()

            tree = ElementTree.parse( port_file )
            root_node = tree.getroot()

            a = ElementTree.Element('timeStamp')
            a.set('value',str(round(at_time/self.__time_unit_scale,n_digits_precision)))

            # All variables values.
            values = list()

            for specie in self.__liquid_phase.species:
                val = self.__liquid_phase.GetValue( specie.name, at_time )
                values.append( val )
            for quant in self.__liquid_phase.quantities:
                val = self.__liquid_phase.GetValue( quant.name, at_time )
                if quant.name == 'position' or quant.name == 'velocity':
                    for v in val:
                        #values.append( math.fabs(v) ) # pyplot can't take negative values
                        values.append( v ) # pyplot can't take negative values
                else:
                    values.append( val )

            # Flush out data.
            text = str()
            for value in values:
                text += str(round(value,n_digits_precision)) + ','

            text = text[:-1]

            a.text = text

            root_node.append(a)

            tree.write( port_file, xml_declaration=True, encoding="unicode", method="xml" )

            mutex.release()

        return

    def __use_flow_velocity( self, port_file, at_time ):
        '''
        Get flow velocity.
        '''

        import pickle
        from threading import Lock
        import numpy as npy

        lock = Lock()

        found = False
        while found is False:

            try:
                lock.acquire()
                flow_phase = pickle.load( open(port_file,'rb') )
                assert flow_phase.time_unit == 's'

                # Find in the Flow Phase the specific quantity name
                for port in self.__ports:
                    (port_name, port_type, this_port_file) = port
                    if port_name == 'droplet-position':
                       assert port_type == 'provide'
                       velocity_name = 'velocity@'+this_port_file

                # Get this Droplet's velocity
                velocity = flow_phase.GetValue(velocity_name,at_time)

                #print('***********************************************************')
                #print('DROPLET: VELOCITY RECEIVED')
                #print('at_time=',at_time,'velocity=',velocity)
                #print('***********************************************************')

                #loc = velocity.value.index.get_loc(at_time,method='nearest',
                #        tolerance=1e-2)
                #time_stamp = velocity.value.index[loc]

                #assert abs(time_stamp - at_time) <= 1e-2

                found = True
                lock.release()

            except:
                lock.release()
                s = '__use_flow_velocity('+str(round(at_time,2))+'[s]): '
                m = port_file+' does not have data yet. Retrying ...'
                self.__log.debug(s+m)
                self.__log.debug(s)

        s = '__use_flow_velocity('+str(round(at_time,2))+'[s]): pickle.loaded velocity.'
        self.__log.debug(s)

        #flow_velocity = velocity.value.loc[time_stamp]
        flow_velocity = velocity
        assert isinstance(flow_velocity,npy.ndarray)
        self.__flow_velocity = flow_velocity

        #print('flow velocity = ',flow_velocity)
        self.__ode_params['flow-velocity'] = flow_velocity

        return

    def __evolve( self, at_time=0.0, at_time_step=0.0 ):
        r'''
        ODE IVP problem:
        Given the initial data at :math:`t=0`,
        :math:`(u_1(0),u_2(0),u_3(0)) = (x_0,x_1,x_2)`,
        :math:`(u_4(0),u_5(0),u_6(0)) = (v_0,v_1,v_2) =
        (\dot{u}_1(0),\dot{u}_2(0),\dot{u}_3(0))`,
        solve :math:`\frac{\text{d}u}{\text{d}t} = f(u)` in the interval
        :math:`0\le t \le t_f`.
        When :math:`u_3(t)` is negative, bounce the droplet to a random height between
        0 and :math:`1.0\,x_0` with no velocity, and continue the time integration until
        :math:`t = t_f`.

        Parameters
        ----------
        at_time: float
            Time in the droplet unit of time (seconds).

        at_time_step: float
            Time step in the droplet unit of time (seconds).

        Returns
        -------
        None
        '''

        if self.__ode_integrator == 'scikits.odes':
            from scikits.odes import ode        # this requires the SUNDIALS ODE package 
        elif self.__ode_integrator == 'scipy.integrate':
            from scipy.integrate import odeint  # this ships with scipy 
        else:
            assert False, 'Fatal: invalid ode integrator config. %r'%self.__ode_integrator

        x_0 = self.__liquid_phase.GetValue( 'position', at_time )
        v_0 = self.__liquid_phase.GetValue( 'velocity', at_time )

        u_vec_0 = npy.concatenate((x_0,v_0)) # concatenate vectors

        # rhs function
        if self.__ode_integrator == 'scikits.odes':

            def rhs_fn(t, u_vec, dt_u_vec, params):

                drop_pos = u_vec[:3]

                try:
                    flow_velo = params['flow-velocity'] # try port connected data
                except:
                    flow_velo_func = params['flow-velocity-function'] # use function
                    flow_velo      = flow_velo_func(drop_pos)

                drop_velo     = u_vec[3:]
                relative_velo = drop_velo - flow_velo
                relative_velo_mag = npy.linalg.norm(relative_velo)
                area = params['droplet-xsec-area']
                diameter = params['droplet-diameter']
                dyn_visco = params['medium-dyn-viscosity']

                rho_flow = params['medium-mass-density']
                reynolds_num = rho_flow * relative_velo_mag * diameter / dyn_visco

                if reynolds_num > 0.0 and reynolds_num < 0.1:
                    fric_factor = 24/reynolds_num
                elif reynolds_num >= 0.1 and reynolds_num < 6000.0:
                    fric_factor = ( math.sqrt(24/reynolds_num) + 0.5407 )**2
                elif reynolds_num >= 6000:
                    fric_factor = 0.44

                if reynolds_num == 0.0:
                    fric_factor = 0.0

                drag = - fric_factor * area * \
                        rho_flow * relative_velo_mag * relative_velo/2.0

                gravity   = params['gravity']
                droplet_mass = params['droplet-mass']
                medium_displaced_mass = params['medium-displaced-mass']
                buoyant_force = (droplet_mass - medium_displaced_mass) * gravity

                dt_u_vec[0] = u_vec[3]                                #  d_t u_1 = u_4
                dt_u_vec[3] = drag[0]/droplet_mass                    #  d_t u_4 = f_1

                dt_u_vec[1] = u_vec[4]                                #  d_t u_2 = u_5
                dt_u_vec[4] = drag[1]/droplet_mass                    #  d_t u_5 = f_2

                dt_u_vec[2] = u_vec[5]                                #  d_t u_3 = u_6
                dt_u_vec[5] = (drag[2] - buoyant_force)/droplet_mass  #  d_t u_6 = f_3

                return

        elif self.__ode_integrator == 'scipy.integrate':

            def rhs_fn(u_vec, t, params):

                drop_pos = u_vec[:3]

                try:
                    flow_velo = params['flow-velocity'] # try port connected data
                except:
                    flow_velo_func = params['flow-velocity-function'] # use function
                    flow_velo      = flow_velo_func(drop_pos)

                drop_velo     = u_vec[3:]
                relative_velo = drop_velo - flow_velo
                relative_velo_mag = npy.linalg.norm(relative_velo)
                area = params['droplet-xsec-area']
                diameter = params['droplet-diameter']
                dyn_visco = params['medium-dyn-viscosity']

                rho_flow = params['medium-mass-density']
                reynolds_num = rho_flow * relative_velo_mag * diameter / dyn_visco

                if reynolds_num > 0.0 and reynolds_num < 0.1:
                    fric_factor = 24/reynolds_num
                elif reynolds_num >= 0.1 and reynolds_num < 6000.0:
                    fric_factor = ( math.sqrt(24/reynolds_num) + 0.5407 )**2
                elif reynolds_num >= 6000:
                    fric_factor = 0.44

                if reynolds_num == 0.0:
                    fric_factor = 0.0

                drag = - fric_factor * area * \
                        rho_flow * relative_velo_mag * relative_velo/2.0

                gravity   = params['gravity']
                droplet_mass = params['droplet-mass']
                medium_displaced_mass = params['medium-displaced-mass']
                buoyant_force = (droplet_mass - medium_displaced_mass) * gravity

                dt_u_0 = u_vec[3]                               #  d_t u_1 = u_4
                dt_u_3 = drag[0]/droplet_mass                   #  d_t u_4 = f_1/m

                dt_u_1 = u_vec[4]                               #  d_t u_2 = u_5
                dt_u_4 = drag[1]/droplet_mass                   #  d_t u_5 = f_2/m

                dt_u_2 = u_vec[5]                               #  d_t u_3 = u_6
                dt_u_5 = (drag[2] - buoyant_force)/droplet_mass #  d_t u_6 = f_3/m

                return [dt_u_0, dt_u_1, dt_u_2, dt_u_3, dt_u_4, dt_u_5]
        else:
            assert False, 'Fatal: invalid ode integrator config. %r'%self.__ode_integrator

        t_interval_sec = npy.linspace(0.0, at_time_step, num=2) # two time stamps output

        if self.__ode_integrator == 'scikits.odes':
            cvode = ode('cvode', rhs_fn, user_data=self.__ode_params, old_api=False)
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
                                                args=( self.__ode_params, ),
                                                rtol=1e-4, atol=1e-8, mxstep=200,
                                                full_output=True
                                              )

            assert info_dict['message']=='Integration successful.',\
                   'Fatal: scipy.integrate.odeint failed %r'%info_dict['message']

            u_vec = u_vec_hist[1,:]  # solution vector at final time step
        else:
            assert False, 'Fatal: invalid ode integrator config. %r'%self.__ode_integrator


        values = self.__liquid_phase.GetRow( at_time ) # values at previous time

        at_time = at_time + at_time_step

        self.__liquid_phase.AddRow( at_time, values ) # repeat values for current time

        if u_vec[2] <= 0.0: # ground impact bounces the drop to a different height near 
                            # original
            position = self.__liquid_phase.GetValue( 'position', self.__start_time )
            bounced_position = position[2] * npy.random.random(1)
            #bounced_position = position[2]
            u_vec[2]  = bounced_position
            u_vec[3:] = 0.0  # zero velocity

        self.__liquid_phase.SetValue( 'position', u_vec[0:3], at_time ) # update current values
        self.__liquid_phase.SetValue( 'velocity', u_vec[3:], at_time ) # update current values
        self.__liquid_phase.SetValue( 'speed', npy.linalg.norm(u_vec[3:]), at_time ) # update current values
        self.__liquid_phase.SetValue( 'radial-position', npy.linalg.norm(u_vec[0:2]), at_time ) # update current values

        return

    def __vortex_velocity( self, position ):
        '''
        Computes the velocity of the flow at a given position.

        Parameters
        ----------
        position: numpy.ndarray(3)

        Returns
        -------
        flow_velocity: numpy.ndarray(3)
        '''

        # Compute the flow velocity at the given external position
        # Using a vortex flow model.
        box_half_length = self.__box_half_length
        min_core_radius = self.__min_core_radius
        outer_v_theta   = self.__outer_v_theta

        outer_cylindrical_radius = math.hypot(box_half_length,box_half_length)
        circulation = 2*math.pi * outer_cylindrical_radius * outer_v_theta   # m^2/s

        core_radius = min_core_radius

        x = position[0]
        y = position[1]
        z = position[2]

        relax_length = self.__box_height/2.0
        z_relax_factor = math.exp(-(self.__box_height-z)/relax_length)
        v_z = self.__v_z_0 * z_relax_factor

        cylindrical_radius = math.hypot(x,y)
        azimuth = math.atan2(y,x)

        v_theta = ( 1 - math.exp(-cylindrical_radius**2/8/core_radius**2) ) *\
                   circulation/2/math.pi/max(cylindrical_radius,min_core_radius) *\
                   z_relax_factor

        v_x = - v_theta * math.sin(azimuth)
        v_y =   v_theta * math.cos(azimuth)

        flow_velocity = npy.array([v_x,v_y,v_z])

        return flow_velocity

    def __plot_vortex_velocity( self ):
        '''
        Plot the vortex velocity function.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''

        import matplotlib.pyplot as plt
        (fig,axs) = plt.subplots(2,1)
        fig.subplots_adjust(hspace=0.5)

        for z in npy.flip( npy.linspace(0,self.__box_height,3), 0 ):
            xval = list()
            yval = list()
            for x in npy.linspace(0,self.__box_half_length,500):
                xval.append(x)
                y = 0.0
                flow_velocity = self.__vortex_velocity( npy.array([x,y,z]) )
                yval.append(flow_velocity[1])

            axs[0].plot( xval, yval, label='z ='+str(round(z,2))+' [m]' )

        axs[0].set_xlabel('Radial distance [m]')
        axs[0].set_ylabel('Tangential speed [m/s]')
        axs[0].legend(loc='best')
        fig.suptitle('Vortex Flow')
        axs[0].grid(True)

        xval = list()
        yval = list()
        for z in npy.linspace(0,self.__box_height,50):
            yval.append(z)
            flow_velocity = self.__vortex_velocity( npy.array([0.0,0.0,z]) )
            xval.append(flow_velocity[2])

        axs[1].plot(xval,yval)

        axs[1].set_xlabel('Vertical speed [m/s]')
        axs[1].set_ylabel('Height [m]')
        axs[1].grid(True)

        fig.savefig('vortex_droplet_'+str(self.__slot_id)+'.png',dpi=200,format='png')

        return

    def __read_manifesto( self, xml_tree_file ):
        '''
        Parse the manifesto
        '''

        assert isinstance(xml_tree_file, str)

        # Read the manifesto
        xml_tree = XMLTree( xml_tree_file=xml_tree_file )

        assert xml_tree.tag == 'module_manifesto'

        assert xml_tree.get_attribute('name') == 'droplet'

        # List of (port_name, port_type, port_mode, port_multiplicity)
        __ports = list()

        self.__port_diagram = 'null-module-port-diagram'

        # Get manifesto data  
        for child in xml_tree.children:

            (elem, tag, attributes, text) = child

            if tag == 'port':

                text = text.strip()

                assert len(attributes) == 3, "only <= 3 attributes allowed."

                tmp = dict()  # store port name and three attributes

                for attribute in attributes:
                    key = attribute[0].strip()
                    val = attribute[1].strip()

                    if key == 'type':
                        assert val == 'use' or val == 'provide', \
                                'port attribute value invalid.'
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

#======================= end class Droplet =======================================