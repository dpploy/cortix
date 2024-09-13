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

class Probation(Module):
    '''
    Probation Cortix module used to model criminal group population in a probation.

    Notes
    -----
    These are the `port` names available in this module to connect to respective
    modules: `adjudication`, `jail`, `arrested`, and `community`.
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

        self.port_names_expected = ['adjudication','jail','arrested','community']

        quantities      = list()
        self.ode_params = dict()

        self.initial_time = 0.0 * unit.day
        self.end_time     = 100 * unit.day
        self.time_step    = 0.5 * unit.day

        unit.month = 30*unit.day
        unit.percent = 1/100

        # Population groups
        self.n_groups = n_groups

        # Probation population groups
        fbg_0 = np.random.random(self.n_groups) * pool_size
        fbg = Quantity(name='fbg', formal_name='probation-pop-grps',
                latex_name = '$n_b^{(g)}$',
                unit='# offenders', value=fbg_0, info='Probation Population Groups')
        quantities.append(fbg)

        # Model parameters: commitment coefficients

        # Probation to community
        a = 35*unit.percent/unit.year * np.ones(self.n_groups)
        b = 45*unit.percent/unit.year * np.ones(self.n_groups)
        cb0g_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        cb0g = Quantity(name='cb0g', formal_name='commit-community-coeff-grps',
               unit='1/s', value=cb0g_0)
        self.ode_params['commit-to-community-coeff-grps'] = cb0g_0
        quantities.append(cb0g)

        # Probation to jail
        a = 55*unit.percent/unit.year * np.ones(self.n_groups)
        b = 65*unit.percent/unit.year * np.ones(self.n_groups)
        cbjg_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        cbjg = Quantity(name='cbjg', formal_name='commit-jail-coeff-grps',
               unit='1/s', value=cbjg_0)
        self.ode_params['commit-to-jail-coeff-grps'] = cbjg_0
        quantities.append(cbjg)

        # Death term
        a = 0.5*unit.percent/unit.year * np.ones(self.n_groups)
        b = 0.7*unit.percent/unit.year * np.ones(self.n_groups)
        dbg_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        self.ode_params['probation-death-rates-coeff'] = dbg_0

        # Initialize inflows to zero
        self.ode_params['arrested-inflow-rates']     = np.zeros(self.n_groups)
        self.ode_params['adjudication-inflow-rates'] = np.zeros(self.n_groups)

        # Phase state
        self.population_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        self.population_phase.SetValue('fbg', fbg_0, self.initial_time)

        return

    def run(self, *args):

        self.__zero_ode_parameters()

        time = self.initial_time

        while time <= self.end_time:

            # Interactions in the jail port
            #------------------------------
            # one way "to" jail

            message_time = self.recv('jail')
            outflow_rates = self.__compute_outflow_rates( message_time, 'jail' )
            self.send( (message_time, outflow_rates), 'jail' )

            # Interactions in the adjudication port
            #------------------------------------
            # one way "from" adjudication

            self.send( time, 'adjudication' )
            (check_time, inflow_rates) = self.recv('adjudication')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['adjudication-inflow-rates'] = inflow_rates

            # Interactions in the arrested port
            #----------------------------------
            # one way "from" arrested

            self.send( time, 'arrested' )
            (check_time, inflow_rates) = self.recv('arrested')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['arrested-inflow-rates'] = inflow_rates

            # Interactions in the community port
            #------------------------------
            # one way "to" community

            message_time = self.recv('community')
            outflow_rates = self.__compute_outflow_rates( message_time, 'community' )
            self.send( (message_time, outflow_rates), 'community' )

            # Evolve probation group population to the next time stamp
            #---------------------------------------------------------

            time = self.__step( time )

    def __rhs_fn(self, u_vec, t, params):

        fbg = u_vec  # probation population groups

        arrested_inflow_rates     = params['arrested-inflow-rates']
        adjudication_inflow_rates = params['adjudication-inflow-rates']

        inflow_rates  = arrested_inflow_rates + adjudication_inflow_rates

        cb0g = self.ode_params['commit-to-community-coeff-grps']

        cbjg = self.ode_params['commit-to-jail-coeff-grps']

        outflow_rates = ( cb0g + cbjg ) * fbg

        death_rates_coeff = params['probation-death-rates-coeff']

        death_rates = death_rates_coeff * fbg

        dt_fbg = inflow_rates - outflow_rates - death_rates

        return dt_fbg

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
            Time in the droplet unit of time (seconds).

        Returns
        -------
        None

        '''

        u_vec_0 = self.population_phase.GetValue('fbg', time)
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
        self.population_phase.SetValue('fbg', u_vec, time)

        return time

    def __compute_outflow_rates(self, time, name):

        fbg = self.population_phase.GetValue('fbg',time)

        assert np.all(fbg>=0.0), 'values: %r'%fbg

        if name == 'jail':

            cbjg = self.ode_params['commit-to-jail-coeff-grps']

            outflow_rates = cbjg * fbg

        if name == 'community':

            cb0g = self.ode_params['commit-to-community-coeff-grps']

            outflow_rates = cb0g * fbg

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

        return
