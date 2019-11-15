#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org

import logging

import numpy as np
import scipy.constants as const
import scipy.constants as sc
import iapws.iapws97 as steam_table

from scipy.integrate import odeint

from cortix import Module
from cortix.support.phase_new import PhaseNew as Phase
from cortix import Quantity

class Condenser(Module):
    '''
    Boiling water reactor single-point reactor.

    Notes
    -----
    These are the `port` names available in this module to connect to respective
    modules: `turbine`, and `pump`.
    See instance attribute `port_names_expected`.

    '''

    def __init__(self, ode_params):
        '''
        Parameters
        ----------
        params: dict
            All parameters for the module in the form of a dictionary.

        '''

        super().__init__()

        self.port_names_expected = ['inflow', 'outflow']

        quantities      = list()
        self.ode_params = dict()

        self.initial_time = 0.0 * const.day
        self.end_time     = 4 * const.hour
        self.time_step    = 10 * const.second
        self.show_time    = (False,10*const.second)

        self.log = logging.getLogger('cortix')
        self.params = self.ode_params

        # Runoff in phase history

        quantities = list()

        flowrate = Quantity(name='inflow-flowrate',
                   formalName='Turbine Runoff Flowrate',
                   unit='kg/s', value=0.0)
        quantities.append(flowrate)

        temp = Quantity(name='inflow-temp', formalName='Turbine Runoff Temp.',
               unit='K', value=0.0)
        quantities.append(temp)

        press = Quantity(name='inflow-pressure',formalName='Turbine Runoff Pressure',
                unit='Pa', value=0.0)
        quantities.append(press)

        quality = Quantity(name='inflow-quality', formalName='Turbine Runoff Quality', unit='%', value=0.0)

        self.turbine_runoff__phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        # Condenser runoff phase history
        quantities = list()

        flowrate = Quantity(name='condenser-runoff-flowrate',
                   formalName='Condenser Runoff Flowrate',
                   unit='kg/s', value=0.0)
        quantities.append(flowrate)

        temp = Quantity(name='condenser-runoff-temp',
                   formalName='Condenser Runoff Temp.',
                   unit='K', value=0.0)
        quantities.append(temp)

        self.condenser_runoff_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        # Neutron phase history

        # Initialize inflows to zero
        #self.ode_params['prison-inflow-rates']       = np.zeros(self.n_groups)
        #self.ode_params['parole-inflow-rates']       = np.zeros(self.n_groups)
        #self.ode_params['arrested-inflow-rates']     = np.zeros(self.n_groups)
        #self.ode_params['jail-inflow-rates']         = np.zeros(self.n_groups)
        #self.ode_params['adjudication-inflow-rates'] = np.zeros(self.n_groups)
        #self.ode_params['probation-inflow-rates']    = np.zeros(self.n_groups)

        return

    def run(self, *args):

       # self.__zero_ode_parameters()

        time = self.initial_time

        while time < self.end_time:

            if self.show_time[0] and abs(time%self.show_time[1]-0.0)<=1.e-1:
                self.log.info('time = '+str(round(time/const.minute,1)))

            # Communicate information
            #------------------------

            self.__call_input_ports(time)

            # Evolve one time step
            #---------------------

            time = self.__step( time )

            self.__call_output_ports(time)

    def __call_input_ports(self, time):

        # Interactions in the outflow port
        #----------------------------------------
        # one way "from" outflow

        # from
        self.send( time, 'inflow' )
        (check_time, inflow_state) = self.recv('inflow')
        assert abs(check_time-time) <= 1e-6

        inflow = self.turbine_runoff_phase.GetRow(time)
        self.turbine_runoff_phase.AddRow(time, inflow)
        self.turbine_runoff_phase.SetValue('inflow-temp', inflow_state['inflow-temp'], time)
        self.turbine_runoff_phase.SetValue('inflow-quality', inflow_state['inflow-quality'], time)

    def __call_output_ports(self, time):
        # Interactions in the coolant-outflow port
        #-----------------------------------------
        # one way "to" coolant-outflow

        # to be, or not to be?
        message_time = self.recv('condenser-runoff')
        outflow_state = dict()
        outflow_cool_temp = self.condenser_runoff_phase.GetValue('condenser-runoff-temp', time)

        condenser_runoff['outflow-temp'] = outflow_cool_temp
        self.send( (message_time, condenser_runoff), 'outflow' )

    def __step(self, time=0.0):

        import iapws.iapws97 as steam
        temp_in = self.turbine_runoff_phase.GetValue('inflow-temp', time)
        x_in = self.turbine_runoff_phase.GetValue('inflow-temp', time)
        temp_c = 0
        t_out = self.__condenser(time, temp_in, x_in, temp_c, self.params)

        condenser_runoff = self.condenser_runoff_phase.GetRow(time)

        time += self.time_step
        self.condenser_runoff_phase.AddRow(time, condenser_runoff)
        self.condenser_runoff_phase.Setvalue('condenser-runoff-temp', t_out)

    def __condenser(time, temp_in, x_in, temp_c, params):
        critical_temp = steam_table._TSat_P(0.005)
        condenser_runoff = critical_temp
        if x == -1 and temp_in > critical_temp: #superheated vapor inlet; deprecated
            pressure = 0.005
            h_steam = steam_table._Region2(temp_in, pressure)['h']
            h_sat = steam_table._Region4(0.005, 1)['h']
            q = params['steam flowrate'] * (h_steam - h_sat) * sc.kilo

            #log mean temperature difference
            delta_Ta = temp_in - critical_temp
            delta_Tb = 20-10
            LMTD = (delta_Ta - delta_Tb) / (math.log(delta_Ta) - math.log(delta_Tb))

            low = steam_table.IAPWS97(T=critical_temp+1, P=pressure)
            high = steam_table.IAPWS97(T=temp_in, P=pressure)

            low_conductivity = low.k
            low_rho = low.rho
            low_prandlt = low.Prandt
            low_viscosity = low.mu
            low_reynolds = (low_rho * 0.1 * 40)/low_viscosity
            low_nusselt = (0.3 + 0.629 * (low_reynolds ** 0.5) * low_prandlt**(1/3))
            low_nusselt = low_nusselt/(1+(0.4/low_prandlt)**(2/3))**(1/4)
            low_nusselt = low_nusselt * (1 + (low_reynolds / 282000)**(5/6))**(4/4.5)       #nusselt number at the crtical temperature according to the churchill-bernsetin correlation
            low_heat_transfer_coeff = low_nusselt * (low.k/0.1)

            high_rho = high.rho
            high_prandlt = high.Prandt
            high_viscocity = high.mu
            high_conductivity = high.k
            high_viscosity = high.mu
            high_reynolds = (high_rho * 0.1 * 40)/high_viscosity
            high_nusselt = (0.3 + 0.629 * (high_reynolds ** 0.5) * high_prandlt**(1/3))
            high_nusselt = high_nusselt/(1+(0.4/high_prandlt)**(2/3))**(1/4)
            high_nusselt = high_nusselt * (1 + (high_reynolds / 282000)**(5/6))**(4/4.5)
            high_heat_transfer_coeff = high_nusselt * (high_conductivity/0.1)

            average_ht_transfer_coeff = (high_heat_transfer_coeff + low_heat_transfer_coeff)/2

        if x > 0:
            pressure = 0.005
            h_mixture = steam_table._Region4(pressure, x)['h']
            h_dewpt = steam_table._Region4(pressure, 0)['h']
            q = (h_mixture - h_dewpt) * sc.kilo * params['steam flowrate']

            critical_temp = steam_table._TSat_P(pressure)
            sat_liquid = steam_table.IAPWS97(T=critical_temp - 1, P=pressure)
            h_dew = steam_table._Region4(0.005, 1)['h']
            h_bubl = steam_table._Region4(0.005, 0)['h']
            water_cp = steam_table.IAPWS97(T=287.15, P=0.1013).cp
            delta_Tb = q/(params['cooling water flowrate'] * water_cp * sc.kilo)
            t_c_in = 14 + 273.15
            t_c_out = 14 + 273.15 + delta_Tb

            LMTD = (t_c_out - t_c_in)/(math.log(critical_temp - t_c_in))/(critical_temp - t_c_out)

            pipe_diameter = params['pipe_diameter']
            liquid_velocity = params['liquid_velocity']

            #calculate the convective heat transfer coefficient on a liquid basis from the Churchill-Bernstein correlation
            liquid_conductivity = sat_liquid.k
            liquid_rho = sat_liquid.rho
            liquid_prandlt = sat_liquid.Prandt
            liquid_viscosity = sat_liquid.mu
            liquid_reynolds = (liquid_rho * pipe_diameter * liquid_velocity)/liquid_viscosity

            liquid_nusselt = (0.3 + 0.629 * (liquid_reynolds ** 0.5) * liquid_prandlt**(1/3))
            liquid_nusselt = liquid_nusselt/(1+(0.4/liquid_prandlt)**(2/3))**(1/4)
            liquid_nusselt = liquid_nusselt * (1 + (liquid_reynolds / 282000)**(5/6))**(4/4.5) #nusselt number at the crtical temperature according to the churchill-bernsetin correlation
            liquid_heat_transfer_coeff = liquid_nusselt * (liquid_conductivity/pipe_diameter) #overall convective heat transfer coefficient

            #determine the Martinelli paremeter
            steam = steam_table.IAPWS97(T=critical_temp+1, P=pressure)
            steam_rho = steam.rho
            steam_viscosity = steam.mu
            xtt = ((1 -x)/x)**1.8 * (steam_rho/liquid_rho) * (liquid_viscosity/steam_viscosity)**0.5
            xtt = math.sqrt(xtt)

            #determine the overall heat transfer coefficient from the McNaught expression
            alpha_sh = liquid_heat_transfer_coeff * (1/xtt)**0.78

            #determine how far the two-phase mixture gets in the condenser before being fully condensed
            condensation_area = (q/(alpha_sh * LMTD))
            remaining_area = params['heat transfer area'] - condensation_area

            condenser_runoff = critical_temp

            if time > params['malfunction start'] and time < params['malfunction end']:
                condenser_runoff = critical_temp

            elif remaining_area > 0:
            #subcool the remaining liquid

            #iterative method
            #0. guess an ending value for the coolant and 
            #1. calculate high nusselt number
            #2. guess a value for low temperature
            #3. calculate low nusselt number
            #4. calculate LMTD and average heat transfer coefficient
            #5. calculate q
            #6. use q to calculate a new ending temperature for the water and the vapor
            #7. rinse and repeat

                final_coolant_temperature_guess = steam_table._TSat_P(0.005) - 10 # initial guess
                final_runoff_temperature_guess = 300 # initial guess
                final_runoff_temperature = 0 #iteration variable

                while abs((final_runoff_temperature_guess - final_runoff_temperature))> 1: #loop until convergeance, +- 1 degree kelvin
                    runoff_in = steam_table._TSat_P(0.005)
                    coolant_in = 14 + 273.15 #k
                    #assert(final_coolant_temperature_guess < final_runoff_temperature_guess)
                    #assert(final_coolant_temperature_guess > coolant_in)

                    final_runoff_temperature = final_runoff_temperature_guess

                    #guess the LMTD

                    LMTD = ((runoff_in - final_coolant_temperature_guess) - (final_runoff_temperature - coolant_in))\
                /math.log((runoff_in -  final_coolant_temperature_guess)/(final_runoff_temperature - coolant_in))

                    #average wall temperatures
                    upper_wall_temp = (coolant_in + runoff_in)/2
                    lower_wall_temp = (final_runoff_temperature + final_coolant_temperature_guess)/2

                    #high temperature heat transfer coefficient calculation
                    high_properties = steam_table.IAPWS97(T=upper_wall_temp, P=pressure)
                    high_conductivity = high_properties.k
                    high_rho = high_properties.rho
                    high_prandlt = high_properties.Prandt
                    high_viscosity = high_properties.mu
                    high_reynolds = (high_rho * pipe_diameter * liquid_velocity)/high_viscosity

                    high_nusselt = (0.3 + 0.629 * (high_reynolds ** 0.5) * high_prandlt**(1/3))
                    high_nusselt = high_nusselt/(1+(0.4/high_prandlt)**(2/3))**(1/4)
                    high_nusselt = high_nusselt * (1 + (high_reynolds / 282000)**(5/6))**(4/4.5)
                    high_heat_transfer_coeff = high_nusselt * (high_conductivity/pipe_diameter) #overall convective heat transfer coefficient

                #   low temperature heat transfer coefficient calculation
                    low_properties = steam_table.IAPWS97(T=lower_wall_temp, P=pressure)
                    low_conductivity = low_properties.k
                    low_rho = low_properties.rho
                    low_prandlt = low_properties.Prandt
                    low_viscosity = low_properties.mu
                    low_reynolds = (low_rho * pipe_diameter * liquid_velocity)/low_viscosity

                    low_nusselt = (0.3 + 0.629 * (low_reynolds ** 0.5) * low_prandlt**(1/3))
                    low_nusselt = low_nusselt/(1+(0.4/low_prandlt)**(2/3))**(1/4)
                    low_nusselt = low_nusselt * (1 + (low_reynolds / 282000)**(5/6))**(4/4.5)
                    low_heat_transfer_coeff = low_nusselt * (low_conductivity/pipe_diameter) #overall convective heat transfer coefficient

                    #average heat transfer coefficient
                    average_heat_transfer_coeff = (high_heat_transfer_coeff + low_heat_transfer_coeff)/2

                    #calculate q = UAdeltaTlm
                    q_1 = average_heat_transfer_coeff * remaining_area * LMTD/10

                    #calculate actual coolant and liquid water temperatures

                    coolant_cp = steam_table.IAPWS97(T=coolant_in, P=0.005).cp
                    iterated_coolant_final_temp = (q_1/(coolant_cp * params['cooling water flowrate'] * sc.kilo)) + coolant_in

                    steam_cp = steam_table.IAPWS97(T=runoff_in, P=0.005).cp
                    iterated_steam_final_temp = runoff_in - (q_1/(steam_cp * params['steam flowrate'] * sc.kilo))

                    if(iterated_steam_final_temp < coolant_in or iterated_coolant_final_temp > runoff_in or iterated_steam_final_temp < iterated_coolant_final_temp):
                        final_runoff_temperature_guess = coolant_in
                        final_coolant_runoff_guess = runoff_in
                        break

                    final_runoff_temperature_guess = iterated_steam_final_temp
                    final_coolant_temperature_guess = iterated_coolant_final_temp

                condenser_runoff = final_runoff_temperature_guess

        return(condenser_runoff)
