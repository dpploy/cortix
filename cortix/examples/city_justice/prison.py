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

class Prison(Module):
    '''
    Prison Cortix module used to model criminal group population in a prison.

    Notes
    -----
    These are the `port` names available in this module to connect to respective
    modules: `parole`, `adjudication`, `jail`, and `community`.
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

        self.port_names_expected = ['parole','adjudication','jail','community']

        quantities      = list()
        self.ode_params = dict()

        self.initial_time = 0.0 * unit.day
        self.end_time     = 100 * unit.day
        self.time_step    = 0.5 * unit.day

        unit.percent = 1/100

        # Population groups
        self.n_groups = n_groups

        # Prison population groups
        fpg_0 = np.random.random(self.n_groups) * pool_size
        fpg = Quantity(name='npg', formal_name='prison-pop-grps',
                latex_name = '$n_p^{(g)}$',
                unit='# offenders', value=fpg_0, info='Prison Population Groups')
        quantities.append(fpg)

        # Model parameters: commitment coefficients 

        # Prison to community
        a = 10*unit.percent/unit.year * np.ones(self.n_groups)
        b = 15*unit.percent/unit.year * np.ones(self.n_groups)
        cp0g_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        cp0g = Quantity(name='cp0g', formal_name='commit-community-coeff-grps',
               unit='1/s', value=cp0g_0)
        self.ode_params['commit-to-community-coeff-grps'] = cp0g_0
        quantities.append(cp0g)

        # Prison to parole  
        a = 20*unit.percent/unit.year * np.ones(self.n_groups)
        b = 25*unit.percent/unit.year * np.ones(self.n_groups)
        cpeg_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        cpeg = Quantity(name='cpeg', formal_name='commit-parole-coeff-grps',
               unit='1/s', value=cpeg_0)
        self.ode_params['commit-to-parole-coeff-grps'] = cpeg_0
        quantities.append(cpeg)

        # Death term
        a = 0.8*unit.percent/unit.year * np.ones(self.n_groups)
        b = 0.9*unit.percent/unit.year * np.ones(self.n_groups)
        dpg_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        self.ode_params['death-rates-coeff'] = dpg_0

        # Phase state
        self.population_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        self.population_phase.SetValue('npg', fpg_0, self.initial_time)

        # Initialize inflows to zero
        self.ode_params['parole-inflow-rates']       = np.zeros(self.n_groups)
        self.ode_params['adjudication-inflow-rates'] = np.zeros(self.n_groups)
        self.ode_params['jail-inflow-rates']         = np.zeros(self.n_groups)

        return

    def run(self, *args):

        self.__zero_ode_parameters()

        time = self.initial_time

        while time <= self.end_time:

            # Interactions in the parole port
            #--------------------------------
            # two way "from" and "to" parole

            # from
            self.send( time, 'parole' )
            (check_time, inflow_rates) = self.recv('parole')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['parole-inflow-rates'] = inflow_rates

            # to
            message_time = self.recv('parole')
            outflow_rates = self.__compute_outflow_rates( message_time, 'parole' )
            self.send( (message_time, outflow_rates), 'parole' )

            # Interactions in the adjudication port
            #------------------------------------
            # one way "from" adjudication

            self.send( time, 'adjudication' )
            (check_time, inflow_rates) = self.recv('adjudication')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['adjudication-inflow-rates'] = inflow_rates

            # Interactions in the jail port
            #------------------------------
            # one way "from" jail

            self.send( time, 'jail' )
            (check_time, inflow_rates) = self.recv('jail')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['jail-inflow-rates'] = inflow_rates

            # Interactions in the community port
            #------------------------------
            # one way "to" community

            message_time = self.recv('community')
            outflow_rates = self.__compute_outflow_rates( message_time, 'community' )
            self.send( (message_time, outflow_rates), 'community' )

            # Evolve prison group population to the next time stamp
            #------------------------------------------------------

            time = self.__step( time )

    def __rhs_fn(self, u_vec, t, params):

        fpg = u_vec  # prison population groups

        parole_inflow_rates       = params['parole-inflow-rates']
        adjudication_inflow_rates = params['adjudication-inflow-rates']
        jail_inflow_rates         = params['jail-inflow-rates']

        inflow_rates = parole_inflow_rates + adjudication_inflow_rates + jail_inflow_rates

        cp0g = self.ode_params['commit-to-community-coeff-grps']

        cpeg = self.ode_params['commit-to-parole-coeff-grps']

        outflow_rates = ( cp0g + cpeg ) * fpg

        death_rates_coeff = params['death-rates-coeff']

        death_rates = death_rates_coeff * fpg

        dt_fpg = inflow_rates - outflow_rates - death_rates

        return dt_fpg

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
            Time in SI unit.

        Returns
        -------
        None

        '''

        u_vec_0 = self.population_phase.GetValue('npg', time)
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
        self.population_phase.SetValue('npg', u_vec, time)

        return time

    def __compute_outflow_rates(self, time, name):

      fpg = self.population_phase.GetValue('npg',time)

      assert np.all(fpg>=0.0), 'values: %r'%fpg

      if name == 'parole':

          cpeg = self.ode_params['commit-to-parole-coeff-grps']

          outflow_rates = cpeg * fpg

      if name == 'community':

          cp0g = self.ode_params['commit-to-community-coeff-grps']

          outflow_rates = cp0g * fpg

      return outflow_rates

    def __zero_ode_parameters(self):
        '''
        If ports are not connected the corresponding outflows must be zero.

        '''

        zeros = np.zeros(self.n_groups)

        p_names = [p.name for p in self.ports]

        if 'community' not in p_names:
            self.ode_params['commit-to-community-coeff-grps']     = zeros

        if 'parole' not in p_names:
            self.ode_params['commit-to-parole-coeff-grps'] = zeros

        return
