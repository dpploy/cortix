#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org

import logging

import math
from scipy.integrate import odeint
import scipy.constants as unit
import numpy as np

import iapws.iapws97 as steam
import iapws.iapws95 as steam2

from cortix import Module
from cortix.support.phase_new import PhaseNew as Phase
from cortix import Quantity

class BWR(Module):
    """Boiling water reactor single-point reactor.

    Notes
    -----
    These are the `port` names available in this module to connect to respective
    modules: `turbine`, and `pump`.
    See instance attribute `port_names_expected`.

    """

    def __init__(self, params):
        """Constructor.

        Parameters
        ----------
        params: dict
            All parameters for the module in the form of a dictionary.

        """

        super().__init__()

        self.port_names_expected = ['coolant-inflow', 'coolant-outflow',
                                    'RCIS-inflow', 'RCIS-outflow']

        self.params = params

        self.initial_time = params['start-time']
        self.end_time = params['end-time']
        self.time_step = 10.0

        self.show_time = (False, 10.0)

        self.log = logging.getLogger('cortix')
        self.__logit = False

        #Data pertaining to one-group energy neutron balance
        self.gen_time = 1.0e-4  # s
        self.beta = 6.5e-3  # params['k_infty'] = 1.3447
        # geometric buckling; B = (pi/R)^2 + (2.405/H)^2
        self.buckling = (math.pi/237.5)**2.0 + (2.405/410)**2.0
        self.q_0 = 5000
        # fuel macroscopic absorption cross section, cm^-1
        self.fuel_macro_a = 1.34226126162
        # moderator microscopic absorption cross section, cm^2
        self.mod_micro_a = 0.332 * unit.zepto * unit.milli
        #number density of the fuel, atoms/cm^3
        self.n_fuel = 1.9577906e+21
        #resonance integral, I (dimensionless)
        self.I = 40.9870483 * unit.zepto * unit.milli
        # moderator microscopic scattering cross section, cm^2
        self.mod_micro_s = 20 * unit.zepto * unit.milli
        self.xi = 1 # average logarithmic energy decrement for light water
        # energy of a neutron produced by fissioning, in electron volts
        self.E0 = 2 * unit.mega
        self.mod_mu0 = 0.71 # migration and diffusion area constants
        self.eta = 1.03 # fast fission factor
        self.epsilon = 2.05 # neutron multiplecation factor
        self.mod_molar_mass = 18 # g/mol
        
        # Delayed neutron emission
        self.species_decay = [0.0124, 0.0305, 0.111, 0.301, 1.14, 3.01] # 1/sec
        self.species_rel_yield = [0.033, 0.219, 0.196, 0.395, 0.115, 0.042]

        # Data pertaining to two-temperature heat balances
        self.fis_energy = 180 * 1.602e-13 # J/fission
        self.enrich = 4.3/100.
        self.fuel_mat_mass_dens = 10.5 # g/cc
        #params['moderator_fuel_ratio'] = 387 # atomic number concentration ratio
        self.sigma_f_o = 586.2 * 100 * 1e-30 # m2
        self.temp_o = 20 + 273.15 # K
        self.thermal_neutron_velo = 2200 # m/s

        self.fis_nuclide_num_dens = 9.84e26 # (fissile nuclei)/m3

        self.q_c = 303 # volumetric flow rate

        self.fuel_dens = 10500 # kg/m3
        self.cp_fuel = 175 # J/(kg K)
        self.fuel_volume = 7.25  # m3

        self.steam_flowrate = 1820 # kg/s
        self.coolant_dens = 1000 #  kg/m3
        self.cp_coolant = 3500# J/(mol K) - > J/(kg K)
        self.coolant_volume = 7 #m3

        self.ht_coeff = 45000000

        # J/(fission sec) 1.26 t^-1.2 (t in seconds)
        self.fis_beta_energy = 1.26 * 1.602e-13
        # J/(fission sec) 1.40 t^-1.2 (t in seconds)
        self.fis_alpha_energy = 1.40 * 1.602e-13
        # % subcooling based on the % subcooling that exists at steady state
        self.subcooling_percent = 1 #(1 -(steam_table._Region4(7, 0)["h"]  - steam_table._Region1(493.15, 7)["h"])/(steam_table._Region4(7,0)["h"]))
        self.shutdown_temp_reached = False
        self.q_source_status = 'in' # is q_source inserted (in) or withdrawn (out)

        gen_time = self.gen_time # retrieve neutron generation time
        self.q_0 = 0.1

        self.n_ss = 0 # neutronless steady state before start up

        rho_0_over_beta = 0.25 # $
        beta = self.beta

        # control rod reactivity worth; enough to cancel out the negative
        self.alpha_n = 0

        self.reactivity = rho_0_over_beta * beta # "rho/beta = 10 cents"

        self.temp_o = self.temp_o

        self.tau = 1 # s
        self.malfunction_subcooling = 0.75
        self.alpha_n_malfunction = 0
        n_species = len(self.species_decay)

        assert len(self.species_rel_yield) == n_species

        # initialize concentration vector
        c_vec_0 = np.zeros(n_species, dtype=np.float64)
        # retrieve list of decay constants
        species_decay = self.species_decay
        lambda_vec = np.array(species_decay) # create a numpy vector
        beta = self.beta
        species_rel_yield = self.species_rel_yield
        # create the beta_i's vector
        beta_vec = np.array(species_rel_yield) * beta
        gen_time = self.gen_time # retrieve neutron generation time
        n_ss = self.n_ss
        # compute the steady state precursors number density
        c_vec_ss = beta_vec/lambda_vec/gen_time * n_ss
        self.c_vec_ss = c_vec_ss
        # setup initial condition for variables
        self.n_0 = n_ss
        self.c_vec_0 = c_vec_ss
        self.rho_0 = self.reactivity

        self.RCIS_operating_mode = 'offline'

        # Coolant outflow phase history
        quantities = list()

        flowrate = Quantity(name='flowrate', formal_name='q_c', unit='kg/s', value=0.0,
                            info='Reactor Outflow Coolant Flowrate', latex_name=r'$q_c$')

        quantities.append(flowrate)

        temp = Quantity(name='temp', formal_name='T_c', unit='K', value=params['coolant-temp'],
                        info='Reactor Outflow Coolant Temperature', latex_name=r'$T_c$')

        quantities.append(temp)

        press = Quantity(name='pressure', formal_name='P_c', unit='Pa', value=0.0,
                         info='Reactor Outflow Coolant Pressure', latex_name=r'$P_c$')

        quantities.append(press)

        quality = Quantity(name='steam-quality', formal_name='chi_s', unit='', value=0.0,
                           info='Reactor Steam Quality', latex_name=r'$\chi$')
        quantities.append(quality)

        self.coolant_outflow_phase = Phase(time_stamp=self.initial_time, time_unit='s', quantities=quantities)

        # Neutron phase history
        quantities = list()

        neutron_dens = Quantity(name='neutron-dens', formal_name='n', unit='1/m^3',
                                value=params['n-dens'], info='Rel. Reactor Neutron Density', latex_name=r'$n$')

        quantities.append(neutron_dens)

        delayed_neutron_cc = Quantity(name='delayed-neutrons-cc', formal_name='c_i',
                                      unit='1/m^3 ', value=params['delayed-neutron-cc'],
                                      info='Rel. Delayed Neutron Precursors', latex_name=r'$c_i$')
        quantities.append(delayed_neutron_cc)

        self.neutron_phase = Phase(time_stamp=self.initial_time, time_unit='s',
                                   quantities=quantities)

        # Reactor phase
        quantities = list()

        fuel_temp = Quantity(name='fuel-temp', formalName='T_f', unit='K',
                             value=params['fuel-temp'], info='Reactor Nuclear Fuel Temperature',
                             latex_name=r'$T_f$')

        quantities.append(fuel_temp)

        reg_rod_position = Quantity(name='reg-rod-position',
                                    formal_name='reg rod position', unit='m', value=0.0,
                                    info='Reactor Regulating Rod Position', latex_name=r'$x_p$')

        quantities.append(reg_rod_position)

        self.reactor_phase = Phase(time_stamp=self.initial_time, time_unit='s',
                                   quantities=quantities)

        # Initialize inflow
        self.params['inflow-cool-temp'] = params['condenser-runoff-temp']

        self.params['decay-heat-0'] = 0
        # Set up initial decay heat value
        if self.params['shutdown-mode']:
            temp = params['fuel-temp']
            n_dens = params['n-dens']
            decay_heat = self.__nuclear_pwr_dens_func(999, temp, n_dens, params)
            decay_heat *= 0.0622 # assume decay heat at 6.5% total power
            self.params['decay-heat-0'] = decay_heat

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

            #last_time_stamp = time - self.time_step

            #if self.show_time[0] and time >= print_time and \
            #        time<print_time+print_time_step:
            if self.show_time[0] and print_time <= time < print_time+print_time_step:

                msg = self.name+'::run():time[m]='+ str(round(time/unit.minute, 1))
                self.log.info(msg)

                self.__logit = True
                print_time += self.show_time[1]

            else:
                self.__logit = False

            #determine operating mode for this timestep
            #------------------------------------------

            current_temp = self.__get_coolant_outflow(time)['temp']
            if current_temp < 373.15:
                #if self.params['operating-mode'] == 'shutdown':
                    self.RCIS_operating_mode = 'online'

            if current_temp > 373.15:
                if self.params['operating-mode'] == 'startup':
                    #self.RCIS = False
                    self.RCIS_operating_mode = 'offline'

            # Communicate information
            #------------------------
            self.__call_ports(time)

            # Evolve one time step
            #---------------------

            time = self.__step(time)

    def __call_ports(self, time):

        # Interactions in the coolant-outflow port
        #-----------------------------------------
        # one way "to" coolant-outflow

        # send to
        if self.get_port('coolant-outflow').connected_port:
            message_time = self.recv('coolant-outflow')

            if self.RCIS_operating_mode == 'online':
                coolant_outflow = dict()
                coolant_outflow['temp'] = 287.15
                coolant_outflow['pressure'] = 0
                coolant_outflow['quality'] = 0
                coolant_outflow['flowrate'] = 0
                self.send((message_time, coolant_outflow), 'coolant-outflow')

            else:
                coolant_outflow = self.__get_coolant_outflow(message_time)
                #outflow_params = dict()
                self.send((message_time, coolant_outflow), 'coolant-outflow')

        # Interactions in the RCIS-outflow port
        #-----------------------------------------
        # one way "to" RCIS-outflow

        # send to
        if self.get_port('RCIS-outflow').connected_port:
            message_time = self.recv('RCIS-outflow')

            if self.RCIS_operating_mode == 'online':
                coolant_outflow = self.__get_coolant_outflow(message_time)
                coolant_outflow['flowrate'] = 5280 # kg/s
                coolant_outflow['status'] = self.RCIS_operating_mode
                self.send((message_time, coolant_outflow), 'RCIS-outflow')
            else:
                coolant_outflow = self.__get_coolant_outflow(message_time)
                coolant_outflow['flowrate'] = 0.0 # kg/s
                coolant_outflow['status'] = self.RCIS_operating_mode
                self.send((message_time, coolant_outflow), 'RCIS-outflow')

        # Interactions in the coolant-inflow port
        #----------------------------------------
        # one way "from" coolant-inflow

        # receive from
        if self.get_port('coolant-inflow').connected_port:
            self.send(time, 'coolant-inflow')

            if self.RCIS_operating_mode == 'online':
                (check_time, _) = self.recv('coolant-inflow')
                assert abs(check_time-time) <= 1e-6
            else:
                (check_time, inflow_cool_temp) = self.recv('coolant-inflow')
                assert abs(check_time-time) <= 1e-6
                self.params['inflow-cool-temp'] = inflow_cool_temp

        # Interactions in the RCIS-inflow port
        #----------------------------------------
        # one way "from" RCIS-inflow

        # receive from
        if self.get_port('RCIS-inflow').connected_port:
            self.send(time, 'RCIS-inflow')

            if self.RCIS_operating_mode == 'online':
                inflow_temp = self.recv('RCIS-inflow')
                self.params['inflow-cool-temp'] = inflow_temp
            else:
                _ = self.recv('RCIS-inflow')

    def __step(self, time=0.0):
        r"""ODE IVP problem.
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
        """
        #import iapws.iapws97 as steam

        # Get state values
        u_0 = self.__get_state_vector(time)

        t_interval_sec = np.linspace(time, time+self.time_step, num=2)

        (u_vec_hist, info_dict) = odeint(self.__f_vec,
                                         u_0, t_interval_sec,
                                         args=(self.params,),
                                         rtol=1e-4, atol=1e-8, mxstep=200,
                                         full_output=True)

        assert info_dict['message'] == 'Integration successful.', info_dict['message']

        u_vec = u_vec_hist[1, :]  # solution vector at final time step

        n_dens = u_vec[0]
        c_vec = u_vec[1:7]
        fuel_temp = u_vec[7]
        cool_temp = u_vec[8]

        #update state variables
        outflow = self.coolant_outflow_phase.get_row(time)
        neutrons = self.neutron_phase.get_row(time)
        reactor = self.reactor_phase.get_row(time)
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

    def __get_signal_out(self, time):
        """Determine whether the RCIS module should be on or off.

        Parameters
        ----------
        time: float
            Time in SI unit.

        Returns
        -------
        signal: string
            either 'online' or 'offline' to represent desired RCIS operation mode
        """
        if self.RCIS:
            signal = 'online'
            return(signal)
        else:
            signal = 'offline'
            return(signal)


    def __get_coolant_outflow(self, time):
        """Get the coolant outflow stream.

        Parameters
        ----------
        time: float
            Time in SI unit.

        Returns
        -------
        None

        """

        coolant_outflow_stream = dict()

        outflow_cool_temp = self.coolant_outflow_phase.get_value('temp', time)

        if outflow_cool_temp <= 373.15:
            coolant_outflow_stream['temp'] = outflow_cool_temp
            coolant_outflow_stream['pressure'] = 0
            coolant_outflow_stream['quality'] = 0
            coolant_outflow_stream['flowrate'] = 0

        else:

            if self.params['valve_opened']:
                pressure = steam._PSat_T(outflow_cool_temp)
                base_temp = 373.15
                base_pressure = steam._PSat_T(base_temp)
                base_params = steam.IAPWS97(T=base_temp, x=0)
                base_entropy = base_params.s
                base_cp = base_params.cp
                inlet_params = steam.IAPWS97(T=outflow_cool_temp, x=0)
                inlet_cp = inlet_params.cp
                average_cp = (base_cp + inlet_cp)/2

                delta_s = average_cp * math.log(outflow_cool_temp/base_temp) - (unit.R/1000) * math.log(pressure/base_pressure)

                inlet_entropy = (delta_s + base_entropy) * 1.25
                bubl_entropy = inlet_params.s
                bubl_enthalpy = inlet_params.h

                inlet_params = steam.IAPWS97(T=base_temp, x=1)
                dew_entropy = inlet_params.s
                dew_enthalpy = inlet_params.h
                quality = (inlet_entropy - bubl_entropy)/(dew_entropy - bubl_entropy)

                delta_t = time - self.params['valve_opening_time']
                mass_flowrate = 1820 * (1 - math.exp(-1 * delta_t/(3 * unit.minute)))

                coolant_outflow_stream['temp'] = outflow_cool_temp
                coolant_outflow_stream['pressure'] = pressure
                coolant_outflow_stream['quality'] = quality
                coolant_outflow_stream['flowrate'] = mass_flowrate

            else:
                self.params['valve_opened'] = True
                self.params['valve_opening_time'] = time
                coolant_outflow_stream['temp'] = 373.15
                coolant_outflow_stream['pressure'] = 0
                coolant_outflow_stream['quality'] = 0
                coolant_outflow_stream['flowrate'] = 0

        return coolant_outflow_stream

    def __get_state_vector(self, time):
        """Return a numpy array of all unknowns ordered as below:
            neutron density (1), delayed neutron emmiter concentrations (6),
            termperature of fuel (1), temperature of coolant (1).
        """

        u_vec = np.empty(0, dtype=np.float64)

        neutron_dens = self.neutron_phase.get_value('neutron-dens', time)
        u_vec = np.append(u_vec, neutron_dens)

        delayed_neutrons_cc = self.neutron_phase.get_value('delayed-neutrons-cc', time)
        u_vec = np.append(u_vec, delayed_neutrons_cc)

        fuel_temp = self.reactor_phase.get_value('fuel-temp', time)
        u_vec = np.append(u_vec, fuel_temp)

        temp = self.coolant_outflow_phase.get_value('temp', time)
        u_vec = np.append(u_vec, temp)

        return u_vec

    def __alpha_tn_func(self, temp, params):
        pressure = steam._PSat_T(temp) # vfda: why accessing protected method?

        d_rho = steam2.IAPWS95(P=pressure, T=temp-1).drhodT_P

        rho = 1 / steam._Region4(pressure, 0)['v'] # mass density, kg/m3

        n_m = ((rho * unit.kilo)/self.mod_molar_mass) * unit.N_A * (unit.centi)**3
        # number density of the moderator
        d_nm = ((d_rho * unit.kilo)/self.mod_molar_mass) * unit.N_A * (unit.centi)**3 #dNm/dTm
        d_nm = d_nm * unit.zepto * unit.milli

        mod_macro_a = self.mod_micro_a * n_m
        # macroscopic absorption cross section of the moderator
        mod_macro_s = self.mod_micro_s * n_m
        # macroscopic scattering cross section of the moderator

        F = self.fuel_macro_a/(self.fuel_macro_a + mod_macro_a) # thermal utilization, F
    #dF/dTm
        d_f = -1*(self.fuel_macro_a * self.mod_micro_a * d_nm)/(
            (self.fuel_macro_a + mod_macro_a)**2)

        # Resonance escape integral, P
        P = math.exp((-1 * self.n_fuel * (self.fuel_volume) * self.I)/
                     ((mod_macro_s * 3000)))
        #dP/dTm
        d_p = P * (-1 * self.n_fuel * self.fuel_volume * unit.centi**3 *
                   (self.mod_micro_s) * d_nm)/(mod_macro_s * 3000 * unit.centi**3)**2

        e_th = 0.0862 * temp # convert temperature to energy in MeV
        e_one = mod_macro_s/math.log(self.E0/e_th)
        # neutron thermalization macroscopic cross section

        d_f = 1/(3 * mod_macro_s * (1 - self.mod_mu0)) # neutron diffusion coefficient
        tau = d_f/e_one # fermi age, tau
        #dTau/dTm
        d_tau = (((0.0862 * (e_th/self.E0)) * 3 * n_m) - math.log(self.E0/e_th) *
                 ((self.mod_micro_s * d_nm))/((3 * n_m)**2 * (1 - self.mod_mu0)))

        L = math.sqrt(1/(3 * mod_macro_s * mod_macro_a * (1 - self.mod_mu0)))
        # diffusion length L
        # dL/dTm
        d_l = 1/(2 * math.sqrt((-2 * d_nm * unit.zepto * unit.milli)/(3 * self.mod_micro_s * (self.mod_micro_a * (n_m * unit.zepto * unit.milli)**3 * ((1 - self.mod_mu0))))))

        # left term of the numerator of the moderator temperature feedback coefficient, alpha
        left_first_term = d_tau * (self.buckling**2 + L**2 * self.buckling**4)
        #holding L as constant
        left_second_term = d_l * (2 * L * self.buckling**2 + 2 * L *
                                  (tau * self.buckling**4)) # holding tau as constant
        left_term = (P * F) * (left_first_term + left_second_term)
        # combining with P and F held as constant

        right_1st_term = (-1) * (1 + ((tau + d_l**2) * self.buckling**2) + \
                tau * d_l**2 * self.buckling**4) # num as const

        right_first_term = (-1) * ((1 + ((tau + L**2) * self.buckling**2))
                                   + tau * L**2 * self.buckling**4) # num as const
        right_second_term = F * d_p # holding thermal utilization as constant
        right_third_term = P * d_f # holding resonance escpae as constant
        right_term = right_first_term * (right_second_term + right_third_term)
        # combining all three terms together

        # numerator and denominator
        numerator = left_term + right_term
        denominator = self.eta * self.epsilon * \
                (F * P)**2

        alpha_tn = numerator/denominator


        alpha_tn = alpha_tn/3

        return alpha_tn

    def __rho_func(self, time, n_dens, temp, params):
        """Reactivity function.

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
        """

        rho_0 = self.rho_0
        temp_ref = self.temp_o
        #n_dens_ss_operation = params['n_dens_ss_operation']
        alpha_n = self.alpha_n

        if temp < 293.15:
            # if temperature is less than the starting temperature then moderator
            # feedback is zero
            alpha_tn = 0

        else:
            alpha_tn = self.__alpha_tn_func(temp, self.params) #alpha_tn_func(temp, params)

        if params['malfunction start'] < time < params['malfunction end']:
            # reg rod held in position; only mod temp reactivity varies with time
            # during malfunction
            alpha_n = self.alpha_n_malfunction
            rho_t = rho_0 + alpha_n + alpha_tn * (temp - temp_ref)

        elif time > params['shutdown time']:
            # effectively the inverse of startup; gradually reduce reactivity and neutron density.
            rho_0 = -0.5 * rho_0
            alpha_n = rho_0 - (alpha_tn * (temp - temp_ref))
            rho_t = rho_0

        elif n_dens < 1e-5:
            #controlled startup w/ blade; gradually increase neutron density to SS value.
            #rho_current = (1 - n_dens) * rho_0
            #alpha_n = rho_current - rho_0 - alpha_tn * (temp - temp_ref)
            #rho_t = rho_current
            #self.alpha_n_malfunction = alpha_n
            rho_t = rho_0

        else:
            rho_current = (1 - n_dens) * rho_0
            alpha_n = rho_current - rho_0 - alpha_tn * (temp - temp_ref)
            rho_t = rho_current
            self.alpha_n_malfunction = alpha_n

        return (rho_t, alpha_n, alpha_tn * (temp - temp_ref))

    def __q_source(self, time, params):
        """Neutron source delta function.

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
        """
        q_0 = self.q_0

        if time <= 30 and params['shutdown-mode'] == False: # small time value
            q_source = q_0
        else:
            q_source = 0.0
            self.q_source_status = 'out'

        return q_source

    def __sigma_fis_func(self, temp, params):
        """Place holder for implementation
        """
        sigma_f = self.sigma_f_o  * math.sqrt(298/temp) * math.sqrt(math.pi) * 0.5

        return sigma_f

    def __nuclear_pwr_dens_func(self, time, temp, n_dens, params):
        """Place holder for implementation.
        """
        # include the neutrons from the initial source

        rxn_heat = self.fis_energy # get fission reaction energy J per reaction

        sigma_f = self.__sigma_fis_func(temp, self.params) # m2

        fis_nuclide_num_dens = self.fis_nuclide_num_dens #  #/m3

        sigma_fis = sigma_f * fis_nuclide_num_dens # macroscopic cross section

        v_o = self.thermal_neutron_velo # m/s

        neutron_flux = n_dens * 0.9E15 * v_o * sigma_f/self.sigma_f_o*0.7

         #reaction rate density
        rxn_rate_dens = sigma_fis * neutron_flux

        # nuclear power source
        q3prime = - rxn_heat * rxn_rate_dens # exothermic reaction W/m3)

        # add decay heat
        if self.params['shutdown-mode']:
            t_0 = unit.hour * 24 # assume 24 hours of steady state operation before shutdown
            p_0 = self.params['decay-heat-0']
            p_t = p_0 * (((time + 1) ** -0.2) - (t_0 + time) ** -0.2)
            print(time, q3prime, p_t, q3prime+p_t, 'p_t')
            q3prime += p_t

        return q3prime

    def __heat_sink_rate(self, time, temp_f, temp_c, params):

        ht_coeff = self.ht_coeff

        q_f = - ht_coeff * (temp_f - temp_c)
        return q_f

    def __f_vec(self, u_vec, time, params):
        num_negatives = u_vec[u_vec < 0]

        if num_negatives.any() < 0:
            assert np.max(abs(u_vec[u_vec < 0])) <= 1e-8, 'u_vec = %r'%u_vec

        #assert np.all(u_vec >= 0.0), 'u_vec = %r'%u_vec
        q_source_t = self.__q_source(time, self.params)

        n_dens = u_vec[0] # get neutron dens

        c_vec = u_vec[1:-2] # get delayed neutron emitter concentration

        temp_f = u_vec[-2] # get temperature of fuel

        temp_c = u_vec[-1] # get temperature of coolant

        # initialize f_vec to zero
        species_decay = self.species_decay
        lambda_vec = np.array(species_decay)
        n_species = len(lambda_vec)

        f_tmp = np.zeros(1+n_species+2, dtype=np.float64) # vector for f_vec return
        #----------------
        # neutron balance
        #----------------
        rho_t = self.__rho_func(time, n_dens, temp_c, self.params)[0]

        beta = self.beta
        gen_time = self.gen_time

        assert len(lambda_vec) == len(c_vec)

        f_tmp[0] = (rho_t - beta)/gen_time * n_dens + lambda_vec @ c_vec + q_source_t

        #-----------------------------------
        # n species balances (implicit loop)
        #-----------------------------------

        species_rel_yield = self.species_rel_yield
        beta_vec = np.array(species_rel_yield) * beta

        assert len(lambda_vec) == len(c_vec)
        assert len(beta_vec) == len(c_vec)

        f_tmp[1:-2] = beta_vec / gen_time * n_dens - lambda_vec * c_vec

        #--------------------
        # fuel energy balance
        #--------------------
        rho_f = self.fuel_dens
        cp_f = self.cp_fuel
        vol_fuel = self.fuel_volume

        pwr_dens = self.__nuclear_pwr_dens_func(time, (temp_f+temp_c)/2,
                                                n_dens, self.params)

        heat_sink = self.__heat_sink_rate(time, temp_f, temp_c, self.params)

        #assert heat_sink <= 0.0,'heat_sink = %r'%heat_sink

        f_tmp[-2] = -1/rho_f/cp_f * (pwr_dens - heat_sink/vol_fuel)

        #-----------------------
        # coolant energy balance
        #-----------------------
        rho_c = self.coolant_dens
        cp_c = self.cp_coolant
        vol_cool = self.coolant_volume

        # subcooled liquid
        pump_out = params['inflow-cool-temp']

        tau = self.tau

        heat_source = heat_sink
        temp_in = pump_out

        f_tmp[-1] = - 1/tau * (temp_c - temp_in) - 1./rho_c/cp_c/vol_cool * heat_source

        f_tmp[:] = [0 if np.isnan(x) else x for x in f_tmp] #nifty conditional mutator

        return f_tmp
