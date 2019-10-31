#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org

import logging

import numpy as np
import scipy.constants as const
from scipy.integrate import odeint

from cortix import Module
from cortix.support.phase_new import PhaseNew as Phase
from cortix import Quantity

class BWR(Module):
    '''
    Boiling water reactor single-point reactor.

    Notes
    -----
    These are the `port` names available in this module to connect to respective
    modules: `turbine`, and `pump`.
    See instance attribute `port_names_expected`.

    '''

    def __init__(self, params):
        '''
        Parameters
        ----------
        params: dict
            All parameters for the module in the form of a dictionary.

        '''

        super().__init__()

        self.port_names_expected = ['coolant-inflow','coolant-outflow']

        quantities      = list()
        self.ode_params = dict()

        self.initial_time = 0.0 * const.day
        self.end_time     = 100 * const.day
        self.time_step    = 0.5 * const.day
        self.show_time    = (False,10*const.day)

        self.log = logging.getLogger('cortix')

        # Community offender population groups removed from circulation
        f0g_0 = np.random.random(self.n_groups) * offender_pool_size
        f0g = Quantity(name='f0g', formalName='offender-pop-grps',
                unit='individual', value=f0g_0)
        quantities.append(f0g)

        # Coolant inflow phase history
        quantities = list()

        flowrate = Quantitiy(name='inflow-cool-flowrate',
                   formalName='Inflow Cool. Flowrate',
                   unit='kg/s', value=0.0)
        quantities.append(flowrate)

        temp = Quantitiy(name='inflow-cool-temp', formalName='Inflow Cool. Temperature',
               unit='K', value=0.0)
        quantities.append(temp)

        press = Quantitiy(name='inflow-cool-press',formalName='Inflow Cool. Pressure',
                unit='Pa', value=0.0)
        quantities.append(press)

        self.coolant_inflow_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        # Coolant outflow phase history
        quantities = list()

        flowrate = Quantitiy(name='outflow-cool-flowrate',
                   formalName='Outflow Cool. Flowrate',
                   unit='kg/s', value=0.0)
        quantities.append(flowrate)

        temp = Quantitiy(name='outflow-cool-temp',
                   formalName='Outflow Cool. Temperature',
                   unit='K', value=0.0)
        quantities.append(temp)

        press = Quantitiy(name='outflow-cool-press',formalName='Outflow Cool. Pressure',
                   unit='Pa', value=0.0)
        quantities.append(press)

        quality = Quantitiy(name='steam-quality',formalName='Steam Quality',
                   unit='', value=0.0)
        quantities.append(quality)

        self.coolant_outflow_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        # Neutron phase history
        quantities = list()

        neutron_dens = Quantitiy(name='neutron-dens',
                   formalName='Neutron Dens.',
                   unit='1/m^3', value=0.0)
        quantities.append(neutron_dens)

        delayed_neutrons_0 = np.zeros(6)

        delayed_neutron_cc = Quantitiy(name='delayed-neutrons-cc',
                   formalName='Delayed Neutrons',
                   unit='1/m^3', value=delayed_neutrons_0)
        quantities.append(delayed_neutron_cc)

        self.neutron_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        #self.population_phase.SetValue('f0g', f0g_0, self.initial_time)

        # Initialize inflows to zero
        #self.ode_params['prison-inflow-rates']       = np.zeros(self.n_groups)
        #self.ode_params['parole-inflow-rates']       = np.zeros(self.n_groups)
        #self.ode_params['arrested-inflow-rates']     = np.zeros(self.n_groups)
        #self.ode_params['jail-inflow-rates']         = np.zeros(self.n_groups)
        #self.ode_params['adjudication-inflow-rates'] = np.zeros(self.n_groups)
        #self.ode_params['probation-inflow-rates']    = np.zeros(self.n_groups)

        return

    def run(self, *args):

        self.__zero_ode_parameters()

        time = self.initial_time

        while time < self.end_time:

            if self.show_time[0] and abs(time%self.show_time[1]-0.0)<=1.e-1:
                self.log.info('Community::time[d] = '+str(round(time/const.day,1)))

            # Communicate information
            #------------------------

            self.__call_ports(time)

            # Evolve one time step
            #---------------------

            time = self.__step( time )

    def __call_ports(self, time):

            # Interactions in the coolant-inflow port
            #----------------------------------------
            # one way "from" coolant-inflow

            # from
            self.send( time, 'coolant-inflow' )
            (check_time, inflow_state) = self.recv('coolant-inflow')
            assert abs(check_time-time) <= 1e-6
            self.ode_params['inflow-state'] = inflow_state

            # Interactions in the coolant-outflow port
            #-----------------------------------------
            # one way "to" coolant-outflow

            # to
            message_time = self.recv('coolant-outflow')
            outflow_state = self.__compute_outflow_state( message_time )
            self.send( (message_time, outflow_state), 'coolant-outflow' )

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
        u_0 = self.__get_state_vector( time )

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

    def __get_state_vector(self, time):
        '''
        Return a numpy array of all unknowns ordered as below:
            neutron density (1), delayed neutron emmiter concentrations (6),
            termperature of fuel (1), temperature of coolant (1).
        '''

        u_list = list()

        u_vec = np.empty(0,dtype=np.float64)

        neutron_dens = self.neutron_phase.get_value('neutron-dens',time)
        u_vec = np.append( u_vec, neutron_dens )

        delayed_neutrons_cc = self.neutron_phase.get_value('delayed-neutrons-cc',time)
        u_vec = np.append( u_vec, delayed_neutrons_cc )

        fuel_temp = self.neutron_phase.get_value('delayed-neutrons-cc',time)
        u_vec = np.append( u_vec, delayed_neutrons_cc )


        for spc in self.aqueous_phase.species:
            #mass_cc = self.aqueous_phase.get_species_concentration(spc.name,time)
            mass_cc = self.aqueous_phase.get_species_concentration(spc.name)
            assert mass_cc is not None
            u_list.append( mass_cc )
            spc.flag = idx # the global id of the species
            idx += 1

        for spc in self.organic_phase.species:
            #mass_cc = self.organic_phase.get_species_concentration(spc.name,time)
            mass_cc = self.organic_phase.get_species_concentration(spc.name)
            assert mass_cc is not None
            u_list.append( mass_cc )
            spc.flag = idx # the global id of the species
            idx += 1

        for spc in self.vapor_phase.species:
            #mass_cc = self.vapor_phase.get_species_concentration(spc.name,time)
            mass_cc = self.vapor_phase.get_species_concentration(spc.name)
            assert mass_cc is not None
            u_list.append( mass_cc )
            spc.flag = idx # the global id of the species
            idx += 1

        u_vec = np.array( u_list, dtype=np.float64 )

        # sanity check
        assert not u_vec[u_vec<0.0],'%r'%u_vec

        return u_vec

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
