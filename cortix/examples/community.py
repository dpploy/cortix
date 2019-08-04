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

class Community(Module):
    '''
    Community Cortix module used to model criminal group population in a community system.

    Note
    ----
    `probation`: this is a `port` for the rate of population groups to/from the
        Probation domain.

    `adjudication`: this is a `port` for the rate of population groups to/from the
        Adjudication domain.

    `jail`: this is a `port` for the rate of population groups to/from the
        Jail domain.

    `prison`: this is a `port` for the rate of population groups to/from the Prison
        domain module.

    `arrested`: this is a `port` for the rate of population groups to/from the Arrested
        domain module.

    `parole`: this is a `port` for the rate of population groups to/from the Parole
        domain module.

    `visualization`: this is a `port` that sends data to a visualization module.
    '''

    def __init__(self, n_groups=1, comm_pool_size=0.0, offender_pool_size=0.0):

        super().__init__()

        quantities      = list()
        self.ode_params = dict()

        self.initial_time = 0.0 * const.day
        self.end_time     = 100 * const.day
        self.time_step    = 0.5 * const.day

        self.show_time = (False,10*const.day)

        # Population groups
        self.n_groups = n_groups

        # Whole community population
        f0_0 = comm_pool_size
        f0 = Quantity(name='f0', formalName='comm-pop',
                unit='individual', value=f0_0)
        self.ode_params['f0'] = f0_0
        quantities.append(f0)

        # Community population groups
        f0g_0 = np.random.random(self.n_groups) * offender_pool_size
        f0g = Quantity(name='f0g', formalName='offender-pop-grps',
                unit='individual', value=f0g_0)
        quantities.append(f0g)

        # Model parameters: commitment coefficients and their modifiers

        # Community general to arrested
        c00g_0 = np.random.random(self.n_groups) / const.day
        c00g = Quantity(name='c00g', formalName='commit-arrested-coeff-grps',
               unit='individual', value=c00g_0)
        self.ode_params['general-commit-to-arrested-coeff-grps'] = c00g_0
        quantities.append(c00g)

        m00g_0 = np.random.random(self.n_groups) / const.day
        m00g = Quantity(name='m00g', formalName='commit-arrested-coeff-mod-grps',
               unit='individual', value=m00g_0)
        self.ode_params['general-commit-to-arrested-coeff-mod-grps'] = m00g_0
        quantities.append(m00g)

        # Community offenders to arrested
        c0rg_0 = np.random.random(self.n_groups) / const.day
        c0rg = Quantity(name='c0rg', formalName='commit-arrested-coeff-grps',
               unit='individual', value=c0rg_0)
        self.ode_params['commit-to-arrested-coeff-grps'] = c0rg_0
        quantities.append(c0rg)

        m0rg_0 = np.random.random(self.n_groups)
        m0rg = Quantity(name='m0rg', formalName='commit-arrested-coeff-mod-grps',
               unit='individual', value=m0rg_0)
        self.ode_params['commit-to-arrested-coeff-mod-grps'] = m0rg_0
        quantities.append(m0rg)

        # Death term
        self.ode_params['community-death-rates'] = np.zeros(self.n_groups)

        # Phase state
        self.population_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        self.population_phase.SetValue('f0g', f0g_0, self.initial_time)
        self.population_phase.SetValue('f0', f0_0, self.initial_time)

        # Set the state to the phase state
        self.state = self.population_phase

        return

    def run(self, state_comm=None, idx_comm=None):

        time = self.initial_time

        while time < self.end_time:

            if self.show_time[0] and abs(time%self.show_time[1]-0.0)<=1.e-1:
                print('Community::time[d] =',round(time,1)/const.day)

            # Interactions in the jail port
            #--------------------------------
            # one way "from" jail

            self.send( time, 'jail' )
            (check_time, jail_inflow_rates) = self.recv('jail')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['jail-inflow-rates'] = jail_inflow_rates

            # Interactions in the adjudication port
            #--------------------------------------
            # one way "from" adjudication

            self.send( time, 'adjudication' )
            (check_time, adjudication_inflow_rates) = self.recv('adjudication')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['adjudication-inflow-rates'] = adjudication_inflow_rates

            # Interactions in the probation port
            #--------------------------------
            # one way "from" probation

            self.send( time, 'probation' )
            (check_time, probation_inflow_rates) = self.recv('probation')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['probation-inflow-rates'] = probation_inflow_rates

            # Interactions in the prison port
            #--------------------------------
            # one way "from" prison

            self.send( time, 'prison' )
            (check_time, prison_inflow_rates) = self.recv('prison')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['prison-inflow-rates'] = prison_inflow_rates

            # Interactions in the parole port
            #--------------------------------
            # one way "from" parole

            self.send( time, 'parole' )
            (check_time, parole_inflow_rates) = self.recv('parole')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['parole-inflow-rates'] = parole_inflow_rates

            # Interactions in the arrested port
            #--------------------------------
            # two way "to" and "from" arrested

            # to
            message_time = self.recv('arrested')
            outflow_rates = self.compute_outflow_rates( message_time, 'arrested' )
            self.send( (message_time, outflow_rates), 'arrested' )

            # from
            self.send( time, 'arrested' )
            (check_time, arrested_inflow_rates) = self.recv('arrested')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['arrested-inflow-rates'] = arrested_inflow_rates

            # Interactions in the visualization port
            #---------------------------------------

            f0g = self.population_phase.GetValue('f0g')
            self.send( f0g, 'visualization' )

            # Evolve offenders group population to the next time stamp
            #---------------------------------------------------------

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

        f0g = u_vec  # offender population groups

        prison_inflow_rates       = params['prison-inflow-rates']
        parole_inflow_rates       = params['parole-inflow-rates']
        arrested_inflow_rates     = params['arrested-inflow-rates']
        jail_inflow_rates         = params['jail-inflow-rates']
        adjudication_inflow_rates = params['adjudication-inflow-rates']
        probation_inflow_rates    = params['probation-inflow-rates']

        inflow_rates = prison_inflow_rates + parole_inflow_rates +\
                       arrested_inflow_rates + jail_inflow_rates +\
                       adjudication_inflow_rates + probation_inflow_rates

        c0rg = self.ode_params['commit-to-arrested-coeff-grps']
        m0rg = self.ode_params['commit-to-arrested-coeff-mod-grps']

        c00g = self.ode_params['general-commit-to-arrested-coeff-grps']
        m00g = self.ode_params['general-commit-to-arrested-coeff-mod-grps']

        f0 = self.ode_params['f0']

        outflow_rates = c0rg * m0rg * f0g + c00g * m00g * f0

        death_rates = params['community-death-rates']

        dt_f0g = inflow_rates - outflow_rates - death_rates

        return dt_f0g

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

        u_vec_0 = self.population_phase.GetValue('f0g', time)
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
        self.population_phase.SetValue('f0g', u_vec, time)

        return time

    def compute_outflow_rates(self, time, name):

        f0g = self.population_phase.GetValue('f0g',time)
        f0  = self.population_phase.GetValue('f0',time)

        if name == 'arrested':

            c0rg = self.ode_params['commit-to-arrested-coeff-grps']
            m0rg = self.ode_params['commit-to-arrested-coeff-mod-grps']

            c00g = self.ode_params['commit-to-arrested-coeff-grps']
            m00g = self.ode_params['commit-to-arrested-coeff-mod-grps']

            outflow_rates = c0rg * m0rg * f0g + c00g * m00g * f0

            return outflow_rates
