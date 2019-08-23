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

        self.initial_time = 0.0 * const.day
        self.end_time     = 100 * const.day
        self.time_step    = 0.5 * const.day

        # Population groups
        self.n_groups = n_groups

        # Adjudication population groups
        fag_0 = np.random.random(self.n_groups) * pool_size
        fag = Quantity(name='fag', formalName='adjudication-pop-grps',
                unit='individual', value=fag_0)
        quantities.append(fag)

        # Model parameters: commitment coefficients and their modifiers

        # Adjudication to community
        ca0g_0 = np.random.random(self.n_groups) / const.day
        ca0g = Quantity(name='ca0g', formalName='commit-community-coeff-grps',
               unit='individual', value=ca0g_0)
        self.ode_params['commit-to-community-coeff-grps'] = ca0g_0
        quantities.append(ca0g)

        ma0g_0 = np.random.random(self.n_groups)
        ma0g = Quantity(name='ma0g', formalName='commit-community-coeff-mod-grps',
               unit='individual', value=ma0g_0)
        self.ode_params['commit-to-community-coeff-mod-grps'] = ma0g_0
        quantities.append(ma0g)

        # Adjudication to jail    
        cajg_0 = np.random.random(self.n_groups) / const.day
        cajg = Quantity(name='cajg', formalName='commit-parole-coeff-grps',
               unit='individual', value=cajg_0)
        self.ode_params['commit-to-jail-coeff-grps'] = cajg_0
        quantities.append(cajg)

        majg_0 = np.random.random(self.n_groups)
        majg = Quantity(name='majg', formalName='commit-parole-coeff-mod-grps',
               unit='individual', value=majg_0)
        self.ode_params['commit-to-jail-coeff-mod-grps'] = majg_0
        quantities.append(majg)

        # Adjudication to probation
        cabg_0 = np.random.random(self.n_groups) / const.day
        cabg = Quantity(name='cabg', formalName='commit-probation-coeff-grps',
               unit='individual', value=cabg_0)
        self.ode_params['commit-to-probation-coeff-grps'] = cabg_0
        quantities.append(cabg)

        mabg_0 = np.random.random(self.n_groups)
        mabg = Quantity(name='mabg', formalName='commit-probation-coeff-mod-grps',
               unit='individual', value=mabg_0)
        self.ode_params['commit-to-probation-coeff-mod-grps'] = mabg_0
        quantities.append(mabg)

        # Adjudication to prison    
        capg_0 = np.random.random(self.n_groups) / const.day
        capg = Quantity(name='capg', formalName='commit-prison-coeff-grps',
               unit='individual', value=capg_0)
        self.ode_params['commit-to-prison-coeff-grps'] = capg_0
        quantities.append(capg)

        mapg_0 = np.random.random(self.n_groups)
        mapg = Quantity(name='mapg', formalName='commit-prison-coeff-mod-grps',
               unit='individual', value=mapg_0)
        self.ode_params['commit-to-prison-coeff-mod-grps'] = mapg_0
        quantities.append(mapg)

        # Death term
        self.ode_params['death-rates'] = np.zeros(self.n_groups)

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

        while time < self.end_time:

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
        ma0g = self.ode_params['commit-to-community-coeff-mod-grps']

        cajg = self.ode_params['commit-to-jail-coeff-grps']
        majg = self.ode_params['commit-to-jail-coeff-mod-grps']

        cabg = self.ode_params['commit-to-probation-coeff-grps']
        mabg = self.ode_params['commit-to-probation-coeff-mod-grps']

        capg = self.ode_params['commit-to-prison-coeff-grps']
        mapg = self.ode_params['commit-to-prison-coeff-mod-grps']

        outflow_rates = ( ca0g * ma0g + cajg * majg + cabg * mabg + capg * mapg ) * fag

        assert np.all(outflow_rates>=0.0), 'values: %r'%outflow_rates

        death_rates = params['death-rates']

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
            mapg = self.ode_params['commit-to-prison-coeff-mod-grps']

            outflow_rates = capg * mapg * fag

        if name == 'probation':

            cabg = self.ode_params['commit-to-probation-coeff-grps']
            mabg = self.ode_params['commit-to-probation-coeff-mod-grps']

            outflow_rates = cabg * mabg * fag

        if name == 'jail':

            cajg = self.ode_params['commit-to-jail-coeff-grps']
            majg = self.ode_params['commit-to-jail-coeff-mod-grps']

            outflow_rates = cajg * majg * fag

        if name == 'community':

            ca0g = self.ode_params['commit-to-community-coeff-grps']
            ma0g = self.ode_params['commit-to-community-coeff-mod-grps']

            outflow_rates = ca0g * ma0g * fag

        return outflow_rates

    def __zero_ode_parameters(self):
        '''
        Zero the outflows of unconnected ports.

        '''

        zeros = np.zeros(self.n_groups)

        p_names = [p.name for p in self.ports]

        if 'community' not in p_names:
            self.ode_params['commit-to-community-coeff-grps']     = zeros
            self.ode_params['commit-to-community-coeff-mod-grps'] = zeros

        if 'jail' not in p_names:
            self.ode_params['commit-to-jail-coeff-grps'] = zeros
            self.ode_params['commit-to-jail-coeff-mod-grps'] = zeros

        if 'probation' not in p_names:
            self.ode_params['commit-to-probation-coeff-grps'] = zeros
            self.ode_params['commit-to-probation-coeff-mod-grps'] = zeros

        if 'prison' not in p_names:
            self.ode_params['commit-to-prison-coeff-grps'] = zeros
            self.ode_params['commit-to-prison-coeff-mod-grps'] = zeros

        return
