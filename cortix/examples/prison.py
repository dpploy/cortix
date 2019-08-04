#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org

import pickle

import numpy as np
import scipy.constants as const
from scipy.integrate import odeint
from cortix.src.module import Module
from cortix.support.phase import Phase
from cortix.support.quantity import Quantity

class Prison(Module):
    '''
    Prison Cortix module used to model criminal group population in a prison.

    Note
    ----
    `parole`: this is a `port` for the rate of population groups to/from the
        parole domain.

    `adjudication`: this is a `port` for the rate of population groups to/from the
        Adjudication (Awaiting Adjudication) domain.

    `jail`: this is a `port` for the rate of population groups to/from the Jail
        domain module.

    `community`: this is a `port` for the rate of population groups to/from the Community
        domain module.

    `visualization`: this is a `port` that sends data to a visualization module.
    '''

    def __init__(self, n_groups=1):

        super().__init__()

        quantities      = list()
        self.ode_params = dict()

        self.initial_time = 0.0 * const.day
        self.end_time     = 100 * const.day
        self.time_step    = 0.5 * const.day

        # Population groups
        self.n_groups = n_groups
        factor = 0.0

        # Prison population groups
        fpg_0 = np.random.random(self.n_groups) * factor
        fpg = Quantity(name='fpg', formalName='prison-pop-grps',
                unit='individual', value=fpg_0)
        quantities.append(fpg)

        # Model parameters: commitment coefficients and their modifiers

        # Prison to community
        cp0g_0 = np.random.random(self.n_groups) / const.day
        cp0g = Quantity(name='cp0g', formalName='commit-community-coeff-grps',
               unit='individual', value=cp0g_0)
        self.ode_params['commit-to-community-coeff-grps'] = cp0g_0
        quantities.append(cp0g)

        mp0g_0 = np.random.random(self.n_groups)
        mp0g = Quantity(name='mp0g', formalName='commit-community-coeff-mod-grps',
               unit='individual', value=mp0g_0)
        self.ode_params['commit-to-community-coeff-mod-grps'] = mp0g_0
        quantities.append(mp0g)

        # Prison to parole  
        cpeg_0 = np.random.random(self.n_groups) / const.day
        cpeg = Quantity(name='cpeg', formalName='commit-parole-coeff-grps',
               unit='individual', value=cpeg_0)
        self.ode_params['commit-to-parole-coeff-grps'] = cpeg_0
        quantities.append(cpeg)

        mpeg_0 = np.random.random(self.n_groups)
        mpeg = Quantity(name='mpeg', formalName='commit-parole-coeff-mod-grps',
               unit='individual', value=mpeg_0)
        self.ode_params['commit-to-parole-coeff-mod-grps'] = mpeg_0
        quantities.append(mpeg)

        # Death term
        self.ode_params['prison-death-rates'] = np.zeros(self.n_groups)

        # Phase state
        self.population_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        self.population_phase.SetValue('fpg', fpg_0, self.initial_time)

        # Set the state to the phase state
        self.state = self.population_phase

        return

    def run(self, state_comm=None, idx_comm=None):

        time = self.initial_time

        while time < self.end_time:

            # Interactions in the parole port
            #--------------------------------
            # two way "from" and "to" parole

            # from
            self.send( time, 'parole' )
            (check_time, parole_inflow_rates) = self.recv('parole')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['parole-inflow-rates'] = parole_inflow_rates

            # to
            message_time = self.recv('parole')
            parole_outflow_rates = self.compute_outflow_rates( message_time, 'parole' )
            self.send( (message_time, parole_outflow_rates), 'parole' )

            # Interactions in the adjudication port
            #------------------------------------
            # one way "from" adjudication

            self.send( time, 'adjudication' )
            (check_time, adjudication_inflow_rates) = self.recv('adjudication')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['adjudication-inflow-rates'] = adjudication_inflow_rates

            # Interactions in the jail port
            #------------------------------
            # one way "from" prison

            self.send( time, 'jail' )
            (check_time, jail_inflow_rates) = self.recv('jail')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['jail-inflow-rates'] = jail_inflow_rates

            # Interactions in the community port
            #------------------------------

            # compute community outflow rate

            # Interactions in the visualization port
            #---------------------------------------

            fpg = self.population_phase.GetValue('fpg')
            self.send( fpg, 'visualization' )

            # Evolve prison group population to the next time stamp
            #------------------------------------------------------

            time = self.step( time )

        self.send('DONE', 'visualization') # this should not be needed: TODO

        if state_comm:
            try:
                pickle.dumps(self.state)
            except pickle.PicklingError:
                state_comm.put((idx_comm,None))
            else:
                state_comm.put((idx_comm,self.state))

    def rhs_fn(self, u_vec, t, params):

        fpg = u_vec  # prison population groups

        parole_inflow_rates     = params['parole-inflow-rates']
        adjudication_inflow_rates = params['adjudication-inflow-rates']
        jail_inflow_rates       = params['jail-inflow-rates']

        inflow_rates  = parole_inflow_rates + adjudication_inflow_rates + jail_inflow_rates

        cp0g = self.ode_params['commit-to-community-coeff-grps']
        mp0g = self.ode_params['commit-to-community-coeff-mod-grps']

        cpeg = self.ode_params['commit-to-parole-coeff-grps']
        mpeg = self.ode_params['commit-to-parole-coeff-mod-grps']

        outflow_rates = ( cp0g * mp0g + cpeg * mpeg ) * fpg

        death_rates = params['prison-death-rates']

        dt_fpg = inflow_rates - outflow_rates - death_rates

        return dt_fpg

    def step(self, time=0.0):
        r'''
        ODE IVP problem:
        Given the initial data at :math:`t=0`,
        :math:`u = (u_1(0),u_2(0),\ldots)`
        solve :math:`\frac{\text{d}u}{\text{d}t} = f(u)` in the interval
        :math:`0\le t \le t_f`.

        Parameters
        ----------
        time: float
            Time in the droplet unit of time (seconds).

        Returns
        -------
        None
        '''

        u_vec_0 = self.population_phase.GetValue('fpg', time)
        t_interval_sec = np.linspace(0.0, self.time_step, num=2)

        (u_vec_hist, info_dict) = odeint(self.rhs_fn,
                                         u_vec_0, t_interval_sec,
                                         args=( self.ode_params, ),
                                         rtol=1e-4, atol=1e-8, mxstep=200,
                                         full_output=True)

        assert info_dict['message'] =='Integration successful.', info_dict['message']

        u_vec = u_vec_hist[1,:]  # solution vector at final time step
        values = self.population_phase.GetRow(time) # values at previous time

        time += self.time_step

        self.population_phase.AddRow(time, values)

        # Update current values
        self.population_phase.SetValue('fpg', u_vec, time)

        return time

    def compute_outflow_rates(self, time, name):

        fpg = self.population_phase.GetValue('fpg',time)

        if name == 'parole':

            cpeg = self.ode_params['commit-to-parole-coeff-grps']
            mpeg = self.ode_params['commit-to-parole-coeff-mod-grps']

            outflow_rates = cpeg * mpeg * fpg

            return outflow_rates

        if name == 'community':

            cp0g = self.ode_params['commit-to-community-coeff-grps']
            mp0g = self.ode_params['commit-to-community-coeff-mod-grps']

            outflow_rates = cp0g * mp0g * fpg

            return outflow_rates
