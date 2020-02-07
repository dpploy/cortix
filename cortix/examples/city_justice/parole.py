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

        self.initial_time = 0.0 * unit.day
        self.end_time     = 100 * unit.day
        self.time_step    = 0.5 * unit.day

        unit.percent = 1/100

        # Population groups
        self.n_groups = n_groups

        # Parole population groups
        feg_0 = np.random.random(self.n_groups) * pool_size
        feg = Quantity(name='feg', formal_name='parole-pop-grps',
                latex_name = '$n_e^{(g)}$',
                unit='# offenders', value=feg_0, info='Parole Population Groups')
        quantities.append(feg)

        # Model parameters: commitment coefficients

        # Parole to community
        a =  50*unit.percent/unit.year * np.ones(self.n_groups)
        b =  70*unit.percent/unit.year * np.ones(self.n_groups)
        ce0g_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        ce0g = Quantity(name='ce0g', formal_name='commit-community-coeff-grps',
               unit='1/s', value=ce0g_0)
        self.ode_params['commit-to-community-coeff-grps'] = ce0g_0
        quantities.append(ce0g)

        # Parole to prison  
        a = 30*unit.percent/unit.year * np.ones(self.n_groups)
        b = 40*unit.percent/unit.year * np.ones(self.n_groups)
        cepg_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        cepg = Quantity(name='cepg', formal_name='commit-prison-coeff-grps',
               unit='1/s', value=cepg_0)
        self.ode_params['commit-to-prison-coeff-grps'] = cepg_0
        quantities.append(cepg)

        # Death term
        a = 0.5*unit.percent/unit.year * np.ones(self.n_groups)
        b = 0.8*unit.percent/unit.year * np.ones(self.n_groups)
        deg_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        self.ode_params['parole-death-rates-coeff'] = deg_0

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

        while time <= self.end_time:

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

        cepg = self.ode_params['commit-to-prison-coeff-grps']

        outflow_rates = ( ce0g + cepg ) * feg

        death_rates_coeff = params['parole-death-rates-coeff']

        death_rates = death_rates_coeff * feg

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

          outflow_rates = cepg * feg

      if name == 'community':

          ce0g = self.ode_params['commit-to-community-coeff-grps']

          outflow_rates = ce0g * feg

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
