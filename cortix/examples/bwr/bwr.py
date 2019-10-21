#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org

import logging

import numpy as np
import scipy.constants as const
from scipy.integrate import odeint

from cortix import Module
from cortix import Phase
from cortix import Quantity

class BWR(Module):
    '''
    Boiling water reactor single-point reactor.

    Notes
    -----
    These are the `port` names available in this module to connect to respective
    modules: `probation`, `adjudication`, `jail`, `prison`, `arrested`, and `parole`.
    See instance attribute `port_names_expected`.

    '''

    def __init__(self, params):
        '''
        Parameters
        ----------
        params: dict
            All parameters for the module in the form of a dictionary or string-value.

        '''

        super().__init__()

        self.port_names_expected = ['coolant-inflow','coolant-outflow']

        quantities      = list()
        self.ode_params = dict()

        self.initial_time = 0.0 * const.day
        self.end_time     = 100 * const.day
        self.time_step    = 0.5 * const.day
        self.show_time = (False,10*const.day)

        self.log = logging.getLogger('cortix')

        # Community offender population groups removed from circulation
        f0g_0 = np.random.random(self.n_groups) * offender_pool_size
        f0g = Quantity(name='f0g', formalName='offender-pop-grps',
                unit='individual', value=f0g_0)
        quantities.append(f0g)

        # Model parameters: commitment coefficients and their modifiers

        # Phase state
        self.population_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        self.population_phase.SetValue('f0g', f0g_0, self.initial_time)

        # Initialize inflows to zero
        self.ode_params['prison-inflow-rates']       = np.zeros(self.n_groups)
        self.ode_params['parole-inflow-rates']       = np.zeros(self.n_groups)
        self.ode_params['arrested-inflow-rates']     = np.zeros(self.n_groups)
        self.ode_params['jail-inflow-rates']         = np.zeros(self.n_groups)
        self.ode_params['adjudication-inflow-rates'] = np.zeros(self.n_groups)
        self.ode_params['probation-inflow-rates']    = np.zeros(self.n_groups)

        return

    def run(self, *args):

        self.__zero_ode_parameters()

        time = self.initial_time

        while time < self.end_time:

            if self.show_time[0] and abs(time%self.show_time[1]-0.0)<=1.e-1:
                self.log.info('Community::time[d] = '+str(round(time/const.day,1)))

            self.__call_ports(time)

            # Evolve offenders group population to the next time stamp
            #---------------------------------------------------------

            time = self.__step( time )

    def __call_ports(self, time):

            # Interactions in the jail port
            #--------------------------------
            # one way "from" jail

            self.send( time, 'jail' )
            (check_time, inflow_rates) = self.recv('jail')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['jail-inflow-rates'] = inflow_rates

            # Interactions in the adjudication port
            #--------------------------------------
            # one way "from" adjudication

            self.send( time, 'adjudication' )
            (check_time, inflow_rates) = self.recv('adjudication')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['adjudication-inflow-rates'] = inflow_rates

            # Interactions in the probation port
            #--------------------------------
            # one way "from" probation

            self.send( time, 'probation' )
            (check_time, inflow_rates) = self.recv('probation')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['probation-inflow-rates'] = inflow_rates

            # Interactions in the prison port
            #--------------------------------
            # one way "from" prison

            self.send( time, 'prison' )
            (check_time, inflow_rates) = self.recv('prison')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['prison-inflow-rates'] = inflow_rates

            # Interactions in the parole port
            #--------------------------------
            # one way "from" parole

            self.send( time, 'parole' )
            (check_time, inflow_rates) = self.recv('parole')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['parole-inflow-rates'] = inflow_rates

            # Interactions in the arrested port
            #--------------------------------
            # two way "to" and "from" arrested

            # to
            message_time = self.recv('arrested')
            outflow_rates = self.__compute_outflow_rates( message_time, 'arrested' )
            self.send( (message_time, outflow_rates), 'arrested' )

            # from
            self.send( time, 'arrested' )
            (check_time, inflow_rates) = self.recv('arrested')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['arrested-inflow-rates'] = inflow_rates

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

        # Get state values
        u_0 = self.population_phase.GetValue('f0g', time)

        t_interval_sec = np.linspace(0.0, self.time_step, num=2)

        (u_vec_hist, info_dict) = odeint( self.__rhs_fn,
                                          u_0, t_interval_sec,
                                          args=( self.ode_params, ),
                                          rtol=1e-4, atol=1e-8, mxstep=200,
                                          full_output=True )

        assert info_dict['message'] =='Integration successful.', info_dict['message']

        u_vec = u_vec_hist[1,:]  # solution vector at final time step


        time += self.time_step

        # Update state variables
        values = self.population_phase.GetRow() # values existing values
        self.population_phase.AddRow(time, values) # copy on new time for convenience

        self.population_phase.SetValue('f0g', u_vec, time) # insert new values

        # Update the population of free offenders returning to community
        inflow_rates = self.ode_params['total-inflow-rates']
        f0g_free = inflow_rates * self.time_step

        self.population_phase.SetValue('f0g_free',f0g_free,time)

        return time

    def __rhs_fn(self, u_vec, t, params):

        f0g = u_vec  # offender population groups (removed from community)

        prison_inflow_rates       = params['prison-inflow-rates']
        parole_inflow_rates       = params['parole-inflow-rates']
        arrested_inflow_rates     = params['arrested-inflow-rates']
        jail_inflow_rates         = params['jail-inflow-rates']
        adjudication_inflow_rates = params['adjudication-inflow-rates']
        probation_inflow_rates    = params['probation-inflow-rates']

        inflow_rates = prison_inflow_rates + parole_inflow_rates +\
                       arrested_inflow_rates + jail_inflow_rates +\
                       adjudication_inflow_rates + probation_inflow_rates

        params['total-inflow-rates'] = inflow_rates

        assert np.all(inflow_rates>=0.0), 'values: %r'%inflow_rates

        c0rg = params['commit-to-arrested-coeff-grps']
        m0rg = params['commit-to-arrested-coeff-mod-grps']

        c00g = params['general-commit-to-arrested-coeff-grps']
        m00g = params['general-commit-to-arrested-coeff-mod-grps']

        non_offender_adult_population = params['non-offender-adult-population']

        # Recidivism + new offenders
        outflow_rates = c0rg * m0rg * np.abs(f0g) + \
                c00g * m00g * non_offender_adult_population

        assert np.all(outflow_rates>=0.0), 'values: %r'%outflow_rates

        death_rates = params['death-rates-coeff'] * np.abs(f0g)

        assert np.all(death_rates>=0.0), 'values: %r'%death_rates

        dt_f0g = inflow_rates - outflow_rates  - death_rates

        return dt_f0g


    def __compute_outflow_rates(self, time, name):

        f0g = self.population_phase.GetValue('f0g',time)

        if name == 'arrested':

            c0rg = self.ode_params['commit-to-arrested-coeff-grps']
            m0rg = self.ode_params['commit-to-arrested-coeff-mod-grps']

            c00g = self.ode_params['general-commit-to-arrested-coeff-grps']
            m00g = self.ode_params['general-commit-to-arrested-coeff-mod-grps']

            f0 = self.ode_params['non-offender-adult-population']

            # Recidivism
            outflow_rates = c0rg * m0rg * np.abs(f0g) + c00g * m00g * f0

        return outflow_rates

    def __zero_ode_parameters(self):
        '''
        If ports are not connected the corresponding outflows must be zero.

        '''

        zeros = np.zeros(self.n_groups)

        p_names = [p.name for p in self.ports]

        if 'arrested' not in p_names:
            self.ode_params['commit-to-arrested-coeff-grps']     = zeros
            self.ode_params['commit-to-arrested-coeff-mod-grps'] = zeros

            self.ode_params['general-commit-to-arrested-coeff-grps']     = zeros
            self.ode_params['general-commit-to-arrested-coeff-mod-grps'] = zeros

        return
