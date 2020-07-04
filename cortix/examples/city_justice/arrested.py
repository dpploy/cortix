#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org

import numpy as np
import scipy.constants as unit
from scipy.integrate import odeint

from cortix import Module
from cortix import Phase
from cortix import Quantity

class Arrested(Module):
    '''
    Arrested Cortix module used to model criminal group population in an
    arrested system.

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

        self.initial_time = 0.0 * unit.day
        self.end_time     = 100 * unit.day
        self.time_step    = 0.5 * unit.day

        unit.month = 30*unit.day
        unit.percent = 1/100

        # Population groups
        self.n_groups = n_groups

        # Arrested population groups
        frg_0 = np.random.random(self.n_groups) * pool_size
        frg = Quantity(name='frg', formal_name='arrested-pop-grps',
                latex_name = '$n_r^{(g)}$',
                unit='# offenders', value=frg_0, info='Arrested Population Groups')
        quantities.append(frg)

        # Model parameters: commitment coefficients

        # Arrested to community
        a = 45*unit.percent/unit.year * np.ones(self.n_groups)
        b = 50*unit.percent/unit.year * np.ones(self.n_groups)
        cr0g_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        cr0g = Quantity(name='cr0g', formal_name='commit-community-coeff-grps',
               unit='1/s', value=cr0g_0)
        self.ode_params['commit-to-community-coeff-grps'] = cr0g_0
        quantities.append(cr0g)

        # Arrested to probation  
        a = 25*unit.percent/unit.year * np.ones(self.n_groups)
        b = 35*unit.percent/unit.year * np.ones(self.n_groups)
        crbg_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        crbg = Quantity(name='crbg', formal_name='commit-probation-coeff-grps',
               unit='1/s', value=crbg_0)
        self.ode_params['commit-to-probation-coeff-grps'] = crbg_0
        quantities.append(crbg)

        # Arrested to jail  
        a = 15*unit.percent/unit.year * np.ones(self.n_groups)
        b = 25*unit.percent/unit.year * np.ones(self.n_groups)
        crjg_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        crjg = Quantity(name='crjg', formal_name='commit-jail-coeff-grps',
               unit='1/s', value=crjg_0)
        self.ode_params['commit-to-jail-coeff-grps'] = crjg_0
        quantities.append(crjg)

        # Arrested to adjudication
        a = 35*unit.percent/unit.year * np.ones(self.n_groups)
        b = 40*unit.percent/unit.year * np.ones(self.n_groups)
        crag_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        crag = Quantity(name='crag', formal_name='commit-adjudication-coeff-grps',
               unit='1/s', value=crag_0)
        self.ode_params['commit-to-adjudication-coeff-grps'] = crag_0
        quantities.append(crag)

        # Death term
        a = 0.4*unit.percent/unit.year * np.ones(self.n_groups)
        b = 0.5*unit.percent/unit.year * np.ones(self.n_groups)
        drg_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        self.ode_params['death-rates-coeff'] = drg_0

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

        while time <= self.end_time:

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

        crbg = self.ode_params['commit-to-probation-coeff-grps']

        crjg = self.ode_params['commit-to-jail-coeff-grps']

        crag = self.ode_params['commit-to-adjudication-coeff-grps']

        outflow_rates = ( cr0g + crbg + crjg + crag ) * frg

        death_rates_coeff = params['death-rates-coeff']

        death_rates = death_rates_coeff * frg

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

            outflow_rates = crbg * frg

        if name == 'jail':

            crjg = self.ode_params['commit-to-jail-coeff-grps']

            outflow_rates = crjg * frg

        if name == 'adjudication':

            crag = self.ode_params['commit-to-adjudication-coeff-grps']

            outflow_rates = crag * frg

        if name == 'community':

            cr0g = self.ode_params['commit-to-community-coeff-grps']

            outflow_rates = cr0g * frg

        return outflow_rates

    def __zero_ode_parameters(self):
        '''
        If ports are not connected the corresponding outflows must be zero.

        '''

        zeros = np.zeros(self.n_groups)

        p_names = [p.name for p in self.ports]

        if 'community' not in p_names:
            self.ode_params['commit-to-community-coeff-grps']     = zeros

        if 'jail' not in p_names:
            self.ode_params['commit-to-jail-coeff-grps'] = zeros

        if 'probation' not in p_names:
            self.ode_params['commit-to-probation-coeff-grps'] = zeros

        if 'adjudication' not in p_names:
            self.ode_params['commit-to-adjudication-coeff-grps'] = zeros

        return
