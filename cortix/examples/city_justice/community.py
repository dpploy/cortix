#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
import logging

import numpy as np
import scipy.constants as unit
from scipy.integrate import odeint

from cortix import Module
from cortix import Phase
from cortix import Quantity

class Community(Module):
    """Community model with criminal group population.

    Community here is the system at large with all possible
    adult individuals included in any given society.

    Notes
    -----
    These are the `port` names available in this module to connect to respective
    modules:

     + `probation`,
     + `adjudication`,
     + `jail`, `prison`,
     + `arrested`, and
     + `parole`.

    See instance attribute `port_names_expected`.

    """

    def __init__(self, n_groups=1, non_offender_adult_population=100,
                 offender_pool_size=0.0, free_offender_pool_size=0.0):
        """Constructor.

        Parameters
        ----------
        n_groups: int
            Number of groups in the population.
        non_offender_adult_population: float
            Pool of individuals reaching the adult age (SI) unit. Default: 100.
        offender_pool_size: float
            Upperbound on the range of the existing population groups. A random value
            from 0 to the upperbound value will be assigned to each group. This is
            typically a small number, say a fraction of a percent.

        """

        super().__init__()

        self.port_names_expected = ['probation', 'adjudication', 'jail', 'prison',
                                    'arrested', 'parole']

        quantities = list()
        self.ode_params = dict()

        self.initial_time = 0.0 * unit.day
        self.end_time = 100 * unit.day
        self.time_step = 0.5 * unit.day
        self.show_time = (False, 10*unit.day)
        self.log = logging.getLogger('cortix')

        unit.percent = 1/100

        # Population groups
        self.n_groups = n_groups

        # Community non-offender population
        n0_0 = np.array([float(non_offender_adult_population)])
        n0 = Quantity(name='n0', formal_name='non-offender-adult-pop',
                      latex_name='$n_0$',
                      unit='# adults', value=n0_0,
                      info='Non-Offender Adult Population')
        quantities.append(n0)

        # Community free-offender population groups
        f0g_0 = np.random.random(self.n_groups) * offender_pool_size
        f0g = Quantity(name='f0g', formal_name='free-offender-pop-grps',
                       latex_name='$n_0^{(g)}$',
                       unit='# offenders', value=f0g_0,
                       info='Free-Offender Population Groups')
        quantities.append(f0g)

        # Model parameters: commitment coefficients

        # Community non-offenders to offenders (arrested)
        a = 0.6*unit.percent/unit.year * np.ones(self.n_groups)
        b = 0.8*unit.percent/unit.year * np.ones(self.n_groups)
        c00g_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        c00g = Quantity(name='c00g',
                        formal_name='non-offenders-commit-arrested-coeff-grps',
                        unit='1/s', value=c00g_0)
        self.ode_params['non-offenders-commit-to-arrested-coeff-grps'] = c00g_0
        quantities.append(c00g)

        # Community free-offenders to arrested (recidivism)
        a = 0.8*unit.percent/unit.year * np.ones(self.n_groups)
        b = 0.9*unit.percent/unit.year * np.ones(self.n_groups)
        c0rg_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        c0rg = Quantity(name='c0rg',
                        formal_name='free-offenders-commit-arrested-coeff-grps',
                        value=c0rg_0, unit='1/s')
        self.ode_params['free-offenders-commit-to-arrested-coeff-grps'] = c0rg_0
        quantities.append(c0rg)

        # Death term for community offenders
        a = 0.8*unit.percent/unit.year * np.ones(self.n_groups)
        b = 1.0*unit.percent/unit.year * np.ones(self.n_groups)
        d0g_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        self.ode_params['free-offenders-death-rates-coeff'] = d0g_0

        # Death term for community non-offenders
        a = 0.5*unit.percent/unit.year
        b = 1.0*unit.percent/unit.year
        d0_0 = a + (b-a)*np.random.random()
        self.ode_params['non-offenders-death-rate-coeff'] = d0_0

        # Maturity term for community non-offenders
        a = 1.5*unit.percent/unit.year
        b = 2.5*unit.percent/unit.year
        s0_0 = a + (b-a)*np.random.random()
        self.ode_params['non-offenders-maturity-rate-coeff'] = s0_0
        self.ode_params['non_offender_adult_population'] = non_offender_adult_population

        # Phase state
        self.population_phase = Phase(self.initial_time, time_unit='s',
                                      quantities=quantities)

        self.population_phase.SetValue('n0', n0_0, self.initial_time)
        self.population_phase.SetValue('f0g', f0g_0, self.initial_time)

        # Initialize inflows to zero
        self.ode_params['prison-inflow-rates'] = np.zeros(self.n_groups)
        self.ode_params['parole-inflow-rates'] = np.zeros(self.n_groups)
        self.ode_params['arrested-inflow-rates'] = np.zeros(self.n_groups)
        self.ode_params['jail-inflow-rates'] = np.zeros(self.n_groups)
        self.ode_params['adjudication-inflow-rates'] = np.zeros(self.n_groups)
        self.ode_params['probation-inflow-rates'] = np.zeros(self.n_groups)

    def run(self, *args):

        self.__zero_ode_parameters()

        time = self.initial_time

        while time <= self.end_time:

            if self.show_time[0] and abs(time%self.show_time[1]-0.0) <= 1.e-1:
                self.log.info('Community::time[d] = '+str(round(time/unit.day, 1)))

            self.__call_ports(time)

            # Evolve offenders group population to the next time stamp
            #---------------------------------------------------------

            time = self.__step(time)

    def __call_ports(self, time):

        # Interactions in the jail port
        #--------------------------------
        # one way "from" jail

        self.send(time, 'jail')
        (check_time, inflow_rates) = self.recv('jail')
        assert abs(check_time-time) <= 1e-6
        self.ode_params['jail-inflow-rates'] = inflow_rates

        # Interactions in the adjudication port
        #--------------------------------------
        # one way "from" adjudication

        self.send(time, 'adjudication')
        (check_time, inflow_rates) = self.recv('adjudication')
        assert abs(check_time-time) <= 1e-6
        self.ode_params['adjudication-inflow-rates'] = inflow_rates

        # Interactions in the probation port
        #--------------------------------
        # one way "from" probation

        self.send(time, 'probation')
        (check_time, inflow_rates) = self.recv('probation')
        assert abs(check_time-time) <= 1e-6
        self.ode_params['probation-inflow-rates'] = inflow_rates

        # Interactions in the prison port
        #--------------------------------
        # one way "from" prison

        self.send(time, 'prison')
        (check_time, inflow_rates) = self.recv('prison')
        assert abs(check_time-time) <= 1e-6
        self.ode_params['prison-inflow-rates'] = inflow_rates

        # Interactions in the parole port
        #--------------------------------
        # one way "from" parole

        self.send(time, 'parole')
        (check_time, inflow_rates) = self.recv('parole')
        assert abs(check_time-time) <= 1e-6
        self.ode_params['parole-inflow-rates'] = inflow_rates

        # Interactions in the arrested port
        #--------------------------------
        # two way "to" and "from" arrested

        # to
        message_time = self.recv('arrested')
        outflow_rates = self.__compute_outflow_rates(message_time, 'arrested')
        self.send((message_time, outflow_rates), 'arrested')

        # from
        self.send(time, 'arrested')
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
        a_vec = self.population_phase.GetValue('n0', time)
        b_vec = self.population_phase.GetValue('f0g', time)

        u_0 = np.concatenate((a_vec, b_vec))

        t_interval_sec = np.linspace(0.0, self.time_step, num=2)

        (u_vec_hist, info_dict) = odeint(self.__rhs_fn,
                                         u_0, t_interval_sec,
                                         args=(self.ode_params, ),
                                         rtol=1e-4, atol=1e-8, mxstep=200,
                                         full_output=True)

        assert info_dict['message'] =='Integration successful.', info_dict['message']

        u_vec = u_vec_hist[1, :]  # solution vector at final time step


        time += self.time_step

        # Update state variables
        values = self.population_phase.GetRow() # values existing values
        self.population_phase.AddRow(time, values) # copy on new time for convenience

        self.population_phase.SetValue('n0', u_vec[:1], time) # insert new values
        self.population_phase.SetValue('f0g', u_vec[1:], time) # insert new values

        return time

    def __rhs_fn(self, u_vec, t, params):

        n0 = u_vec[:1]   # non-offender population

        # source of non-offenders
        s0_coeff = params['non-offenders-maturity-rate-coeff']
        n0_0 = params['non_offender_adult_population']
        s0 = s0_coeff * n0_0

        # outflow rate to Arrested
        c00g = params['non-offenders-commit-to-arrested-coeff-grps']
        outflow_rate = np.sum(c00g * n0)

        # death rate
        death_rate_coeff = params['non-offenders-death-rate-coeff']
        death_rate = death_rate_coeff * n0

        dt_n0 = s0 - outflow_rate - death_rate


        f0g = u_vec[1:]  # free-offender population groups

        prison_inflow_rates = params['prison-inflow-rates']
        parole_inflow_rates = params['parole-inflow-rates']
        arrested_inflow_rates = params['arrested-inflow-rates']
        jail_inflow_rates = params['jail-inflow-rates']
        adjudication_inflow_rates = params['adjudication-inflow-rates']
        probation_inflow_rates = params['probation-inflow-rates']

        # free-offenders inflows
        inflow_rates = prison_inflow_rates + parole_inflow_rates +\
                       arrested_inflow_rates + jail_inflow_rates +\
                       adjudication_inflow_rates + probation_inflow_rates

        assert np.all(inflow_rates >= 0.0), 'values: %r'%inflow_rates

        c0rg = params['free-offenders-commit-to-arrested-coeff-grps']


        # free-offenders outflow (recidivism)
        outflow_rates = c0rg * f0g

        assert np.all(outflow_rates >= 0.0), 'values: %r'%outflow_rates

        death_rates_coeff = params['free-offenders-death-rates-coeff']

        death_rates = death_rates_coeff * f0g

        assert np.all(death_rates >= 0.0), 'values: %r'%death_rates

        dt_f0g = inflow_rates - outflow_rates - death_rates


        dt_u = np.concatenate((dt_n0, dt_f0g))

        return dt_u

    def __compute_outflow_rates(self, time, name):

        n0 = self.population_phase.GetValue('n0', time)
        f0g = self.population_phase.GetValue('f0g', time)

        if name == 'arrested':

            c0rg = self.ode_params['free-offenders-commit-to-arrested-coeff-grps']

            c00g = self.ode_params['non-offenders-commit-to-arrested-coeff-grps']

            # Recidivism and new offenders
            outflow_rates = c0rg * f0g + c00g * n0

        return outflow_rates

    def __zero_ode_parameters(self):
        '''
        If ports are not connected the corresponding outflows must be zero.

        '''

        zeros = np.zeros(self.n_groups)

        p_names = [p.name for p in self.ports]

        if 'arrested' not in p_names:
            self.ode_params['commit-to-arrested-coeff-grps'] = zeros

            self.ode_params['general-commit-to-arrested-coeff-grps'] = zeros

        return
