#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org

import pickle
import logging
import numpy as np
import scipy.constants as const
from scipy.integrate import odeint
from cortix.src.module import Module
from cortix.support.phase import Phase
from cortix.support.specie import Specie
from cortix.support.quantity import Quantity

class Droplet(Module):
    '''
    Droplet Cortix module used to model very simple fluid-particle interactions.

    Notes
    -----
    Port names used in this module: `external-flow` exchanges data with any other
    module that provides information about the flow outside the droplet,
    `visualization` sends data to a visualization module.
    '''

    def __init__(self):
        '''
        Attributes
        ----------
        initial_time: float
        end_time: float
        time_step: float
        show_time: tuple
            Two-element tuple, `(bool,float)`, `True` will print to standard
            output.
        '''

        super().__init__()

        self.port_names_expected = ['external-flow','visualization']

        self.initial_time = 0.0
        self.end_time = 100
        self.time_step = 0.1
        self.show_time = (False,1*const.minute)

        self.bounce = True
        self.slip   = True

        species = list()
        quantities = list()

        self.ode_params = dict()

        # Create a drop with random diameter up within 5 and 8 mm.
        self.droplet_diameter = (np.random.random(1) * (8 - 5) + 5)[0] * const.milli
        self.ode_params['droplet-diameter'] = self.droplet_diameter
        self.ode_params['droplet-xsec-area'] = np.pi * (self.droplet_diameter/2.0)**2
        self.ode_params['gravity'] = const.g

        # Species in the liquid phase
        water = Specie(name='water', formula_name='H2O(l)', phase='liquid', \
                atoms=['2*H','O'])
        water.massCC =  0.99965 # [g/cc]
        water.massCCUnit = 'g/cc'
        water.molarCCUnit = 'mole/cc'
        species.append(water)

        droplet_mass = 4/3 * np.pi * (self.droplet_diameter/2)**3 * water.massCC * \
                const.gram / const.centi**3  # [kg]
        self.ode_params['droplet-mass'] = droplet_mass

        # Spatial position
        x_0 = np.zeros(3)
        position = Quantity(name='position', formalName='Pos.', unit='m', value=x_0)
        quantities.append(position)

        # Velocity
        v_0 = np.zeros(3)
        velocity = Quantity(name='velocity', formalName='Veloc.', unit='m/s', value=v_0)
        quantities.append(velocity)

        # Speed
        speed = Quantity(name='speed', formalName='Speed', unit='m/s', value=0.0)
        quantities.append(speed)

        # Radial position
        radial_pos = Quantity(name='radial-position', formalName='Radius', unit='m', \
                value=np.linalg.norm(x_0[0:2]))
        quantities.append(radial_pos)

        # Liquid phase 
        self.liquid_phase = Phase(self.initial_time, time_unit='s', species=species, \
                quantities=quantities)
        self.liquid_phase.SetValue('water', water.massCC, self.initial_time)

        # Domain box dimensions: LxLxH m^3 box with given H.
        # Origin of cartesian coordinate system at the bottom of the box. 
        # z coordinate pointing upwards. -L <= x <= L, -L <= y <= L, 
        self.box_half_length = 250.0 # L [m]
        self.box_height = 500.0 # H [m]

        # Random positioning of the droplet constrained to a box sub-region.
        x_0 = (2 * np.random.random(3) - np.ones(3)) * self.box_half_length / 4.0
        x_0[2] = self.box_height
        self.liquid_phase.SetValue('position', x_0, self.initial_time)

        # Droplet Initial velocity = 0 -> placed still in the flow
        self.liquid_phase.SetValue('velocity', np.array([0.0,0.0,0.0]), \
                self.initial_time)

        # Default value for the medium surrounding the droplet if data is not passed
        # through a conneted port.
        medium_mass_density = 0.1 * const.gram / const.centi**3 # [kg/m^3]
        self.ode_params['medium-mass-density'] = medium_mass_density

        medium_displaced_mass = 4/3 * np.pi * (self.droplet_diameter/2)**3 * \
                medium_mass_density # [kg]
        self.ode_params['medium-displaced-mass'] = medium_displaced_mass

        medium_dyn_viscosity = 1.81e-5 # kg/(m s)
        self.ode_params['medium-dyn-viscosity'] = medium_dyn_viscosity

    def run(self, *args):

        time = self.initial_time

        self.bottom_impact = False

        while time < self.end_time:

            # Interactions in the external-flow port
            #---------------------------------------

            position = self.liquid_phase.GetValue('position')
            self.send( (time,position), 'external-flow' )

            (check_time, velocity,fluid_props) = self.recv( 'external-flow' )

            assert abs(check_time-time) <= 1e-6
            self.ode_params['flow-velocity'] = velocity
            #medium_mass_density  = fluid_props.mass_density  # see Vortex
            #medium_dyn_viscosity = fluid_props.dyn_viscosity # see Vortex
            medium_mass_density  = fluid_props[0]
            medium_dyn_viscosity = fluid_props[1]

            self.ode_params['medium-mass-density'] = medium_mass_density

            medium_displaced_mass = 4/3 * np.pi * (self.droplet_diameter/2)**3 * \
                    medium_mass_density # [kg]
            self.ode_params['medium-displaced-mass'] = medium_displaced_mass

            self.ode_params['medium-dyn-viscosity'] = medium_dyn_viscosity

            # Interactions in the visualization port
            #---------------------------------------

            self.send( position, 'visualization' )

            # Evolve droplet state to next time stamp
            #----------------------------------------

            time = self.__step( time )

        self.send('DONE', 'visualization') # this should not be needed: TODO
        return

    def __rhs_fn(self, u_vec, t, params):
        drop_pos = u_vec[:3]
        flow_velo = params['flow-velocity']

        drop_velo = u_vec[3:]
        relative_velo = drop_velo - flow_velo
        relative_velo_mag = np.linalg.norm(relative_velo)
        area = params['droplet-xsec-area']
        diameter = params['droplet-diameter']
        dyn_visco = params['medium-dyn-viscosity']
        rho_flow = params['medium-mass-density']

        # Calculate the friction factor
        reynolds_num = rho_flow * relative_velo_mag * diameter / dyn_visco
        if reynolds_num <= 0.0:
            fric_factor = 0.0
        elif reynolds_num < 0.1:
            fric_factor = 24 / reynolds_num
        elif reynolds_num >= 0.1 and reynolds_num < 6000.0:
            fric_factor = (np.sqrt(24 / reynolds_num) + 0.5407)**2
        elif reynolds_num >= 6000:
            fric_factor = 0.44

        drag = - fric_factor * area * rho_flow * relative_velo_mag * relative_velo / 2.0

        gravity = params['gravity']
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

    def __step(self, time=0.0):
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
        time: float
            Time in the droplet unit of time (seconds).

        Returns
        -------
        None
        '''

        if not self.bottom_impact:

           x_0 = self.liquid_phase.GetValue('position', time)
           v_0 = self.liquid_phase.GetValue('velocity', time)
           u_vec_0 = np.concatenate((x_0,v_0))

           t_interval_sec = np.linspace(0.0, self.time_step, num=2)

           (u_vec_hist, info_dict) = odeint(self.__rhs_fn,
                                            u_vec_0, t_interval_sec,
                                            args=( self.ode_params, ),
                                            rtol=1e-4, atol=1e-8, mxstep=300,
                                            full_output=True)

           assert info_dict['message'] =='Integration successful.', \
                   'At time: %r; state: %r; message: %r; full output: %r'%\
                   (round(time,2), u_vec_0, info_dict['message'], info_dict)

           u_vec = u_vec_hist[1,:]  # solution vector at final time step

        values = self.liquid_phase.GetRow(time) # values at previous time

        time += self.time_step

        self.liquid_phase.AddRow(time, values)

        if not self.bottom_impact:

            # Ground impact with bouncing drop
            if u_vec[2] <= 0.0 and self.bounce:
                position = self.liquid_phase.GetValue('position', self.initial_time)
                bounced_position = position[2] * np.random.random(1)
                u_vec[2]  = bounced_position
                u_vec[3:] = 0.0  # zero velocity
            # Ground impact with no bouncing drop and slip velocity
            elif u_vec[2] <= 0.0 and not self.bounce and self.slip:
                u_vec[2]  = 0.0  # don't bounce
            # Ground impact with no bouncing drop and no velocity
            elif u_vec[2] <= 0.0 and not self.bounce and not self.slip:
                u_vec[2]  = 0.0  # don't bounce
                u_vec[3:] = 0.0  # zero velocity
                self.bottom_impact = True

            # Update current values
            self.liquid_phase.SetValue('position', u_vec[0:3], time)
            self.liquid_phase.SetValue('velocity', u_vec[3:], time)
            self.liquid_phase.SetValue('speed', np.linalg.norm(u_vec[3:]), time)
            self.liquid_phase.SetValue('radial-position', np.linalg.norm(u_vec[0:2]),
                    time)

        return time
