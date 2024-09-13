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

class Jail(Module):
    '''
    Jail Cortix module used to model criminal group population in a jail.

    Notes
    -----
    These are the `port` names available in this module to connect to respective
    modules: `probation`, `adjudication`, `arrested`, `prison`, and `community`.
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

        self.port_names_expected = ['probation','adjudication','arrested','prison',
                                    'community']
        quantities      = list()
        self.ode_params = dict()

        self.initial_time = 0.0 * unit.day
        self.end_time     = 100 * unit.day
        self.time_step    = 0.5 * unit.day

        unit.month = 30*unit.day
        unit.percent = 1/100

        # Population groups
        self.n_groups = n_groups

        # Jail population groups
        fjg_0 = np.random.random(self.n_groups) * pool_size
        fjg = Quantity(name='fjg', formal_name='jail-pop-grps',
                latex_name = '$n_j^{(g)}$',
                unit='# offenders', value=fjg_0, info='Jail Population Groups')
        quantities.append(fjg)

        # Model parameters: commitment coefficients

        # Jail to community
        a =  35*unit.percent/unit.year * np.ones(self.n_groups)
        b =  40*unit.percent/unit.year * np.ones(self.n_groups)
        cj0g_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        cj0g = Quantity(name='cj0g', formal_name='commit-community-coeff-grps',
               unit='1/s', value=cj0g_0)
        self.ode_params['commit-to-community-coeff-grps'] = cj0g_0
        quantities.append(cj0g)

        # Jail to prison    
        a =  60*unit.percent/unit.year * np.ones(self.n_groups)
        b =  65*unit.percent/unit.year * np.ones(self.n_groups)
        cjpg_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        cjpg = Quantity(name='cjpg', formal_name='commit-prison-coeff-grps',
               unit='1/s', value=cjpg_0)
        self.ode_params['commit-to-prison-coeff-grps'] = cjpg_0
        quantities.append(cjpg)

        # Death term
        a = 0.5*unit.percent/unit.year * np.ones(self.n_groups)
        b = 0.6*unit.percent/unit.year * np.ones(self.n_groups)
        djg_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        self.ode_params['jail-death-rates-coeff'] = djg_0

        # Phase state
        self.population_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        self.population_phase.SetValue('fjg', fjg_0, self.initial_time)

        # Initialize inflows to zero
        self.ode_params['arrested-inflow-rates']     = np.zeros(self.n_groups)
        self.ode_params['probation-inflow-rates']    = np.zeros(self.n_groups)
        self.ode_params['adjudication-inflow-rates'] = np.zeros(self.n_groups)

        return

    def run(self, *args):

        self.__zero_ode_parameters()

        time = self.initial_time

        while time <= self.end_time:

            # Interactions in the prison port
            #--------------------------------
            # one way "to" prison

            message_time = self.recv('prison')
            outflow_rates = self.__compute_outflow_rates( message_time, 'prison' )
            self.send( (message_time, outflow_rates), 'prison' )

            # Interactions in the adjudication port
            #------------------------------------
            # one way "from" adjudication

            self.send( time, 'adjudication' )
            (check_time, adjudication_inflow_rates) = self.recv('adjudication')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['adjudication-inflow-rates'] = adjudication_inflow_rates

            # Interactions in the arrested port
            #----------------------------------
            # one way "from" arrested

            self.send( time, 'arrested' )
            (check_time, arrested_inflow_rates) = self.recv('arrested')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['arrested-inflow-rates'] = arrested_inflow_rates

            # Interactions in the probation port
            #-----------------------------------
            # one way "from" probation

            self.send( time, 'probation' )
            (check_time, probation_inflow_rates) = self.recv('probation')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['probation-inflow-rates'] = probation_inflow_rates

            # Interactions in the community port
            #------------------------------
            # one way "to" community

            message_time = self.recv('community')
            outflow_rates = self.__compute_outflow_rates( message_time, 'community' )
            self.send( (message_time, outflow_rates), 'community' )

            # Evolve jail group population to the next time stamp
            #----------------------------------------------------

            time = self.__step( time )

    def __rhs_fn(self, u_vec, t, params):

        fjg = u_vec  # jail population groups

        arrested_inflow_rates    = params['arrested-inflow-rates']
        probation_inflow_rates   = params['probation-inflow-rates']
        adjudication_inflow_rates = params['adjudication-inflow-rates']

        inflow_rates  = arrested_inflow_rates + probation_inflow_rates + \
                        adjudication_inflow_rates

        cj0g = self.ode_params['commit-to-community-coeff-grps']

        cjpg = self.ode_params['commit-to-prison-coeff-grps']

        outflow_rates = ( cj0g + cjpg ) * fjg

        death_rates_coeff = params['jail-death-rates-coeff']

        death_rates = death_rates_coeff * fjg

        dt_fjg = inflow_rates - outflow_rates - death_rates

        return dt_fjg

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

        u_vec_0 = self.population_phase.GetValue('fjg', time)
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
        self.population_phase.SetValue('fjg', u_vec, time)

        return time

    def __compute_outflow_rates(self, time, name):

      fjg = self.population_phase.GetValue('fjg',time)

      assert np.all(fjg>=0.0), 'values: %r'%fjg

      if name == 'prison':

          cjpg = self.ode_params['commit-to-prison-coeff-grps']

          outflow_rates = cjpg * fjg

      if name == 'community':

          cj0g = self.ode_params['commit-to-community-coeff-grps']

          outflow_rates = cj0g * fjg

      return outflow_rates

    def __zero_ode_parameters(self):
        '''
        If ports are not connected the corresponding outflows must be zero.

        '''

        zeros = np.zeros(self.n_groups)

        p_names = [p.name for p in self.ports]

        if 'community' not in p_names:
            self.ode_params['commit-to-community-coeff-grps']     = zeros

        if 'prison' not in p_names:
            self.ode_params['commit-to-prison-coeff-grps'] = zeros

        return
