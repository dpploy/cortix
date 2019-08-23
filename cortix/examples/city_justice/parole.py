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

class Parole(Module):
    '''
    Parole Cortix module used to model criminal group population in a parole system.

    Notes
    -----
    These are the `port` names available in this module to connect to respective
    modules: `prison` and `community`.
    See instance attribute `port_names_expected`.

    '''

    def __init__(self, n_groups=1, pool_size=0.0):

        super().__init__()

        self.port_names_expected = ['prison','community']

        quantities      = list()
        self.ode_params = dict()

        self.initial_time = 0.0 * const.day
        self.end_time     = 100 * const.day
        self.time_step    = 0.5 * const.day

        # Population groups
        self.n_groups = n_groups

        # Parole population groups
        feg_0 = np.random.random(self.n_groups) * pool_size
        feg = Quantity(name='feg', formalName='parole-pop-grps',
                unit='individual', value=feg_0)
        quantities.append(feg)

        # Model parameters: commitment coefficients and their modifiers

        # Parole to community
        ce0g_0 = np.random.random(self.n_groups) / const.day
        ce0g = Quantity(name='ce0g', formalName='commit-community-coeff-grps',
               unit='individual', value=ce0g_0)
        self.ode_params['commit-to-community-coeff-grps'] = ce0g_0
        quantities.append(ce0g)

        me0g_0 = np.random.random(self.n_groups)
        me0g = Quantity(name='me0g', formalName='commit-community-coeff-mod-grps',
               unit='individual', value=me0g_0)
        self.ode_params['commit-to-community-coeff-mod-grps'] = me0g_0
        quantities.append(me0g)

        # Parole to prison  
        cepg_0 = np.random.random(self.n_groups) / const.day
        cepg = Quantity(name='cepg', formalName='commit-prison-coeff-grps',
               unit='individual', value=cepg_0)
        self.ode_params['commit-to-prison-coeff-grps'] = cepg_0
        quantities.append(cepg)

        mepg_0 = np.random.random(self.n_groups)
        mepg = Quantity(name='mepg', formalName='commit-prison-coeff-mod-grps',
               unit='individual', value=mepg_0)
        self.ode_params['commit-to-prison-coeff-mod-grps'] = mepg_0
        quantities.append(mepg)

        # Death term
        self.ode_params['parole-death-rates'] = np.zeros(self.n_groups)

        # Phase state
        self.population_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        self.population_phase.SetValue('feg', feg_0, self.initial_time)

        # Initialize inflows to zero
        self.ode_params['prison-inflow-rates'] = np.zeros(self.n_groups)

        return

    def run(self, *args):

        self.__zero_ode_parameters()

        time = self.initial_time

        while time < self.end_time:

            # Interactions in the prison port
            #--------------------------------
            # two way "to" and "from" prison

            # to
            message_time = self.recv('prison')
            outflow_rates = self.__compute_outflow_rates( message_time, 'prison' )
            self.send( (message_time, outflow_rates), 'prison' )

            # from
            self.send( time, 'prison' )
            (check_time, prison_inflow_rates) = self.recv('prison')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['prison-inflow-rates'] = prison_inflow_rates

            # Interactions in the community port
            #-----------------------------------
            # one way "to" community

            message_time = self.recv('community')
            outflow_rates = self.__compute_outflow_rates( message_time, 'community' )
            self.send( (message_time, outflow_rates), 'community' )

            # Evolve parole group population to the next time stamp
            #------------------------------------------------------

            time = self.__step( time )

    def __rhs_fn(self, u_vec, t, params):

        feg = u_vec  # parole population groups

        prison_inflow_rates = params['prison-inflow-rates']

        inflow_rates  = prison_inflow_rates

        ce0g = self.ode_params['commit-to-community-coeff-grps']
        me0g = self.ode_params['commit-to-community-coeff-mod-grps']

        cepg = self.ode_params['commit-to-prison-coeff-grps']
        mepg = self.ode_params['commit-to-prison-coeff-mod-grps']

        outflow_rates = ( ce0g * me0g + cepg * mepg ) * feg

        death_rates = params['parole-death-rates']

        dt_feg = inflow_rates - outflow_rates - death_rates

        return dt_feg

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

        u_vec_0 = self.population_phase.GetValue('feg', time)
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
        self.population_phase.SetValue('feg', u_vec, time)

        return time

    def __compute_outflow_rates(self, time, name):

      feg = self.population_phase.GetValue('feg',time)

      assert np.all(feg>=0.0), 'values: %r'%feg

      if name == 'prison':

          cepg = self.ode_params['commit-to-prison-coeff-grps']
          mepg = self.ode_params['commit-to-prison-coeff-mod-grps']

          outflow_rates = cepg * mepg * feg

      if name == 'community':

          ce0g = self.ode_params['commit-to-community-coeff-grps']
          me0g = self.ode_params['commit-to-community-coeff-mod-grps']

          outflow_rates = ce0g * me0g * feg

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
