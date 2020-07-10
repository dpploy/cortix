#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org

import logging

import numpy as np
import scipy.constants as unit
from scipy.integrate import odeint
import math

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

        self.port_names_expected = ['coolant-inflow', 'coolant-outflow',
                                     'signal-out', 'signal-in']

        self.params = params

        self.initial_time = 0.0 * unit.day
        self.end_time     = 4 * unit.hour
        self.time_step    = 10.0

        self.show_time    = (False,10.0)

        self.log = logging.getLogger('cortix')

        # Coolant outflow phase history
        quantities = list()

        flowrate = Quantity(name='flowrate', formal_name='q_c', unit='kg/s', value=0.0,
                info='Reactor Outflow Coolant Flowrate' ,latex_name='$q_c$')

        quantities.append(flowrate)

        temp = Quantity(name='temp', formal_name='T_c', unit='K', value=273.15,
                info='Reactor Outflow Coolant Temperature', latex_name='$T_c$')

        quantities.append(temp)

        press = Quantity(name='pressure', formal_name='P_c', unit='Pa', value=0.0,
                info='Reactor Outflow Coolant Pressure', latex_name='$P_c$')

        quantities.append(press)

        quality = Quantity(name='steam-quality', formal_name='chi_s', unit='', value=0.0,
                info='Reactor STeam Quality', latex_name='$\chi$')

        quantities.append(quality)

        self.coolant_outflow_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        # Neutron phase history
        quantities = list()

        neutron_dens = Quantity(name='neutron-dens', formal_name='n', unit='1/m^3',
                value=0.0, info='Rel. Reactor Neutron Density', latex_name='$n$')

        quantities.append(neutron_dens)

        delayed_neutrons_0 = np.zeros(6)

        delayed_neutron_cc = Quantity(name='delayed-neutrons-cc', formal_name='c_i',
                unit='1/m^3 ', value=delayed_neutrons_0,
                info='Rel. Delayed Neutron Precursors', latex_name='$c_i$')

        quantities.append(delayed_neutron_cc)

        self.neutron_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        #reactor paramaters
        quantities = list()

        fuel_temp = Quantity( name='fuel-temp', formalName='T_f', unit='k',
                value=273.15, info='Reactor Nuclear Fuel Temperature',
                latex_name='$T_f$')

        quantities.append(fuel_temp)

        reg_rod_position = Quantity(name='reg-rod-position',
                formal_name = 'reg rod position', unit='m', value=0.0,
                info='Reactor Regulating Rod Position', latex_name='$x_p$')

        quantities.append(reg_rod_position)

        self.reactor_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        # Initialize inflow
        self.params['inflow-cool-temp'] = 273.15

        return

    def run(self, *args):

        # Some logic for logging time stamps
        if self.initial_time + self.time_step > self.end_time:
            self.end_time = self.initial_time + self.time_step

        time = self.initial_time
        print_time = self.initial_time
        print_time_step = self.show_time[1]
        if print_time_step < self.time_step:
            print_time_step = self.time_step

        while time <= self.end_time:

            last_time_stamp = time - self.time_step

            if self.show_time[0] and time>=print_time and \
                    time<print_time+print_time_step:

                self.log.info( self.name+'::run():time[m]='+
                        str(round(time/unit.minute,1)))

                self.__logit = True
                print_time += self.show_time[1]

            else:
                self.__logit = False

            # Communicate information
            #------------------------
            self.__call_ports(time)

            # Evolve one time step
            #---------------------

            time = self.__step( time )

    def __call_ports(self, time):

        # Interactions in the coolant-outflow port
        #-----------------------------------------
        # one way "to" coolant-outflow

        # send to 
        if self.get_port('coolant-outflow').connected_port:

            message_time = self.recv('coolant-outflow')

            coolant_outflow = self.__get_coolant_outflow( message_time )
            outflow_params = dict()
            self.send( (message_time, coolant_outflow), 'coolant-outflow' )

        # Interactions in the coolant-inflow port
        #----------------------------------------
        # one way "from" coolant-inflow

        #self.send( time, 'coolant-inflow' )

        # receive from
        if self.get_port('coolant-inflow').connected_port:

            self.send( time, 'coolant-inflow' )
            (check_time, inflow_cool_temp) = self.recv('coolant-inflow')

            assert abs(check_time-time) <= 1e-6
            self.params['inflow-cool-temp'] = inflow_cool_temp

        # Interactions in the signal-out port
        #-----------------------------------------
        # one way "to" signal-out 

        # send to 
        if self.get_port('signal-out').connected_port:

            message_time = self.recv('signal-out')

            signal_out = self.__get_signal_out(time)

            self.send( (message_time, signal_out), 'signal-out' )

    def __get_coolant_outflow(message_time):

        outflow = self.params['coolant-outflow']
        return(outflow)

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
        import iapws.iapws97 as steam

        # Get state values
        u_0 = self.__get_state_vector( time )

        t_interval_sec = np.linspace(time, time+self.time_step, num=2)

        (u_vec_hist, info_dict) = odeint( self.__f_vec,
                                          u_0, t_interval_sec,
                                          args=( self.params, ),
                                          rtol=1e-4, atol=1e-8, mxstep=200,
                                          full_output=True )

        assert info_dict['message'] =='Integration successful.', info_dict['message']

        u_vec = u_vec_hist[1,:]  # solution vector at final time step

        n_dens    = u_vec[0]
        c_vec     = u_vec[1:7]
        fuel_temp = u_vec[7]
        cool_temp = u_vec[8]

        #update state variables
        outflow  = self.coolant_outflow_phase.get_row(time)
        neutrons = self.neutron_phase.get_row(time)
        reactor  = self.reactor_phase.get_row(time)
        self.params['outflow temp'] = cool_temp
        time += self.time_step

        self.coolant_outflow_phase.add_row(time, outflow)
        self.neutron_phase.add_row(time, neutrons)
        self.reactor_phase.add_row(time, reactor)

        self.coolant_outflow_phase.set_value('temp', cool_temp, time)
        self.neutron_phase.set_value('neutron-dens', n_dens, time)
        self.neutron_phase.set_value('delayed-neutrons-cc', c_vec, time)
        self.reactor_phase.set_value('fuel-temp', fuel_temp, time)

        return time

    def __signal_out(self, time=0.0):
        '''
        Send reactor signals to anyone requesting it.

        Parameters
        ----------
        time: float
            Time in SI unit.

        Returns
        -------
        None

        '''

        signals = dict()

        return signals

    def __get_coolant_outflow(self, time=0.0):
        '''
        Get the coolant outflow stream.

        Parameters
        ----------
        time: float
            Time in SI unit.

        Returns
        -------
        None

        '''

        coolant_outflow_stream = dict()

        outflow_cool_temp = self.coolant_outflow_phase.get_value('temp', time)

        coolant_outflow_stream['temp'] = outflow_cool_temp
        coolant_outflow_stream['quality'] = 0.7
        return coolant_outflow_stream

    def __get_state_vector(self, time):
        '''
        Return a numpy array of all unknowns ordered as below:
            neutron density (1), delayed neutron emmiter concentrations (6),
            termperature of fuel (1), temperature of coolant (1).
        '''

        u_vec = np.empty(0,dtype=np.float64)

        neutron_dens = self.neutron_phase.get_value('neutron-dens',time)
        u_vec = np.append( u_vec, neutron_dens )

        delayed_neutrons_cc = self.neutron_phase.get_value('delayed-neutrons-cc',time)
        u_vec = np.append(u_vec, delayed_neutrons_cc)

        fuel_temp = self.reactor_phase.get_value('fuel-temp',time)
        u_vec = np.append( u_vec, fuel_temp)

        temp = self.coolant_outflow_phase.get_value('temp',time)
        u_vec = np.append(u_vec, temp)

        # sanity check

        return u_vec

    def __alpha_tn_func(self, temp, params):
        import math
        import scipy.misc as diff
        import scipy.constants as unit
        import iapws.iapws97 as steam
        import iapws.iapws95 as steam2

        pressure = steam._PSat_T(temp)

        d_rho = steam2.IAPWS95(P=pressure, T=temp-1).drhodT_P

        #d_rho2 = diff.derivative(derivative_helper, temp) # dRho/dTm

        rho = 1 / steam._Region4(pressure, 0)['v'] # mass density, kg/m3

        Nm = ((rho * unit.kilo)/params['mod molar mass']) * unit.N_A * (unit.centi)**3 # number density of the moderator
        d_Nm =  ((d_rho * unit.kilo)/params['mod molar mass']) * unit.N_A * (unit.centi)**3 #dNm/dTm
        d_Nm = d_Nm * unit.zepto * unit.milli

        mod_macro_a = params['mod micro a'] * Nm # macroscopic absorption cross section of the moderator
        mod_macro_s = params['mod micro s'] * Nm # macroscopic scattering cross section of the moderator

        F = params['fuel macro a']/(params['fuel macro a'] + mod_macro_a) # thermal utilization, F
    #dF/dTm
        d_F = -1*(params['fuel macro a'] * params['mod micro a'] * d_Nm)/(params['fuel macro a'] + mod_macro_a)**2

        # Resonance escape integral, P
        P = math.exp((-1 * params['n fuel'] * (params['fuel_volume']) * params['I'])/(mod_macro_s * 3000))
        #dP/dTm
        d_P = P * (-1 * params['n fuel'] * params['fuel_volume'] * unit.centi**3 * params['mod micro s'] * d_Nm)/(mod_macro_s * 3000 * unit.centi**3)**2

        Eth = 0.0862 * temp # convert temperature to energy in MeV
        E1 = mod_macro_s/math.log(params['E0']/Eth) # neutron thermalization macroscopic cross section

        Df = 1/(3 * mod_macro_s * (1 - params['mod mu0'])) # neutron diffusion coefficient
        tau = Df/E1 # fermi age, tau
        #dTau/dTm
        d_tau = (((0.0862 * (Eth/params['E0'])) * 3 * Nm) - math.log(params['E0']/Eth) * (params['mod micro s'] * d_Nm))/((3 * Nm)**2 * (1 - params['mod mu0']))

        L = math.sqrt(1/(3 * mod_macro_s * mod_macro_a * (1 - params['mod mu0']))) # diffusion length L
        # dL/dTm
        d_L = 1/(2 * math.sqrt((-2 * d_Nm * unit.zepto * unit.milli)/(3 * params['mod micro s'] * params['mod micro a'] * (Nm * unit.zepto * unit.milli)**3 * (1 - params['mod mu0']))))

        # left term of the numerator of the moderator temperature feedback coefficient, alpha
        left_1st_term = d_tau * (params['buckling']**2 + L**2 * params['buckling']**4) #holding L as constant
        left_2nd_term = d_L * (2 * L * params['buckling']**2 + 2 * L * tau * params['buckling']**4) # holding tau as constant
        left_term = (P * F) * (left_1st_term + left_2nd_term) # combining with P and F held as constant

        # right term of the numerator of the moderator temperature feedback coefficient, alpha

        right_1st_term = (-1) * (1 + ((tau + L**2) * params['buckling']**2) + tau * L**2 * params['buckling']**4) # num as const
        right_2nd_term = F * d_P # holding thermal utilization as constant
        right_3rd_term = P * d_F # holding resonance escpae as constant
        right_term = right_1st_term * (right_2nd_term + right_3rd_term) # combining all three terms together

        # numerator and denominator
        numerator = left_term + right_term
        denominator = params['eta'] * params['epsilon'] * (F * P)**2

        alpha_tn = numerator/denominator


        alpha_tn = alpha_tn/3
        return alpha_tn

    def __rho_func(self, time, n_dens, temp, params, ):
        '''
        Reactivity function.

        Parameters
        ----------
        t: float, required
            Time.
        temp_f: float, required
            Temperature at time t.
        params: dict, required
            Dictionary of quantities. It must have a `'rho_0'` key/value pair.

        Returns
        -------
        rho_t: float
            Value of reactivity.

        Examples
        --------
        '''

        rho_0    = params['rho_0']
        temp_ref = params['temp_0']
        n_dens_ss_operation = params['n_dens_ss_operation']
        alpha_n  = params['alpha_n']

        if temp < 293.15: # if temperature is less than the starting temperature then moderator feedback is zero
            alpha_tn = 0

        else:
            alpha_tn = self.__alpha_tn_func(temp , self.params) #alpha_tn_func(temp, params)

        if time > params['malfunction start'] and time < params['malfunction end']: # reg rod held in position; only mod temp reactivity varies with time during malfunction
            alpha_n = params['alpha_n_malfunction']
            rho_t = rho_0 + alpha_n + alpha_tn * (temp - temp_ref)

        elif time > params['shutdown time']: # effectively the inverse of startup; gradually reduce reactivity and neutron density.
            rho_0 = -1 * rho_0
            alpha_n = rho_0 - (alpha_tn * (temp - temp_ref))
            rho_t = rho_0

        elif n_dens < 1e-5: #controlled startup w/ blade; gradually increase neutron density to SS value.
            #rho_current = (1 - n_dens) * rho_0
            #alpha_n = rho_current - rho_0 - alpha_tn * (temp - temp_ref)
            #rho_t = rho_current
            #params['alpha_n_malfunction'] = alpha_n
            rho_t = rho_0

        else:
            rho_current = (1 - n_dens) * rho_0
            alphh_n = rho_current - rho_0 - alpha_tn * (temp - temp_ref)
            rho_t = rho_current
            params['alpha_n_malfunction'] = alpha_n
        #print(n_dens)

        return (rho_t, alpha_n, alpha_tn * (temp - temp_ref))

    def __q_source(self, time, params):
        '''
        Neutron source delta function.

        Parameters
        ----------
        t: float, required
            Time.
        params: dict, required
            Dictionary of quantities. It must have a `'q_0'` key/value pair.

        Returns
        -------
        q: float
            Value of source.

        Examples
        --------
        '''
        q_0 = params['q_0']

        if time <= 1500: # small time value
            q = q_0
        else:
            q = 0.0
            params['q_source_status'] = 'out'

        return q

    def __sigma_fis_func(self, temp, params):
        '''
        Place holder for implementation
        '''
        sigma_f = params['sigma_f_o']  * math.sqrt(298/temp) * math.sqrt(math.pi) * 0.5

        return(sigma_f)

    def __nuclear_pwr_dens_func(self, time, temp, n_dens, params ):
        '''
        Place holder for implementation
        '''
        n_dens = n_dens + self.__q_source(time, self.params) # include the neutrons from the initial source

        rxn_heat = params['fis_energy'] # get fission reaction energy J per reaction

        sigma_f = self.__sigma_fis_func( temp, self.params ) # m2

        fis_nuclide_num_dens = params['fis_nuclide_num_dens_fake'] #  #/m3

        Sigma_fis = sigma_f * fis_nuclide_num_dens # macroscopic cross section

        v_o = params['thermal_neutron_velo'] # m/s

        neutron_flux = n_dens * 0.95E15 * v_o * sigma_f/params['sigma_f_o']*0.7

         #reaction rate density
        rxn_rate_dens = Sigma_fis * neutron_flux

        # nuclear power source
        q3prime = - rxn_heat * rxn_rate_dens # exothermic reaction W/m3)
        #q3prime = - n_dens * 3323E6
        #print("q3prime")
        #print(q3prime)

        return q3prime

    def __heat_sink_rate(self, time, temp_f, temp_c, params):

        ht_coeff = params['ht_coeff']

        q_f = - ht_coeff * (temp_f - temp_c)
        #print(q_f)
        return q_f

    def __f_vec(self, u_vec, time, params):
        num_negatives = u_vec[u_vec < 0]

        if num_negatives.any() < 0:
            assert np.max(abs(u_vec[u_vec < 0])) <= 1e-8, 'u_vec = %r'%u_vec

        #assert np.all(u_vec >= 0.0), 'u_vec = %r'%u_vec
        q_source_t = self.__q_source(time, self.params)

        n_dens = u_vec[0] # get neutron dens

        c_vec  = u_vec[1:-2] # get delayed neutron emitter concentration

        temp_f = u_vec[-2] # get temperature of fuel

        temp_c = u_vec[-1] # get temperature of coolant

        # initialize f_vec to zero 
        species_decay = params['species_decay']
        lambda_vec = np.array(species_decay)
        n_species  = len(lambda_vec)

        f_tmp = np.zeros(1+n_species+2,dtype=np.float64) # vector for f_vec return

        #----------------
        # neutron balance
        #----------------
        rho_t = self.__rho_func(time, n_dens, temp_c, self.params)[0]

        beta = params['beta']
        gen_time = params['gen_time']

        assert len(lambda_vec)==len(c_vec)

        f_tmp[0] = (rho_t - beta)/gen_time * n_dens + lambda_vec @ c_vec + q_source_t

        #-----------------------------------
        # n species balances (implicit loop)
        #-----------------------------------

        species_rel_yield = params['species_rel_yield']
        beta_vec = np.array(species_rel_yield) * beta

        assert len(lambda_vec)==len(c_vec)
        assert len(beta_vec)==len(c_vec)
        #species are in RELATIVE yield, not actual; multiply by delayed neutron
        #yield fraction of 0.0065 to get the actual delayed neutron
        #concentration

        f_tmp[1:-2] = beta_vec / gen_time * n_dens - lambda_vec * c_vec


        #--------------------
        # fuel energy balance
        #--------------------
        rho_f    = params['fuel_dens']
        cp_f     = params['cp_fuel']
        vol_fuel = params['fuel_volume']

        pwr_dens  = self.__nuclear_pwr_dens_func( time, (temp_f+temp_c)/2, n_dens, self.params)

        heat_sink = self.__heat_sink_rate( time, temp_f, temp_c, self.params)

        #assert heat_sink <= 0.0,'heat_sink = %r'%heat_sink

        f_tmp[-2] =  -1/rho_f/cp_f * ( pwr_dens - heat_sink/vol_fuel )

        #-----------------------
        # coolant energy balance
        #-----------------------
        rho_c    = params['coolant_dens']
        cp_c     = params['cp_coolant']
        vol_cool = params['coolant_volume']

        # subcooled liquid
        pump_out = params['inflow-cool-temp']

        tau = params['tau_fake']

        heat_source = heat_sink
        temp_in = pump_out

        f_tmp[-1] = - 1/tau * (temp_c - temp_in) - 1./rho_c/cp_c/vol_cool * heat_source

        # pressure calculations

        #print(time)
        #print(u_vec)
        return f_tmp
