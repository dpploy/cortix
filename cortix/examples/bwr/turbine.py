#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org
"""
Cortix Example Module
"""

import logging
from copy import deepcopy

import scipy.constants as unit
import numpy as math

import iapws.iapws97 as steam_table

from cortix import Module
from cortix.support.phase_new import PhaseNew as Phase
from cortix import Quantity

class Turbine(Module):
    """Boiling water single-point reactor.

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

        self.params = deepcopy(params)
        self.params['entropy'] = 4.5 # Kj/Kg-K

        self.port_names_expected = ['inflow', 'outflow-1', 'outflow-2']

        self.initial_time = params['start-time']
        self.end_time = params['end-time']

        self.time_step = 10.0
        self.show_time = (False, 10.0)

        self.log = logging.getLogger('cortix')
        self.efficiency = 0.8

        # Inflow phase history
        quantities = list()

        temp = Quantity(name='temp', formal_name='T_in', unit='K', value=params['coolant-temp'],
                        info='Turbine Steam Inflow Temperature', latex_name=r'$T_i$')

        quantities.append(temp)

        self.inflow_phase = Phase(time_stamp=self.initial_time, time_unit='s',
                                  quantities=quantities)

        # Outflow phase history
        quantities = list()

        temp = Quantity(name='temp', formal_name='T_o', unit='K', value=params['turbine-outflow-temp'],
                        info='Turbine Steam Outflow Temperature', latex_name=r'$T_o$')

        quantities.append(temp)

        press = Quantity(name='pressure', formal_name='P_t', unit='Pa',
                         value=params['runoff-pressure'],
                         info='Turbine Steam Outflow Pressure', latex_name=r'$P_t$')

        quantities.append(press)

        x = Quantity(name='quality', formal_name='chi_t', unit='%', value=params['turbine-chi'],
                     info='Turbine Steam Outflow Quality', latex_name=r'$\chi_t$')

        quantities.append(x)

        work = Quantity(name='power', formal_name='P_t', unit='W', value=params['turbine-work'],
                        info='Turbine Power', latex_name=r'$W_t$')

        quantities.append(work)

        flowrate = Quantity(name='flowrate', formal_name='m', unit='kg/s', value=params['initial-flowrate'], info='Mass Flowrate', latex_name=r'$/dot m$')

        quantities.append(flowrate)

        self.outflow_phase = Phase(time_stamp=self.initial_time, time_unit='s',
                                   quantities=quantities)

    def run(self, *args):

        time = self.initial_time

        while time < self.end_time + self.time_step:

            if self.show_time[0] and abs(time%self.show_time[1]-0.0) <= 1.e-1:
                msg = 'time = '+str(round(time/unit.minute, 1))
                self.log.info(msg)

            # Communicate information
            #------------------------
            self.__call_ports(time)

            # Evolve one time step
            #---------------------

            time = self.__step(time)

    def module_tester(self):
        return

    def __call_ports(self, time):

        # Interactions in the steam-outflow-1 port
        #-----------------------------------------
        # one way "to" outflow-1

        # to
        if self.get_port('outflow-1').connected_port:
            message_time = self.recv('outflow-1')

            outflow_state = dict()

            steam_temp = self.outflow_phase.get_value('temp', time)
            steam_quality = self.outflow_phase.get_value('quality', time)
            steam_press = self.params['turbine_inlet_pressure']
            steam_flowrate = self.outflow_phase.get_value('flowrate', time)


            outflow_state['temp'] = steam_temp
            outflow_state['quality'] = steam_quality
            outflow_state['pressure'] = steam_press
            outflow_state['flowrate'] = steam_flowrate

            if self.params['high_pressure_turbine'] == False:
                outflow_state['flowrate'] *= 2

            else:
                outflow_state['flowrate'] *= 0.5

            self.send((message_time, outflow_state), 'outflow-1')

        # Interactions in the steam-outflow-2 port
        #-----------------------------------------
        # one way "to" outflow-2

        # to
        if self.get_port('outflow-2').connected_port:

            message_time = self.recv('outflow-2')

            outflow_state = dict()

            steam_temp = self.outflow_phase.get_value('temp', time)
            steam_quality = self.outflow_phase.get_value('quality', time)
            steam_press = self.params['turbine_outlet_pressure']
            steam_flowrate = self.outflow_phase.get_value('flowrate', time)

            outflow_state['temp'] = steam_temp
            outflow_state['quality'] = steam_quality
            outflow_state['pressure'] = steam_press
            outflow_state['flowrate'] = steam_flowrate

            if self.params['high_pressure_turbine'] == False:
                outflow_state['flowrate'] *= 2

            else:
                outflow_state['flowrate'] *= 0.5

            self.send((message_time, outflow_state), 'outflow-2')

        # Interactions in the steam-inflow port
        #----------------------------------------
        # one way "from" inflow

        # from
        if self.get_port('inflow').connected_port:

            self.send(time, 'inflow')

            (check_time, inflow_state) = self.recv('inflow')
            assert abs(check_time-time) <= 1e-6

            self.temp = inflow_state['temp']
            self.chi = inflow_state['quality']
            self.pressure = inflow_state['pressure']
            self.flowrate = inflow_state['flowrate']

            if self.params['high_pressure_turbine'] == False:
                self.flowrate = self.flowrate * 0.5

    def __step(self, time=0.0):
        r"""
        Advance the state of the turbine.

        Parameters
        ----------
        time: float
            Time in SI unit.

        Returns
        -------
        None
        """
        output = self.__turbine(time, self.temp, self.chi, self.pressure, self.flowrate, self.params)

        tmp = self.outflow_phase.get_row(time)

        time += self.time_step

        self.outflow_phase.add_row(time, tmp)

        t_runoff = output[0]

        x_runoff = output[2]

        m_runoff = output[3]

        #if x_runoff < 0 and x_runoff != -1:
            #x_runoff = 0

        w_turbine = output[1]

        self.outflow_phase.set_value('power', w_turbine, time)
        self.outflow_phase.set_value('quality', x_runoff, time)
        self.outflow_phase.set_value('temp', t_runoff, time)
        self.outflow_phase.set_value('flowrate', m_runoff, time)

        return time

    def __turbine(self, time, temp_in, chi_in, p_in, flowrate, params):
        # Expand the entering steam from whatever temperature and pressure it enters
        # at to 0.035 kpa, with 80% efficiency.

        if flowrate == 0:
            return(293.15, 0, 0, 0)

        if temp_in < steam_table._TSat_P(0.5) and self.params['high_pressure_turbine'] == False:
            t_runoff = steam_table._TSat_P(0.5)
            w_real = 0
            runoff_quality = 0
            return(t_runoff, w_real, runoff_quality)

        # vfda: access of a protected member?
        inlet_parameters = steam_table._Region4(p_in, chi_in)
        inlet_entropy = inlet_parameters['s']
        inlet_enthalpy = inlet_parameters['h']

        p_out = self.params['turbine_outlet_pressure']

        #bubble and dewpoint properties at turbine outlet
        # vfda: access of a protected member?
        bubl = steam_table._Region4(p_out, 0)
        # vfda: access of a protected member?
        dew = steam_table._Region4(p_out, 1)
        bubl_entropy = bubl['s']
        dew_entropy = dew['s']
        bubl_enthalpy = bubl['h']
        dew_enthalpy = dew['h']
        #print(bubl_entropy, inlet_entropy, dew_entropy, self.params['high_pressure_turbine'])

        #if the ideal runoff is two-phase mixture:
        #if inlet_entropy < dew_entropy and inlet_entropy > bubl_entropy:
        if  bubl_entropy < inlet_entropy < dew_entropy:
            x_ideal = (inlet_entropy - bubl_entropy)/(dew_entropy - bubl_entropy)
            # vfda: access of a protected member?
            h_ideal = steam_table._Region4(p_out, x_ideal)['h']

        #if the ideal runoff is a superheated steam
        #elif inlet_entropy > dew_entropy:
            # vfda: access of a protected member?
            #t_ideal = steam_table._Backward2_T_Ps(p_out, inlet_entropy)
            # vfda: access of a protected member?
            #h_ideal = steam_table._Region2(t_ideal, p_out)['h']

        #calculate the real runoff enthalpy
        w_ideal = inlet_enthalpy - h_ideal #on a per mass basis
        #assert(w_ideal > 0)
        w_real = w_ideal * self.efficiency
        h_real = inlet_enthalpy - w_ideal
        assert h_real > 0
        if w_real < 0:
            w_real = 0

        # if the real runoff is a superheated steam
        if h_real > dew_enthalpy:
            # vfda: access of a protected member?
            t_runoff = steam_table._Backward2_T_Ph(p_out, h_real)
            x_runoff = -1 # superheated steam

        #if the real runoff is a subcooled liquid
        elif h_real < bubl_enthalpy:
            # vfda: access of a protected member?
            t_runoff = steam_table._Backward1_T_Ph(p_out, h_real)
            x_runoff = 2 # subcooled liquid

        #if the real runoff is a two-phase mixture
        else:
            # saturated vapor
            x_runoff = (h_real - bubl_enthalpy)/(dew_enthalpy - bubl_enthalpy)
            # vfda: access of a protected member?
            t_runoff = steam_table._TSat_P(p_out)
        w_real = w_real * flowrate * unit.kilo

        return (t_runoff, w_real, x_runoff, flowrate)
