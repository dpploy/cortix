#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
"""
Cortix Run File
"""
import scipy.constants as unit
import matplotlib.pyplot as plt

from cortix import Cortix
from cortix import Network

from reactor import BWR
from turbine import Turbine
from condenser import Condenser
from params import get_params

def main():
    """Balance of plant of a boiling water nuclear reactor.

    Attributes
    ----------
    end_time: float
        End of the flow time in SI unit.
    time_step: float
        Size of the time step between port communications in SI unit.
    use_mpi: bool
        If set to `True` use MPI otherwise use Python multiprocessing.

    """

    # Preamble

    end_time = 30 * unit.minute
    time_step = 30.0 # seconds
    show_time = (True, 5*unit.minute)

    use_mpi = False  # True for MPI; False for Python multiprocessing
    plot_results = True # True for enabling plotting section below
    params = get_params() # parameters for BoP BWR

    #*****************************************************************************
    # Define Cortix system

    # System top level
    plant = Cortix(use_mpi=use_mpi, splash=True)

    # Network
    plant_net = plant.network = Network()

    params['start-time'] = 0
    params['end-time'] = end_time

    #*****************************************************************************
    # Create reactor module
    reactor = BWR(params)

    reactor.name = 'BWR'
    reactor.save = True
    reactor.time_step = time_step
    reactor.end_time = end_time
    reactor.show_time = show_time

    # Add reactor module to network
    plant_net.module(reactor)

    #*****************************************************************************
    # Create turbine 1 module
    params['turbine_inlet_pressure'] = 2
    params['turbine_outlet_pressure'] = 0.005
    params['high_pressure_turbine'] = True

    #params_turbine = reactor.params
    #params_turbine.inlet_pressure = 2
    #params.turbine_outlet_pressure = 0.5

    turbine1 = Turbine(params)

    turbine1.name = 'High Pressure Turbine'
    turbine1.save = True
    turbine1.time_step = time_step
    turbine1.end_time = end_time

    # Add turbine 1 module to network
    plant_net.module(turbine1)

    #*****************************************************************************
    # Create condenser module
    params['steam flowrate'] = params['steam flowrate'] * 2

    condenser = Condenser(params)

    condenser.name = 'Condenser'
    condenser.save = True
    condenser.time_step = time_step
    condenser.end_time = end_time

    plant_net.module(condenser)

    #*****************************************************************************
    # Create the BoP network connectivity
    plant_net.connect([reactor, 'coolant-outflow'], [turbine1, 'inflow'])
    plant_net.connect([turbine1, 'outflow-1'], [condenser, 'inflow-1'])
    plant_net.connect([condenser, 'outflow'], [reactor, 'coolant-inflow'])

    plant_net.draw()

    #*****************************************************************************
    # Run network dynamics simulation
    plant.run()

    #*****************************************************************************
    # Plot results

    if plot_results and (plant.use_multiprocessing or plant.rank == 0):

        # Reactor plots
        reactor = plant_net.modules[0]

        (quant, time_unit) = reactor.neutron_phase.get_quantity_history('neutron-dens')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.latex_name+' ['+quant.unit+']')

        plt.grid()
        plt.savefig('test-neutron-dens.png', dpi=300)

        (quant, time_unit) = reactor.neutron_phase.get_quantity_history('delayed-neutrons-cc')
        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.latex_name+' ['+quant.unit+']')

        plt.grid()
        plt.savefig('test-delayed-neutrons-cc.png', dpi=300)

        (quant, time_unit) = reactor.coolant_outflow_phase.get_quantity_history('temp')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.latex_name+' ['+quant.unit+']')

        plt.grid()
        plt.savefig('test-coolant-outflow-temp.png', dpi=300)

        (quant, time_unit) = reactor.reactor_phase.get_quantity_history('fuel-temp')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.latex_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('test-fuel-temp.png', dpi=300)

        # Turbine1 plots
        turbine1 = plant_net.modules[1]

        (quant, time_unit) = turbine1.outflow_phase.get_quantity_history('power')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.latex_name+' ['+quant.unit+']',
                   title='High Pressure Turbine Power')
        plt.grid()
        plt.savefig('test-turbine1-power.png', dpi=300)

        (quant, time_unit) = turbine1.outflow_phase.get_quantity_history('temp')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.latex_name+' ['+quant.unit+']',
                   title='High Pressure Turbine Outflow Temperature')
        plt.grid()
        plt.savefig('test-turbine1-outflow-temp.png', dpi=300)

        # Condenser graphs
        condenser = plant_net.modules[-1]

        (quant, time_unit) = condenser.outflow_phase.get_quantity_history('temp')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.latex_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('test-condenser-outflow-temp.png', dpi=300)

    # Properly shutdown simulation
    plant.close()
if __name__ == '__main__':
    main()
