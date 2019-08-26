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

        self.initial_time = 0.0 * const.day
        self.end_time     = 100 * const.day
        self.time_step    = 0.5 * const.day

        # Population groups
        self.n_groups = n_groups

        # Jail population groups
        fjg_0 = np.random.random(self.n_groups) * pool_size
        fjg = Quantity(name='fjg', formalName='jail-pop-grps',
                unit='individual', value=fjg_0)
        quantities.append(fjg)

        # Model parameters: commitment coefficients and their modifiers

        # Jail to community
        cj0g_0 = np.random.random(self.n_groups) / const.day
        cj0g = Quantity(name='cj0g', formalName='commit-community-coeff-grps',
               unit='individual', value=cj0g_0)
        self.ode_params['commit-to-community-coeff-grps'] = cj0g_0
        quantities.append(cj0g)

        mj0g_0 = np.random.random(self.n_groups)
        mj0g = Quantity(name='mj0g', formalName='commit-community-coeff-mod-grps',
               unit='individual', value=mj0g_0)
        self.ode_params['commit-to-community-coeff-mod-grps'] = mj0g_0
        quantities.append(mj0g)

        # Jail to prison    
        cjpg_0 = np.random.random(self.n_groups) / const.day
        cjpg = Quantity(name='cjpg', formalName='commit-prison-coeff-grps',
               unit='individual', value=cjpg_0)
        self.ode_params['commit-to-prison-coeff-grps'] = cjpg_0
        quantities.append(cjpg)

        mjpg_0 = np.random.random(self.n_groups)
        mjpg = Quantity(name='mjpg', formalName='commit-prison-coeff-mod-grps',
               unit='individual', value=mjpg_0)
        self.ode_params['commit-to-prison-coeff-mod-grps'] = mjpg_0
        quantities.append(mjpg)

        # Death term
        self.ode_params['jail-death-rates'] = np.zeros(self.n_groups)

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

        while time < self.end_time:

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
        mj0g = self.ode_params['commit-to-community-coeff-mod-grps']

        cjpg = self.ode_params['commit-to-prison-coeff-grps']
        mjpg = self.ode_params['commit-to-prison-coeff-mod-grps']

        outflow_rates = ( cj0g * mj0g + cjpg * mjpg ) * fjg

        death_rates = params['jail-death-rates']

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
          mjpg = self.ode_params['commit-to-prison-coeff-mod-grps']

          outflow_rates = cjpg * mjpg * fjg

      if name == 'community':

          cj0g = self.ode_params['commit-to-community-coeff-grps']
          mj0g = self.ode_params['commit-to-community-coeff-mod-grps']

          outflow_rates = cj0g * mj0g * fjg

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

        if 'prison' not in p_names:
            self.ode_params['commit-to-prison-coeff-grps'] = zeros
            self.ode_params['commit-to-prison-coeff-mod-grps'] = zeros

        return
