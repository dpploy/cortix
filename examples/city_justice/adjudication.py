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

class Adjudication(Module):
    '''
    Adjudication Cortix module used to model criminal group population in an
    adjudication system.

    Notes
    -----
    These are the `port` names available in this module to connect to respective
    modules: `probation`, `jail`, `arrested`, `prison`, and `community`.
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

        self.port_names_expected = ['probation','jail','arrested','prison','community']

        quantities      = list()
        self.ode_params = dict()

        self.initial_time = 0.0 * unit.day
        self.end_time     = 100 * unit.day
        self.time_step    = 0.5 * unit.day

        unit.percent = 1/100
        unit.month = 30*unit.day

        # Population groups
        self.n_groups = n_groups

        # Adjudication population groups
        fag_0 = np.random.random(self.n_groups) * pool_size
        fag = Quantity(name='fag', formal_name='adjudication-pop-grps',
                latex_name = '$n_a^{(g)}$',
                unit='# offenders', value=fag_0, info='Adjudication Population Groups')
        quantities.append(fag)

        # Model parameters: commitment coefficients

        # Adjudication to community
        a = 10*unit.percent/unit.year * np.ones(self.n_groups)
        b = 15*unit.percent/unit.year * np.ones(self.n_groups)
        ca0g_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        ca0g = Quantity(name='ca0g', formal_name='commit-community-coeff-grps',
               unit='1/s', value=ca0g_0)
        self.ode_params['commit-to-community-coeff-grps'] = ca0g_0
        quantities.append(ca0g)

        # Adjudication to probation
        a = 20*unit.percent/unit.year * np.ones(self.n_groups)
        b = 30*unit.percent/unit.year * np.ones(self.n_groups)
        cabg_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        cabg = Quantity(name='cabg', formal_name='commit-probation-coeff-grps',
               unit='1/s', value=cabg_0)
        self.ode_params['commit-to-probation-coeff-grps'] = cabg_0
        quantities.append(cabg)

        # Adjudication to jail    
        a = 15*unit.percent/unit.year * np.ones(self.n_groups)
        b = 25*unit.percent/unit.year * np.ones(self.n_groups)
        cajg_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        cajg = Quantity(name='cajg', formal_name='commit-parole-coeff-grps',
               unit='1/s', value=cajg_0)
        self.ode_params['commit-to-jail-coeff-grps'] = cajg_0
        quantities.append(cajg)

        # Adjudication to prison    
        a = 40*unit.percent/unit.year * np.ones(self.n_groups)
        b = 50*unit.percent/unit.year * np.ones(self.n_groups)
        capg_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        capg = Quantity(name='capg', formal_name='commit-prison-coeff-grps',
               unit='1/s', value=capg_0)
        self.ode_params['commit-to-prison-coeff-grps'] = capg_0
        quantities.append(capg)

        # Death term
        a = 0.2*unit.percent/unit.year * np.ones(self.n_groups)
        b = 0.3*unit.percent/unit.year * np.ones(self.n_groups)
        dag_0 = (a + (b-a)*np.random.random(self.n_groups)) / self.n_groups
        self.ode_params['death-rates-coeff'] = dag_0

        # Phase state
        self.population_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        self.population_phase.SetValue('fag', fag_0, self.initial_time)

        # Initialize inflows to zero
        self.ode_params['arrested-inflow-rates'] = np.zeros(self.n_groups)

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

            # Interactions in the jail port
            #------------------------------
            # one way "to" jail

            message_time = self.recv('jail')
            outflow_rates = self.__compute_outflow_rates( message_time, 'jail' )
            self.send( (message_time, outflow_rates), 'jail' )

            # Interactions in the arrested port
            #----------------------------------
            # one way "from" arrested

            self.send( time, 'arrested' )
            (check_time, inflow_rates) = self.recv('arrested')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['arrested-inflow-rates'] = inflow_rates

            # Interactions in the probation port
            #-----------------------------------
            # one way "to" probation

            message_time = self.recv('probation')
            outflow_rates = self.__compute_outflow_rates( message_time, 'probation' )
            self.send( (message_time, outflow_rates), 'probation' )

            # Interactions in the community port
            #-----------------------------------
            # one way "to" community

            message_time = self.recv('community')
            outflow_rates = self.__compute_outflow_rates( message_time, 'community' )
            self.send( (message_time, outflow_rates), 'community' )

            # Evolve prison group population to the next time stamp
            #------------------------------------------------------

            time = self.__step( time )

        return

    def __rhs_fn(self, u_vec, t, params):
        '''
        Right side function of the ODE system.
        '''

        fag = u_vec  # adjudication population groups

        assert np.all(fag>=0.0), 'values: %r'%fag

        arrested_inflow_rates = params['arrested-inflow-rates']

        inflow_rates = arrested_inflow_rates

        assert np.all(inflow_rates>=0.0), 'values: %r'%inflow_rates

        ca0g = self.ode_params['commit-to-community-coeff-grps']

        cajg = self.ode_params['commit-to-jail-coeff-grps']

        cabg = self.ode_params['commit-to-probation-coeff-grps']

        capg = self.ode_params['commit-to-prison-coeff-grps']

        outflow_rates = ( ca0g + cajg + cabg + capg ) * fag

        assert np.all(outflow_rates>=0.0), 'values: %r'%outflow_rates

        death_rates_coeff = params['death-rates-coeff']

        death_rates = death_rates_coeff * fag

        assert np.all(death_rates>=0.0), 'values: %r'%death_rates

        dt_fag = inflow_rates - outflow_rates - death_rates

        return dt_fag

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
        time: float

        '''

        u_vec_0 = self.population_phase.GetValue('fag', time)
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
        self.population_phase.SetValue('fag', u_vec, time)

        return time

    def __compute_outflow_rates(self, time, name):

        fag = self.population_phase.GetValue('fag',time)

        assert np.all(fag>=0.0), 'values: %r'%fag

        if name == 'prison':

            capg = self.ode_params['commit-to-prison-coeff-grps']

            outflow_rates = capg * fag

        if name == 'probation':

            cabg = self.ode_params['commit-to-probation-coeff-grps']

            outflow_rates = cabg * fag

        if name == 'jail':

            cajg = self.ode_params['commit-to-jail-coeff-grps']

            outflow_rates = cajg * fag

        if name == 'community':

            ca0g = self.ode_params['commit-to-community-coeff-grps']

            outflow_rates = ca0g * fag

        return outflow_rates

    def __zero_ode_parameters(self):
        '''
        Zero the outflows of unconnected ports.

        '''

        zeros = np.zeros(self.n_groups)

        p_names = [p.name for p in self.ports]

        if 'community' not in p_names:
            self.ode_params['commit-to-community-coeff-grps']     = zeros

        if 'jail' not in p_names:
            self.ode_params['commit-to-jail-coeff-grps'] = zeros

        if 'probation' not in p_names:
            self.ode_params['commit-to-probation-coeff-grps'] = zeros

        if 'prison' not in p_names:
            self.ode_params['commit-to-prison-coeff-grps'] = zeros

        return
