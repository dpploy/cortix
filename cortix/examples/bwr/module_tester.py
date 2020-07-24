#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org

import logging

import scipy.constants as unit

from cortix import Module
from cortix.support.phase_new import PhaseNew as Phase
from cortix import Quantity

class Tester(Module):
    """
    Passes a linearly-increasing stream of data to its ports in order to test how a module behaves.

    The actual series that is used must be specified for each run.
    """

    def __init__(self, params, outflow_zero, outflow_max):
        """Constructor.

        Parameters
        ----------
        params: dict
            All parameters for the module in the form of a dictionary.

        """

        super().__init__()

        self.port_names_expected = ['signal-out']

        self.params = params

        self.initial_time = params['start-time']
        self.end_time = params['end-time']
        self.time_step = 10.0

        self.show_time = (False, 10.0)

        self.log = logging.getLogger('cortix')
        self.__logit = False

        #Determine time-step increment
        delta = outflow_max[0] - outflow_zero[0]
        time_delta = self.end_time - self.initial_time
        d_dt = delta/time_delta
        self.change_per_timestep[0] = d_dt * self.time_step
        delta = outflow_max[1] - outflow_zero[1]
        d_dt = delta/time_delta
        self.change_per_timestep[1] = d_dt * self.time_step

        #outflow phase quantity history
        quantities = list()

        outflow1 = Quantity(name='Test Variable 1', formal_name='x1', unit='', value=outflow_zero[0], info='Simulation Independent Variable 1', latex_name=r'x_1')
        quantities.append(outflow1)

        outflow2 = Quantity(name='Test Variable 2', formal_name='x2', unit='', value=outflow_zero[1], info='Simulation Independent Variable 2', latex_name=r'x_2')

        quantities.append(outflow2)

        outflow_phase = Phase(self.inital_time, time_unit='s', quantities=quantities)
    def run(self, *args):

        # Some logic for logging time stamps
        if self.initial_time + self.time_step > self.end_time:
            self.end_time = self.initial_time + self.time_step

        time = self.initial_time

        while time <= self.end_time:
             
            if self.show_time[0] and print_time <= time < print_time+print_time_step:

                msg = self.name+'::run():time[m]='+ str(round(time/unit.minute, 1))
                self.log.info(msg)

                self.__logit = True
                print_time += self.show_time[1]

            else:
                self.__logit = False

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
        if self.get_port('signal-out').connected_port:

            message_time = self.recv('coolant-outflow')

            outflow  = self.outflow_phase.get_value('Test Variable 1', message_time) # for Reactor
            #outflow_2 = self.outflow_phase.get_value('Test Variable 1', message_time)
            #outflow_params = dict()
            #outflow_params['temp'] = outflow
            #outflow_params['quality'] = outflow_2
            self.send((message_time, outflow), 'signal-out')

    def __step(self, time):
        initial_x_1 = self.outflow_phase.get_value('Test Variable 1', time)
        initial_x_2 = self.outflow_phase.get_value('Test Variable 2', time)

        final_x_1 = inital_x_1 + self.change_per_timestep[0]
        final_x_2 = initial_x_2 + self.change_per_timestep[1]

        tmp = self.outflow_phase.get_row(time)
        time += self.time_step
        self.outflow_phase.add_row(time, tmp)
        self.outflow_phase.set_value('Test Variable 1', time)
        self.outflow_phase.set_value('Test Variable 2', time)
        return(time)

