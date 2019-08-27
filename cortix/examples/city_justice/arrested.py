#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org

import pickle

import numpy as np
import scipy.constants as const
from scipy.integrate import odeint

from cortix import Module
from cortix import Phase
from cortix import Quantity

class Arrested(Module):
    '''
    Arrested Cortix module used to model criminal group population in an arrested system.

    Notes
    -----
    These are the `port` names available in this module to connect to respective
    modules: `probation`, `adjudication`, `jail`, and `community`.
    See instance attribute `port_names_expected`.

    '''

    def __init__(self, n_groups=1, pool_size=0.0):
        '''
        Parameters
        ----------
        n_groups: int
            Number of groups in the population.
        pool_size: float
            Upperbound on the range of the existing population groups. A random value
            from 0 to the upperbound value will be assigned to each group.

        '''

        super().__init__()

        self.port_names_expected = ['probation','adjudication','jail','community']

        quantities      = list()
        self.ode_params = dict()

        self.initial_time = 0.0 * const.day
        self.end_time     = 100 * const.day
        self.time_step    = 0.5 * const.day

        # Population groups
        self.n_groups = n_groups

        # Arrested population groups
        frg_0 = np.random.random(self.n_groups) * pool_size
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
        self.ode_params['death-rates'] = np.zeros(self.n_groups)

        # Phase state
        self.population_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        self.population_phase.SetValue('frg', frg_0, self.initial_time)

        # Initialize inflows to zero
        self.ode_params['community-inflow-rates'] = np.zeros(self.n_groups)

        return

    def run(self, *args):

        self.__zero_ode_parameters()

        time = self.initial_time

        while time < self.end_time:

            # Interactions in the jail port
            #--------------------------------
            # one way "to" jail

            message_time = self.recv('jail')
            outflow_rates = self.__compute_outflow_rates( message_time, 'jail' )
            self.send( (message_time, outflow_rates), 'jail' )

            # Interactions in the adjudication port
            #--------------------------------------
            # one way "to" adjudication

            message_time = self.recv('adjudication')
            outflow_rates = self.__compute_outflow_rates( message_time, 'adjudication' )
            self.send( (message_time, outflow_rates), 'adjudication' )

            # Interactions in the probation port
            #--------------------------------
            # one way "to" probation

            message_time = self.recv('probation')
            outflow_rates = self.__compute_outflow_rates( message_time, 'probation' )
            self.send( (message_time, outflow_rates), 'probation' )

            # Interactions in the community port
            #---------------------------------
            # two way "from" and "to"

            # from
            self.send( time, 'community' )
            (check_time, community_inflow_rates) = self.recv('community')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['community-inflow-rates'] = community_inflow_rates

            # to
            message_time = self.recv('community')
            outflow_rates = self.__compute_outflow_rates( message_time, 'community' )
            self.send( (message_time, outflow_rates), 'community' )

            # Evolve arrested group population to the next time stamp
            #--------------------------------------------------------

            time = self.__step( time )

    def __rhs_fn(self, u_vec, t, params):

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

        death_rates = params['death-rates']

        dt_frg = inflow_rates - outflow_rates - death_rates

        return dt_frg

    def __step(self, time=0.0):
        r'''
        ODE IVP problem:
        Given the initial data at :math:`t=0`,
        :math:`u = (u_1(0),u_2(0),\ldots)`
        solve :math:`\frac{\text{d}u}{\text{d}t} = f(u)` in the interval
        :math:`0\le t \le t_f`.

        Parameters
        ----------
        time: float
            Time in SI units.

        Returns
        -------
        None

        '''

        u_vec_0 = self.population_phase.GetValue('frg', time)
        t_interval_sec = np.linspace(0.0, self.time_step, num=2)

        (u_vec_hist, info_dict) = odeint(self.__rhs_fn,
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

    def __compute_outflow_rates(self, time, name):

        frg = self.population_phase.GetValue('frg',time)

        assert np.all(frg>=0.0), 'values: %r'%frg

        if name == 'probation':

            crbg = self.ode_params['commit-to-probation-coeff-grps']
            mrbg = self.ode_params['commit-to-probation-coeff-mod-grps']

            outflow_rates = crbg * mrbg * frg

        if name == 'jail':

            crjg = self.ode_params['commit-to-jail-coeff-grps']
            mrjg = self.ode_params['commit-to-jail-coeff-mod-grps']

            outflow_rates = crjg * mrjg * frg

        if name == 'adjudication':

            crag = self.ode_params['commit-to-adjudication-coeff-grps']
            mrag = self.ode_params['commit-to-adjudication-coeff-mod-grps']

            outflow_rates = crag * mrag * frg

        if name == 'community':

            cr0g = self.ode_params['commit-to-community-coeff-grps']
            mr0g = self.ode_params['commit-to-community-coeff-mod-grps']

            outflow_rates = cr0g * mr0g * frg

        return outflow_rates

    def __zero_ode_parameters(self):
        '''
        If ports are not connected the corresponding outflows must be zero.

        '''

        zeros = np.zeros(self.n_groups)

        p_names = [p.name for p in self.ports]

        if 'community' not in p_names:
            self.ode_params['commit-to-community-coeff-grps']     = zeros
            self.ode_params['commit-to-community-coeff-mod-grps'] = zeros

        if 'jail' not in p_names:
            self.ode_params['commit-to-jail-coeff-grps'] = zeros
            self.ode_params['commit-to-jail-coeff-mod-grps'] = zeros

        if 'probation' not in p_names:
            self.ode_params['commit-to-probation-coeff-grps'] = zeros
            self.ode_params['commit-to-probation-coeff-mod-grps'] = zeros

        if 'adjudication' not in p_names:
            self.ode_params['commit-to-adjudication-coeff-grps'] = zeros
            self.ode_params['commit-to-adjudication-coeff-mod-grps'] = zeros

        return
