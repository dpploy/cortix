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

class Arrested(Module):
    '''
    Arrested Cortix module used to model criminal group population in a arrested system.

    Note
    ----
    `probation`: this is a `port` for the rate of population groups to/from the
        Probation domain.

    `adjudication`: this is a `port` for the rate of population groups to/from the
        Adjudication domain.

    `jail`: this is a `port` for the rate of population groups to/from the
        Jail domain.

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

        # Arrested population groups
        frg_0 = np.random.random(self.n_groups) * factor
        frg = Quantity(name='frg', formalName='arrested-pop-grps',
                unit='individual', value=frg_0)
        quantities.append(frg)

        # Model parameters: commitment coefficients and their modifiers

        # Arrested to community
        cr0g_0 = np.random.random(self.n_groups) / const.day
        cr0g = Quantity(name='cr0g', formalName='commit-community-coeff-grps',
               unit='individual', value=cr0g_0)
        self.ode_params['commit-to-community-coeff-grps'] = cr0g_0
        quantities.append(cr0g)

        mr0g_0 = np.random.random(self.n_groups)
        mr0g = Quantity(name='mr0g', formalName='commit-community-coeff-mod-grps',
               unit='individual', value=mr0g_0)
        self.ode_params['commit-to-community-coeff-mod-grps'] = mr0g_0
        quantities.append(mr0g)

        # Arrested to probation  
        crbg_0 = np.random.random(self.n_groups) / const.day
        crbg = Quantity(name='crbg', formalName='commit-probation-coeff-grps',
               unit='individual', value=crbg_0)
        self.ode_params['commit-to-probation-coeff-grps'] = crbg_0
        quantities.append(crbg)

        mrbg_0 = np.random.random(self.n_groups)
        mrbg = Quantity(name='mrbg', formalName='commit-probation-coeff-mod-grps',
               unit='individual', value=mrbg_0)
        self.ode_params['commit-to-probation-coeff-mod-grps'] = mrbg_0
        quantities.append(mrbg)

        # Arrested to jail  
        crjg_0 = np.random.random(self.n_groups) / const.day
        crjg = Quantity(name='crjg', formalName='commit-jail-coeff-grps',
               unit='individual', value=crjg_0)
        self.ode_params['commit-to-jail-coeff-grps'] = crjg_0
        quantities.append(crjg)

        mrjg_0 = np.random.random(self.n_groups)
        mrjg = Quantity(name='mrjg', formalName='commit-jail-coeff-mod-grps',
               unit='individual', value=mrjg_0)
        self.ode_params['commit-to-jail-coeff-mod-grps'] = mrjg_0
        quantities.append(mrjg)

        # Arrested to adjudication
        crag_0 = np.random.random(self.n_groups) / const.day
        crag = Quantity(name='crag', formalName='commit-adjudication-coeff-grps',
               unit='individual', value=crag_0)
        self.ode_params['commit-to-adjudication-coeff-grps'] = crag_0
        quantities.append(crag)

        mrag_0 = np.random.random(self.n_groups)
        mrag = Quantity(name='mrag', formalName='commit-adjudication-coeff-mod-grps',
               unit='individual', value=mrag_0)
        self.ode_params['commit-to-adjudication-coeff-mod-grps'] = mrag_0
        quantities.append(mrag)

        # Death term
        self.ode_params['arrested-death-rates'] = np.zeros(self.n_groups)

        # Phase state
        self.population_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        self.population_phase.SetValue('frg', frg_0, self.initial_time)

        # Set the state to the phase state
        self.state = self.population_phase

        return

    def run(self, state_comm=None, idx_comm=None):

        time = self.initial_time

        while time < self.end_time:


            # Interactions in the jail port
            #--------------------------------
            # one way "to" jail

            message_time = self.recv('jail')
            jail_outflow_rates = self.compute_outflow_rates( message_time,
                    'jail' )
            self.send( (message_time, jail_outflow_rates), 'jail' )

            # Interactions in the adjudication port
            #--------------------------------------
            # one way "to" adjudication

            message_time = self.recv('adjudication')
            adjudication_outflow_rates = self.compute_outflow_rates( message_time,
                    'adjudication' )
            self.send( (message_time, adjudication_outflow_rates), 'adjudication' )

            # Interactions in the probation port
            #--------------------------------
            # one way "to" probation

            message_time = self.recv('probation')
            probation_outflow_rates = self.compute_outflow_rates( message_time,
                    'probation' )
            self.send( (message_time, probation_outflow_rates), 'probation' )

            # Interactions in the community port
            #---------------------------------
            # two way "from" and "to"

            # compute community outflow rate

            self.ode_params['community-inflow-rates'] = np.ones(self.n_groups)/const.day

            # Interactions in the visualization port
            #---------------------------------------

            frg = self.population_phase.GetValue('frg')
            self.send( frg, 'visualization' )

            # Evolve arrested group population to the next time stamp
            #--------------------------------------------------------

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

        frg = u_vec  # arrested population groups

        community_inflow_rates = params['community-inflow-rates']

        inflow_rates  = community_inflow_rates

        cr0g = self.ode_params['commit-to-community-coeff-grps']
        mr0g = self.ode_params['commit-to-community-coeff-mod-grps']

        crbg = self.ode_params['commit-to-probation-coeff-grps']
        mrbg = self.ode_params['commit-to-probation-coeff-mod-grps']

        crjg = self.ode_params['commit-to-jail-coeff-grps']
        mrjg = self.ode_params['commit-to-jail-coeff-mod-grps']

        crag = self.ode_params['commit-to-adjudication-coeff-grps']
        mrag = self.ode_params['commit-to-adjudication-coeff-mod-grps']

        outflow_rates = ( cr0g * mr0g + crbg * mrbg + crjg * mrjg + crag * mrag ) * frg

        death_rates = params['arrested-death-rates']

        dt_frg = inflow_rates - outflow_rates - death_rates

        return dt_frg

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

        u_vec_0 = self.population_phase.GetValue('frg', time)
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
        self.population_phase.SetValue('frg', u_vec, time)

        return time

    def compute_outflow_rates(self, time, name):

        frg = self.population_phase.GetValue('frg',time)

        if name == 'probation':

            crbg = self.ode_params['commit-to-probation-coeff-grps']
            mrbg = self.ode_params['commit-to-probation-coeff-mod-grps']

            outflow_rates = crbg * mrbg * frg

            return outflow_rates

        if name == 'jail':

            crjg = self.ode_params['commit-to-jail-coeff-grps']
            mrjg = self.ode_params['commit-to-jail-coeff-mod-grps']

            outflow_rates = crjg * mrjg * frg

            return outflow_rates

        if name == 'adjudication':

            crag = self.ode_params['commit-to-adjudication-coeff-grps']
            mrag = self.ode_params['commit-to-adjudication-coeff-mod-grps']

            outflow_rates = crag * mrag * frg

            return outflow_rates

        if name == 'community':

            cr0g = self.ode_params['commit-to-community-coeff-grps']
            mr0g = self.ode_params['commit-to-community-coeff-mod-grps']

            outflow_rates = cr0g * mr0g * frg

            return outflow_rates
