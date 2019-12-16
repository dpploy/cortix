#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org

import logging

import numpy as np
import scipy.constants as const
from scipy.integrate import odeint
import scipy.constants as sc
import iapws.iapws97 as steam_table

from cortix import Module
from cortix.support.phase_new import PhaseNew as Phase
from cortix import Quantity

class Turbine(Module):
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
        self.params = params
        self.port_names_expected = ['steam-inflow','runoff']

        self.initial_time = 0.0 * const.day
        self.end_time     = 4 * const.hour
        self.time_step    = 10.0
        self.show_time    = (False,10.0)

        self.log = logging.getLogger('cortix')

        # Coolant outflow phase history
        quantities = list()

        temp = Quantity(name='reactor-runoff-temp', formal_name = 'T_in',
                unit = 'k', value = 273.15)

        quantities.append(temp)

        self.coolant_inflow_phase = Phase(self.initial_time, time_unit = 's', quantities = quantities)

        # Outflow phase history
        quantities = list()

        temp = Quantity(name='runoff-temp', formal_name='T_o',
                unit = 'k', value=273.15)

        quantities.append(temp)

        press = Quantity(name='runoff-press', formal_name='P_t',
                unit = 'Pa', value = params['runoff-pressure'])

        quantities.append(press)

        x = Quantity(name='runoff-quality', formal_name='chi_t',
                formalName = 'Turbine Runoff Quality', unit = '%', value = 0.0)

        quantities.append(x)

        self.turbine_runoff_phase = Phase(self.initial_time, time_unit = 's', quantities = quantities)

        # Turbine params history
        quantities = list()

        work = Quantity(name='turbine-power', formal_name='P_t',
                unit = 'w', value = 0.0)
        quantities.append(work)

        self.turbine_work_phase = Phase(self.initial_time, time_unit = 's', quantities = quantities)

        return

    def run(self, *args):

        time = self.initial_time
        while time < self.end_time + self.time_step:

            if self.show_time[0] and abs(time%self.show_time[1]-0.0)<=1.e-1:
                self.log.info('time = '+str(round(time/const.minute,1)))

            # Communicate information
            #------------------------
            self.__call_ports(time)

            # Evolve one time step
            #---------------------

            time = self.__step( time )

    def __call_ports(self, time):

        # Interactions in the steam-inflow port
        #-----------------------------------------
        # one way "to" steam-inflow

        # to 
        if self.get_port('runoff').connected_port:
            message_time = self.recv('runoff')
            #print('message time', message_time)
            outflow_state = dict()
            outflow_cool_temp = self.turbine_runoff_phase.get_value('runoff-temp', time)
            outflow_cool_quality = self.turbine_runoff_phase.get_value('runoff-quality', time)
            outflow_cool_press = self.turbine_runoff_phase.get_value('runoff-press', time)

            outflow_state['inflow-temp'] = outflow_cool_temp
            outflow_state['inflow-quality'] = outflow_cool_quality
            outflow_state['inflow-press'] = outflow_cool_press
            self.send( (message_time, outflow_state), 'runoff' )

        # Interactions in the coolant-inflow port
        #----------------------------------------
        # one way "from" coolant-inflow

        # from
        if self.get_port('steam-inflow').connected_port:
            self.send( time, 'steam-inflow' )
            (check_time, inflow_state) = self.recv('steam-inflow')
            assert abs(check_time-time) <= 1e-6
            self.temp = inflow_state['inflow-temp']
            self.x = inflow_state['inflow-quality']

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
        output = self.__turbine(time, self.temp, self.x, self.params)
        time = time + self.time_step
        t_runoff = output[0]
        x_runoff = output[2]
        if x_runoff < 0 and x_runoff != -1:
            x_runoff = 0
        w_turbine = output[1]

        if self.turbine_work_phase.has_time_stamp(time) == False:
            work = list()
            work.append(w_turbine)
            self.turbine_work_phase.add_row(time, work)
            runoff = self.turbine_runoff_phase.get_row(time - self.time_step)
            self.turbine_runoff_phase.add_row(time, runoff)

        self.turbine_work_phase.set_value('turbine-power', w_turbine, time)
        self.turbine_runoff_phase.set_value('runoff-quality', x_runoff, time)
        self.turbine_runoff_phase.set_value('runoff-temp', t_runoff, time)

        return(time)
        # Get state values

    def __turbine(self, time, temp_in, x,  params):
        #expand the entering steam from whatever temperature and pressure it enters at to 0.035 kpa, with 80% efficiency.
        #pressure of steam when it enters the turbine equals the current reactor operating pressure
        if self.params['high_pressure_turbine'] == True:
            p_in = steam_table._PSat_T(temp_in)
        else:
            p_in = self.params['turbine_inlet_pressure']

        p_out = self.params['turbine_outlet_pressure']
        if temp_in <= 273.15 or p_in <= p_out: # if temp is below this the turbine will not work
            t_runoff = temp_in
            w_real = 0
            x = 0
            return(t_runoff, w_real, x)
        if temp_in < 373.15:
            t_runoff = steam_table._TSat_P(p_out)
            w_real = 0
            x = -3
            return(t_runoff, w_real, x)

        #properties of the inlet steam

        inlet_parameters = steam_table._Region4(p_in, x)
        inlet_entropy = inlet_parameters['s']
        inlet_enthalpy = inlet_parameters['h']

        #bubble and dewpoint properties at turbine outlet
        bubl = steam_table._Region4(p_out, 0)
        dew = steam_table._Region4(p_out, 1)
        bubl_entropy = bubl['s']
        dew_entropy = dew['s']
        bubl_enthalpy = bubl['h']
        dew_enthalpy = dew['h']

        #if the ideal runoff is two-phase mixture:
        if inlet_entropy < dew_entropy and inlet_entropy > bubl_entropy:
            x_ideal = (inlet_entropy - bubl_entropy)/(dew_entropy - bubl_entropy)
            h_ideal = steam_table._Region4(p_out, x_ideal)['h']

        #if the ideal runoff is a superheated steam
        elif inlet_entropy > dew_entropy:
            t_ideal = steam_table._Backward2_T_Ps(p_out, inlet_entropy)
            h_ideal = steam_table._Region2(t_ideal, p_out)['h']

        #calculate the real runoff enthalpy
        w_ideal = inlet_enthalpy - h_ideal #on a per mass basis
        #assert(w_ideal > 0)
        w_real = w_ideal * params['turbine efficiency']
        h_real = inlet_enthalpy - w_ideal
        assert(h_real > 0)

        # if the real runoff is a superheated steam
        if h_real > dew_enthalpy:
            t_runoff = steam_table._Backward2_T_Ph(p_out, h_real)
            x_runoff = -1 # superheated steam

        #if the real runoff is a subcooled liquid
        elif h_real < bubl_enthalpy:
            t_runoff = steam_table._Backward1_T_Ph(p_out, h_real)
            x_runoff = 2 # subcooled liquid

        #if the real runoff is a two-phase mixture    
        else:
            x_runoff = (h_real - bubl_enthalpy)/(dew_enthalpy - bubl_enthalpy) # saturated vapor
            t_runoff = steam_table._TSat_P(p_out)

        w_real = w_real * params['steam flowrate'] * sc.kilo

        #w_real = heat_removed
        return (t_runoff, w_real, x_runoff)

