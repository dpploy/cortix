#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org

import pickle

import numpy as np
import scipy.constants as const
from scipy.integrate import odeint
from cortix.src.module import Module
from cortix.support.phase import Phase
from cortix.support.quantity import Quantity

class Adjudication(Module):
    '''
    Prison Cortix module used to model criminal group population in a prison.

    Note
    ----
    `probation`: this is a `port` for the rate of population groups to/from the
        Probation domain.

    `jail`: this is a `port` for the rate of population groups to/from the Jail
        domain module.

    `arrested`: this is a `port` for the rate of population groups to/from the
        Arrested domain module.

    `prison`: this is a `port` for the rate of population groups to/from the
        Prison domain module.

    `freedom`: this is a `port` for the rate of population groups to/from the Freedom
        domain module.

    `visualization`: this is a `port` that sends data to a visualization module.
    '''

    def __init__(self, n_groups=1):

        super().__init__()

        quantities      = list()
        self.ode_params = dict()

        self.initial_time = 0.0 * const.day
        self.end_time     = 100 * const.day
        self.time_step    = 0.5 * const.day

        # Population groups
        self.n_groups = n_groups
        factor = 100.0 # percent basis

        # Adjudication population groups
        fag_0 = np.random.random(self.n_groups) * factor
        fag = Quantity(name='fag', formalName='adjudication-pop-grps',
                unit='individual', value=fag_0)
        quantities.append(fag)

        # Model parameters: commitment coefficients and their modifiers

        # Adjudication to freedom
        ca0g_0 = np.random.random(self.n_groups) / const.day
        ca0g = Quantity(name='ca0g', formalName='commit-freedom-coeff-grps',
               unit='individual', value=ca0g_0)
        self.ode_params['commit-to-freedom-coeff-grps'] = ca0g_0
        quantities.append(ca0g)

        ma0g_0 = np.random.random(self.n_groups)
        ma0g = Quantity(name='ma0g', formalName='commit-freedom-coeff-mod-grps',
               unit='individual', value=ma0g_0)
        self.ode_params['commit-to-freedom-coeff-mod-grps'] = ma0g_0
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
        self.ode_params['prison-death-rates'] = np.zeros(self.n_groups)

        # Phase state
        self.population_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        self.population_phase.SetValue('fag', fag_0, self.initial_time)

        # Set the state to the phase state
        self.state = self.population_phase

        return

    def run(self, state_comm=None, idx_comm=None):

        time = self.initial_time

        while time < self.end_time:

            # Interactions in the prison port
            #--------------------------------

            message_time = self.recv('prison')
            prison_outflow_rates = self.compute_outflow_rates( message_time, 'prison' )
            self.send( (message_time, prison_outflow_rates), 'prison' )

            # Interactions in the arrested port
            #----------------------------------

            self.ode_params['arrested-inflow-rates'] = np.ones(self.n_groups) / const.day

            # Interactions in the freedom port
            #------------------------------

            # compute freedom outflow rate

            # Interactions in the visualization port
            #---------------------------------------

            fag = self.population_phase.GetValue('fag')
            self.send( fag, 'visualization' )

            # Evolve prison group population to the next time stamp
            #------------------------------------------------------

            time = self.step( time )

        self.send('DONE', 'visualization') # this should not be needed: TODO

        if state_comm:
            try:
                pickle.dumps(self.state)
            except pickle.PicklingError:
                state_comm.put((idx_comm,None))
            else:
                state_comm.put((idx_comm,self.state))

    def rhs_fn(self, u_vec, t, params):

        fag = u_vec  # prison population groups

        arrested_inflow_rates = params['arrested-inflow-rates']

        inflow_rates  = arrested_inflow_rates

        ca0g = self.ode_params['commit-to-freedom-coeff-grps']
        ma0g = self.ode_params['commit-to-freedom-coeff-mod-grps']

        cajg = self.ode_params['commit-to-jail-coeff-grps']
        majg = self.ode_params['commit-to-jail-coeff-mod-grps']

        cabg = self.ode_params['commit-to-probation-coeff-grps']
        mabg = self.ode_params['commit-to-probation-coeff-mod-grps']

        capg = self.ode_params['commit-to-prison-coeff-grps']
        mapg = self.ode_params['commit-to-prison-coeff-mod-grps']

        outflow_rates = ( ca0g * ma0g + cajg * majg + cabg * mabg + capg * mapg ) * fag

        death_rates = params['prison-death-rates']

        dt_fag = inflow_rates - outflow_rates - death_rates

        return dt_fag

    def step(self, time=0.0):
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

        u_vec_0 = self.population_phase.GetValue('fag', time)
        t_interval_sec = np.linspace(0.0, self.time_step, num=2)

        (u_vec_hist, info_dict) = odeint(self.rhs_fn,
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

    def compute_outflow_rates(self, time, name):

        fag = self.population_phase.GetValue('fag',time)

        if name == 'prison':

            capg = self.ode_params['commit-to-prison-coeff-grps']
            mapg = self.ode_params['commit-to-prison-coeff-mod-grps']

            outflow_rates = capg * mapg * fag

            return outflow_rates

        if name == 'probation':

            cabg = self.ode_params['commit-to-probation-coeff-grps']
            mabg = self.ode_params['commit-to-probation-coeff-mod-grps']

            outflow_rates = cabg * mabg * fag

            return outflow_rates

        if name == 'jail':

            cajg = self.ode_params['commit-to-jail-coeff-grps']
            majg = self.ode_params['commit-to-jail-coeff-mod-grps']

            outflow_rates = cajg * majg * fag

            return outflow_rates

        if name == 'freedom':

            ca0g = self.ode_params['commit-to-freedom-coeff-grps']
            ma0g = self.ode_params['commit-to-freedom-coeff-mod-grps']

            outflow_rates = ca0g * ma0g * fag

            return outflow_rates
