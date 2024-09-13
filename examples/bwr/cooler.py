#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org
'''
Heat exchanger used for reactor startup, shutdown and emergency operation.
'''

import logging

import scipy.constants as unit
import numpy as np

from cortix import Module

class Cooler(Module):
    """RCIS used in emergencies, cold startup and shutdown.
    Cools the reactor while the condenser is offline.
    """

    def __init__(self, params):
        """Constructor. No quantities needed at the moment.
        """

        super().__init__()

        self.port_names_expected = ['coolant-inflow', 'coolant-outflow', 'signal-in']
        
        self.status = 'online'
        self.params = params
        self.initial_time = params['start-time']
        self.end_time = params['end-time']
        self.time_step = 10.0

        self.show_time = (False, 10.0)

        self.log = logging.getLogger('cortix')
        self.__logit = False

        self.rcis_ua = 10000000 #w/m-k

    def run(self, *args):

        # Some logic for logging time stamps
        if self.initial_time + self.time_step > self.end_time:
            self.end_time = self.initial_time + self.time_step

        time = self.initial_time
        #unused print_time = self.initial_time
        print_time_step = self.show_time[1]
        if print_time_step < self.time_step:
            print_time_step = self.time_step

        while time <= self.end_time:

            #last_time_stamp = time - self.time_step

            #if self.show_time[0] and time >= print_time and \
            #        time<print_time+print_time_step:

            # Communicate information
            #------------------------
            self.__call_ports(time)

            # Evolve one time step
            #---------------------

            time = self.__step(time)

    def __call_ports(self, time):


        # Interactions in the coolant-inflow port
        #-----------------------------------------
        # one way "from" coolant-inflow

        if self.get_port('coolant-inflow').connected_port:
            self.send(time, 'coolant-inflow')
            (check_time, inflow_state) = self.recv('coolant-inflow')
            assert abs(check_time-time) <= 1e-6
            inflow_temp = inflow_state['temp']
            flowrate = inflow_state['flowrate'] # kg/s
            self.status = inflow_state['status']

        # Interactions in the coolant-outflow port
        #-----------------------------------------
        # one way "to" coolant-outflow

        if self.get_port('coolant-outflow').connected_port:
            
            message_time = self.recv('coolant-outflow')
            if self.status == 'online':
                outflow_temp = self.__get_coolant_outflow(message_time,
                                                          inflow_temp,
                                                          flowrate, self.params)
            else:
                outflow_temp = 0
            self.send(outflow_temp, 'coolant-outflow')

    def __step(self, time=0.0):
        time += self.time_step
        return time

    def __get_coolant_outflow(self, time, temp_in, flowrate, params):
        """Calculate the temperature of the coolant leaving the RCIS system.

        Parameters
        ----------
        time: float
            Time in SI unit.
        temp_in: float
            The temperature of the coolant entering the RCIS system (also the current reactor
            temperature, in Kelvin).
        flowrate: float
            The current recirculation mass flowrate in kg/s.

        Returns
        -------
        temp_out: float
            The temperature of the cooled recirculation being fed back to the
            top of the reactor, in Kelvin.

        """
        heat_transfer_coef = self.rcis_ua
        cp_rho = 4.184 * unit.kilo * flowrate # Kj/Kg-k
        tc = 287.15 # assumed constant for simplicity

        #initial guess: outflow temp = 300k
        temp_out_2 = temp_in - 5
        temp_out_1 = 999

        while abs(temp_out_2 - temp_out_1) > 0.1:
            temp_out_1 = temp_out_2
            delta_t1 = temp_in - tc
            delta_t2 = temp_out_1 - tc
            lmtd = (delta_t1 - delta_t2)/np.log(delta_t1/delta_t2)
            quantity = heat_transfer_coef * lmtd / cp_rho
            print(lmtd)
            print(time, heat_transfer_coef * lmtd, 'cooler')
            temp_out_2 = temp_in - quantity
            if temp_out_2 < tc:
                temp_out_2 = tc
                break

        return temp_out_2
