#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org

import pickle
import logging

import numpy as np
import scipy.constants as const
from scipy.integrate import odeint

from cortix import Module
from cortix import Phase
from cortix import Quantity

class State(Module):
    '''
    State Cortix module used to model non-offender  group population transit from and to
    a state. This assumes various ports of communication with other states,
    and an internal port to the internal Community.

    Notes
    -----
    These are the `port` names available in this module to connect to other `State`
    modules: `inflow:id`, `outflow:id`.
    In addition this module takes an internal network to model the free-offenders
    community of people. The port used for this connection is `community`.
    See instance attribute `port_names_expected`.

    '''

    def __init__(self, name, non_offender_adult_population=100):
        '''
        Parameters
        ----------
        non_offender_adult_population: float
            Individuals reaching the adult age (SI) unit. Default: 100.

        '''

        super().__init__()

        self.name = name

        #self.port_names_expected = ['inflow:','outflow:','community']

        quantities      = list()
        self.ode_params = dict()

        self.initial_time = 0.0 * const.day
        self.end_time     = 100 * const.day
        self.time_step    = 0.5 * const.day
        self.show_time    = (False,10*const.day)
        self.log = logging.getLogger('cortix')

        # State population
        fs_0 = non_offender_adult_population
        fs = Quantity(name='fs', formalName='non-offender-pop',
                unit='individual', value=fs_0)
        quantities.append(fs)

        # Model parameters: commitment coefficients and their modifiers

        i = 1
        for p in self.ports:

            if p.name.strip().split(':')[0] == 'outflow':

                # Non-offenders move to outside the state
                cso_0 = np.random.random(1) / (60*const.day)
                cso = Quantity(name='cso-'+stri(i), formalName='commit-out-coeff-'+str(i),
                       unit='individual', value=cso_0)
                self.ode_params['commit-out-coeff-'+str(i)] = cso_0
                quantities.append(c0rg)

                mso = Quantity(name='mso', formalName='commit-arrested-coeff-mod-grps',
                   unit='individual', value=m0rg_0)
                self.ode_params['commit-to-arrested-coeff-mod-grps'] = m0rg_0
                quantities.append(m0rg)

        # Death term
        self.ode_params['death-rates'] = np.zeros(1)

        # Maturity source rate term
        self.ode_params['maturity-rate'] = np.ones(1)

        # Phase state
        self.population_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        self.population_phase.SetValue('fs', fs_0, self.initial_time)

        # Initialize inflows to zero
        #self.ode_params['prison-inflow-rates']       = np.zeros(self.n_groups)
        #self.ode_params['parole-inflow-rates']       = np.zeros(self.n_groups)
        #self.ode_params['arrested-inflow-rates']     = np.zeros(self.n_groups)
        #self.ode_params['jail-inflow-rates']         = np.zeros(self.n_groups)
        #self.ode_params['adjudication-inflow-rates'] = np.zeros(self.n_groups)
        #self.ode_params['probation-inflow-rates']    = np.zeros(self.n_groups)

        # Set the state to the phase state
        self.state = self.population_phase

        return

    def run(self, *args):

        self.__zero_ode_parameters()

        time = self.initial_time

        while time < self.end_time:

            if self.show_time[0] and abs(time%self.show_time[1]-0.0)<=1.e-1:
                self.log.info('Community::time[d] = '+str(round(time/const.day,1)))

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

            # Evolve offenders group population to the next time stamp
            #---------------------------------------------------------

            time = self.__step( time )

        # Share state with parent process
        if self.use_processing:
            try:
                pickle.dumps(self.state)
            except pickle.PicklingError:
                args[1].put((args[0],None))
            else:
                args[1].put((args[0],self.state))

    def __rhs_fn(self, u_vec, t, params):

        f0g = u_vec  # offender population groups

        prison_inflow_rates       = params['prison-inflow-rates']
        parole_inflow_rates       = params['parole-inflow-rates']
        arrested_inflow_rates     = params['arrested-inflow-rates']
        jail_inflow_rates         = params['jail-inflow-rates']
        adjudication_inflow_rates = params['adjudication-inflow-rates']
        probation_inflow_rates    = params['probation-inflow-rates']

        inflow_rates = prison_inflow_rates + parole_inflow_rates +\
                       arrested_inflow_rates + jail_inflow_rates +\
                       adjudication_inflow_rates + probation_inflow_rates

        c0rg = self.ode_params['commit-to-arrested-coeff-grps']
        m0rg = self.ode_params['commit-to-arrested-coeff-mod-grps']

        c00g = self.ode_params['general-commit-to-arrested-coeff-grps']
        m00g = self.ode_params['general-commit-to-arrested-coeff-mod-grps']

        maturity_rate = params['maturity-rate']

        outflow_rates = c0rg * m0rg * f0g + c00g * m00g * maturity_rate

        death_rates = params['death-rates']

        dt_f0g = inflow_rates - outflow_rates - death_rates

        return dt_f0g

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

        u_vec_0 = self.population_phase.GetValue('f0g', time)
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
        self.population_phase.SetValue('f0g', u_vec, time)

        return time

    def __compute_outflow_rates(self, time, name):

        f0g = self.population_phase.GetValue('f0g',time)

        if name == 'arrested':

            c0rg = self.ode_params['commit-to-arrested-coeff-grps']
            m0rg = self.ode_params['commit-to-arrested-coeff-mod-grps']

            c00g = self.ode_params['general-commit-to-arrested-coeff-grps']
            m00g = self.ode_params['general-commit-to-arrested-coeff-mod-grps']

            f0 = self.ode_params['maturity-rate']

            outflow_rates = c0rg * m0rg * f0g + c00g * m00g * f0

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
