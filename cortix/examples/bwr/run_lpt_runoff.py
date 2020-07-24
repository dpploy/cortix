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
from params import get_params

def main():
    """Cortix run file for a solvent extraction network.

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

    # System top level
    plant = Cortix(use_mpi=use_mpi, splash=True)

    # Network
    plant_net = plant.network = Network()

    params = get_params()
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

    # Create the network connectivity

    #*****************************************************************************

    plant_net.draw()

    # Run network dynamics simulation
    plant.run()

    plot_results = True

    if plot_results and (plant.use_multiprocessing or plant.rank == 0):

        # Reactor graphs
        reactor = plant_net.modules[0]

        (quant, time_unit) = reactor.neutron_phase.get_quantity_history('neutron-dens')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('test-neutron-dens.png', dpi=300)

        (quant, time_unit) = reactor.neutron_phase.get_quantity_history('delayed-neutrons-cc')
        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('test-delayed-neutrons-cc.png', dpi=300)

        (quant, time_unit) = reactor.coolant_outflow_phase.get_quantity_history('temp')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('test-coolant-outflow-temp.png', dpi=300)

        (quant, time_unit) = reactor.reactor_phase.get_quantity_history('fuel-temp')

        quant.plot(x_scaling=1/unit.minute, x_label='Time [m]',
                   y_label='Fuel Temp. [k]')
        plt.grid()
        plt.savefig('test-fuel-temp.png', dpi=300)

    # Properly shutdown simulation
    plant.close()

if __name__ == '__main__':
    main()
