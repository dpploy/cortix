#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
'''

'''

#import logging
import scipy.constants as unit
import matplotlib.pyplot as plt

from cortix import Cortix
from cortix import Network

from reactor import BWR
from turbine import Turbine
from condenser import Condenser
from params import startup_params
from params import shutdown_params

def main():
    '''Cortix run file for a solvent extraction network.

    Attributes
    ----------
    end_time: float
        End of the flow time in SI unit.
    time_step: float
        Size of the time step between port communications in SI unit.
    use_mpi: bool
        If set to `True` use MPI otherwise use Python multiprocessing.

    '''

    # Preamble

    end_time = 25 * unit.minute
    time_step = 30.0 # seconds
    show_time = (True, 5*unit.minute)

    use_mpi = False  # True for MPI; False for Python multiprocessing

    # System top level
    plant = Cortix(use_mpi=use_mpi, splash=True)

    # Network
    plant_net = plant.network = Network()

    params = startup_params()
    params['start-time'] = 0
    params['end-time'] = end_time

    # Create reactor module
    reactor = BWR(params)

    reactor.name = 'BWR'
    reactor.save = True
    reactor.time_step = time_step
    reactor.end_time = end_time
    reactor.show_time = show_time

    # Add reactor module to network
    plant_net.module(reactor)

    # Create turbine 1 module
    params['turbine_inlet_pressure'] = 2
    params['turbine_outlet_pressure'] = 0.5
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
    params['turbine_inlet_pressure'] = 0.5
    params['turbine_outlet_pressure'] = 0.005
    params['high_pressure_turbine'] = False
    params['steam flowrate'] = params['steam flowrate']/2

    turbine2 = Turbine(params)

    turbine2.name = 'Low Pressure Turbine 1'
    turbine2.save = True
    turbine2.time_step = time_step
    turbine2.end_time = end_time

    plant_net.module(turbine2)

    #*****************************************************************************
    params['turbine_inlet_pressure'] = 0.5
    params['turbine_outlet_pressure'] = 0.005
    params['high_pressure_turbine'] = False

    turbine3 = Turbine(params)

    turbine3.name = 'Low Pressure Turbine 2'
    turbine3.save = True
    turbine3.time_step = time_step
    turbine3.end_time = end_time

    plant_net.module(turbine3)

    #*****************************************************************************
    params['steam flowrate'] = params['steam flowrate'] * 2

    condenser = Condenser(params)

    condenser.name = 'Condenser'
    condenser.save = True
    condenser.time_step = time_step
    condenser.end_time = end_time

    plant_net.module(condenser)

    #*****************************************************************************
    # Create the network connectivity
    plant_net.connect([reactor, 'coolant-outflow'], [turbine1, 'inflow'])
    plant_net.connect([turbine1, 'outflow-1'], [turbine2, 'inflow'])
    plant_net.connect([turbine1, 'outflow-2'], [turbine3, 'inflow'])
    plant_net.connect([turbine2, 'outflow-1'], [condenser, 'inflow-1'])
    plant_net.connect([turbine3, 'outflow-1'], [condenser, 'inflow-2'])
    plant_net.connect([condenser, 'outflow'], [reactor, 'coolant-inflow'])

    #*****************************************************************************

    plant_net.draw()

    # Run network dynamics simulation
    plant_net.run()

    plot_results = True

    if plot_results and (plant.use_multiprocessing or plant.rank == 0):

        # Reactor graphs
        reactor = plant_net.modules[0]

        (quant, time_unit) = reactor.neutron_phase.get_quantity_history('neutron-dens')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('startup-neutron-dens.png', dpi=300)

        (quant, time_unit) = reactor.neutron_phase.get_quantity_history('delayed-neutrons-cc')
        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('startup-delayed-neutrons-cc.png', dpi=300)

        (quant, time_unit) = reactor.coolant_outflow_phase.get_quantity_history('temp')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('startup-coolant-outflow-temp.png', dpi=300)

        (quant, time_unit) = reactor.reactor_phase.get_quantity_history('fuel-temp')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label='Fuel Temp. [k]')
        plt.grid()
        plt.savefig('startup-fuel-temp.png', dpi=300)

        # Turbine graphs
        turbine1 = plant_net.modules[1]

        (quant, time_unit) = turbine1.outflow_phase.get_quantity_history('power')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']',
                   title='High Pressure Turbine Power')
        plt.grid()
        plt.savefig('startup-turbine1-power.png', dpi=300)

        (quant, time_unit) = turbine1.outflow_phase.get_quantity_history('temp')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']',
                   title='High Pressure Turbine Outflow Temperature')
        plt.grid()
        plt.savefig('startup-turbine1-outflow-temp.png', dpi=300)

        # Turbine graphs
        turbine2 = plant_net.modules[2]

        (quant, time_unit) = turbine2.outflow_phase.get_quantity_history('power')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']',
                   title='Lower Pressure Turbine 1 Power')
        plt.grid()
        plt.savefig('startup-turbine2-power.png', dpi=300)

        (quant, time_unit) = turbine2.outflow_phase.get_quantity_history('temp')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']',
                   title='Lower Pressure Turbine 1 Outflow Temperature')
        plt.grid()
        plt.savefig('startup-turbine2-outflow-temp.png', dpi=300)

        # Condenser graphs
        condenser = plant_net.modules[-1]

        (quant, time_unit) = condenser.outflow_phase.get_quantity_history('temp')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('startup-condenser-outflow-temp.png', dpi=300)


    #setup initial values for simulation
    turbine1-outflow-temp = turbine1.outflow_phase.get_value('temp', end_time)
    turbine1-chi = turbine1.outflow_phase.get_value('quality', end_time)
    turbine1-power = turbine1.outflow_phase.get_value('power', end_time)

    turbine2-outflow-temp = turbine2.outflow_phase.get_value('temp', end_time)
    turbine2-chi = turbine2.outflow_phase.get_value('quality', end_time)
    turbine2-power = turbine2.outflow_phase.get_value('power', end_time)

    condenser-runoff-temp = condenser.outflow_phase.get_value('temp', end_time)
    delayed-neutron-cc = reactor.neutron_phase.get_value('delayed-neutrons-cc', time)
    n-dens = reactor.neutron_phase.get_value('neutron-dens', end_time)
    fuel-temp = reactor.reactor_phase.get_value('fuel-temp', end_time)
    coolant-temp = reactor.coolant_outflow_phase.get_value('temp', end_time)

    # Properly shutdown simulation
    plant.close()

#**************************************************************************************************
    # Now, run plant shutdown

    # Preamble
    start_time = end_time
    end_time = 1 * unit.hour
    time_step = 30.0 # seconds
    show_time = (True, 5*unit.minute)

    use_mpi = False  # True for MPI; False for Python multiprocessing

    # System top level
    plant = Cortix(use_mpi=use_mpi, splash=True)

    # Network
    plant_net = plant.network = Network()
    params = shutdown_params()
    params['start-time'] = start_time
    params['end-time'] = end_time

    #setup params
    params['turbine-outflow-temp'] = turbine1-outflow-temp
    params['turbine-chi'] = turbine1-chi
    params['turbine-power'] = turbine1-power

    params['delayed-neutron-cc'] = delayed-neutron-cc
    params['n-dens'] = n-dens
    params['fuel-temp'] = fuel-temp
    params['coolant-temp'] = coolant-temp

    params['condenser-runoff-temp'] = condenser-runoff-temp

    # Create reactor module
    reactor = BWR(params)

    reactor.name = 'BWR'
    reactor.save = True
    reactor.time_step = time_step
    reactor.end_time = end_time
    reactor.show_time = show_time

    # Add reactor module to network
    plant_net.module(reactor)

    # Create turbine 1 module
    params['turbine_inlet_pressure'] = 2
    params['turbine_outlet_pressure'] = 0.5
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
    params['turbine-chi'] = turbine2-chi
    params['turbine-outflow-temp'] = turbine2-outflow-temp
    params['turbine-power'] = turbine2-power
    params['turbine_inlet_pressure'] = 0.5
    params['turbine_outlet_pressure'] = 0.005
    params['high_pressure_turbine'] = False
    params['steam flowrate'] = params['steam flowrate']/2

    turbine2 = Turbine(params)

    turbine2.name = 'Low Pressure Turbine 1'
    turbine2.save = True
    turbine2.time_step = time_step
    turbine2.end_time = end_time

    plant_net.module(turbine2)

    #*****************************************************************************
    params['turbine_inlet_pressure'] = 0.5
    params['turbine_outlet_pressure'] = 0.005
    params['high_pressure_turbine'] = False

    turbine3 = Turbine(params)

    turbine3.name = 'Low Pressure Turbine 2'
    turbine3.save = True
    turbine3.time_step = time_step
    turbine3.end_time = end_time

    plant_net.module(turbine3)

    #*****************************************************************************
    params['steam flowrate'] = params['steam flowrate'] * 2

    condenser = Condenser(params)

    condenser.name = 'Condenser'
    condenser.save = True
    condenser.time_step = time_step
    condenser.end_time = end_time

    plant_net.module(condenser)

    #*****************************************************************************
    # Create the network connectivity
    plant_net.connect([reactor, 'coolant-outflow'], [turbine1, 'inflow'])
    plant_net.connect([turbine1, 'outflow-1'], [turbine2, 'inflow'])
    plant_net.connect([turbine1, 'outflow-2'], [turbine3, 'inflow'])
    plant_net.connect([turbine2, 'outflow-1'], [condenser, 'inflow-1'])
    plant_net.connect([turbine3, 'outflow-1'], [condenser, 'inflow-2'])
    plant_net.connect([condenser, 'outflow'], [reactor, 'coolant-inflow'])

    #*****************************************************************************

    # Run network dynamics simulation
    plant_net.run()

    plot_results = True

    if plot_results and (plant.use_multiprocessing or plant.rank == 0):

        # Reactor graphs
        reactor = plant_net.modules[0]

        (quant, time_unit) = reactor.neutron_phase.get_quantity_history('neutron-dens')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('shutdown-neutron-dens.png', dpi=300)

        (quant, time_unit) = reactor.neutron_phase.get_quantity_history('delayed-neutrons-cc')
        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('shutdown-delayed-neutrons-cc.png', dpi=300)

        (quant, time_unit) = reactor.coolant_outflow_phase.get_quantity_history('temp')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('shutdown-coolant-outflow-temp.png', dpi=300)

        (quant, time_unit) = reactor.reactor_phase.get_quantity_history('fuel-temp')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label='Fuel Temp. [k]')
        plt.grid()
        plt.savefig('shutdown-fuel-temp.png', dpi=300)

        # Turbine graphs
        turbine1 = plant_net.modules[1]

        (quant, time_unit) = turbine1.outflow_phase.get_quantity_history('power')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']',
                   title='High Pressure Turbine Power')
        plt.grid()
        plt.savefig('shutdown-turbine1-power.png', dpi=300)

        (quant, time_unit) = turbine1.outflow_phase.get_quantity_history('temp')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']',
                   title='High Pressure Turbine Outflow Temperature')
        plt.grid()
        plt.savefig('shutdown-turbine1-outflow-temp.png', dpi=300)

        # Turbine graphs
        turbine2 = plant_net.modules[2]

        (quant, time_unit) = turbine2.outflow_phase.get_quantity_history('power')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']',
                   title='Lower Pressure Turbine 1 Power')
        plt.grid()
        plt.savefig('shutdown-turbine2-power.png', dpi=300)

        (quant, time_unit) = turbine2.outflow_phase.get_quantity_history('temp')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']',
                   title='Lower Pressure Turbine 1 Outflow Temperature')
        plt.grid()
        plt.savefig('shutdown-turbine2-outflow-temp.png', dpi=300)

        # Condenser graphs
        condenser = plant_net.modules[-1]

        (quant, time_unit) = condenser.outflow_phase.get_quantity_history('temp')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('shutdown-condenser-outflow-temp.png', dpi=300)

        #shutdown plant
        plant.close()


if __name__ == '__main__':
    main()
