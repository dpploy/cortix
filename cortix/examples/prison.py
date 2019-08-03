#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org

import pickle

import numpy as np
import scipy.constants as const
from scipy.integrate import odeint
from cortix.src.module import Module
from cortix.support.quantity import Quantity

class Prison(Module):
    '''
    Prison Cortix module used to model criminal group population in a prison.

    Note
    ----
    `parole`: this is a `port` for the rate of population groups to/from the
        parole domain.

    `street`: this is a `port` for the rate of population groups to/from the Street
        (Awaiting Adjugation) domain.

    `jail`: this is a `port` for the rate of population groups to/from the Jail
        domain module.
    '''

    def __init__(self):

        super().__init__()

        quantities = list()
        self.ode_params = dict()

        self.initial_time = 0.0
        self.end_time = 100
        self.time_step = 0.1

        # Population group 1
        factor = 100.0
        g1_prison = Quantity(name='g1-prison', formalName='grp-1-prison',
                unit='individual', value=np.random.random()*factor)
        quantities.append(g1_prison)

        g2_prison = Quantity(name='g2-prison', formalName='grp-2-prison',
                unit='individual', value=np.random.random()*factor)
        quantities.append(g2_prison)

        g3_prison = Quantity(name='g3-prison', formalName='grp-3-prison',
                unit='individual', value=np.random.random()*factor)
        quantities.append(g3_prison)

        factor = 80.0
        g1_parole = Quantity(name='g1-parole', formalName='grp-1-parole',
                unit='individual', value=np.random.random()*factor)
        quantities.append(g1_parole)

        factor = 30.0
        g2_street = Quantity(name='g2-street', formalName='grp-2-street',
                unit='individual', value=np.random.random()*factor)
        quantities.append(g2_street)

        factor = 30.0
        g3_street = Quantity(name='g3-street', formalName='grp-3-street',
                unit='individual', value=np.random.random()*factor)
        quantities.append(g3_street)

        factor = 20.0
        g1_jail = Quantity(name='g1-jail', formalName='grp-1-jail',
                unit='individual', value=np.random.random()*factor)
        quantities.append(g1_jail)

        g2_jail = Quantity(name='g2-jail', formalName='grp-2-jail',
                unit='individual', value=np.random.random()*factor)
        quantities.append(g2_jail)

        g3_jail = Quantity(name='g3-jail', formalName='grp-3-jail',
                unit='individual', value=np.random.random()*factor)
        quantities.append(g3_jail)

        # Model parameters (group- and time-dependent)
        self.prison_unconditional_release_rate = 0.2
        self.ode_params['prison-unconditional-release-rate'] =
                self.prison_unconditional_release_rate

        self.prison_release_rate_mod = 0.12
        self.ode_params['prison-release-rate-mod'] = self.prison_release_rate_mod

        self.parole_rate = 0.11
        self.ode_params['parole-rate'] = self.parole_rate

        self.parole_rate_mod = 0.08
        self.ode_params['parole-rate-mod'] = self.parole_rate_mod

        return

    def run(self, state_comm=None, idx_comm=None):

        time = self.initial_time

        while time < self.end_time:

            # Interactions in the parole port
            #--------------------------------

            self.send( time )

            (check_time, g1_parole_return_rate) = recv('parole')

            assert abs(check_time-time) <= 1e-6
            self.ode_params['g1_parole_return_rate'] = g1_parole_return_rate

            # Evolve prison group population to the next time stamp
            #------------------------------------------------------

            time = self.step( time )

        if state_comm:
            try:
                pickle.dumps(self.state)
            except pickle.PicklingError:
                state_comm.put((idx_comm,None))
            else:
                state_comm.put((idx_comm,self.state))

    def rhs_fn(self, u_vec, t, params):
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

    def step(self, time=0.0):
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

        x_0 = self.liquid_phase.GetValue('position', time)
        v_0 = self.liquid_phase.GetValue('velocity', time)
        u_vec_0 = np.concatenate((x_0,v_0))
        t_interval_sec = np.linspace(0.0, self.time_step, num=2)

        (u_vec_hist, info_dict) = odeint(self.rhs_fn,
                                         u_vec_0, t_interval_sec,
                                         args=( self.ode_params, ),
                                         rtol=1e-4, atol=1e-8, mxstep=200,
                                         full_output=True)

        assert info_dict['message'] =='Integration successful.', info_dict['message']

        u_vec = u_vec_hist[1,:]  # solution vector at final time step
        values = self.liquid_phase.GetRow(time) # values at previous time

        time += self.time_step

        self.liquid_phase.AddRow(time, values)

        # Ground impact with bouncing drop
        if u_vec[2] <= 0.0 and self.bounce:
            position = self.liquid_phase.GetValue('position', self.initial_time)
            bounced_position = position[2] * np.random.random(1)
            u_vec[2]  = bounced_position
            u_vec[3:] = 0.0  # zero velocity
        # Ground impact with no bouncing drop and slip velocity
        elif u_vec[2] <= 0.0 and not self.bounce and self.slip:
            u_vec[2]  = 0.0
        elif u_vec[2] <= 0.0 and not self.bounce and not self.slip:
            u_vec[2]  = 0.0
            u_vec[3:] = 0.0  # zero velocity

        # Update current values
        self.liquid_phase.SetValue('position', u_vec[0:3], time)
        self.liquid_phase.SetValue('velocity', u_vec[3:], time)
        self.liquid_phase.SetValue('speed', np.linalg.norm(u_vec[3:]), time)
        self.liquid_phase.SetValue('radial-position', np.linalg.norm(u_vec[0:2]), time)

        return time
