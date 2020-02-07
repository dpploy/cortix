#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
'''
UMass Lowell research nuclear reactor single point dynamics.
'''

import scipy.constants as unit
import matplotlib.pyplot as plt

from cortix import Cortix
from cortix import Network

from umlrr import UMLRR

def main():
    '''Cortix run file for UMass Lowell research nuclear reactor.

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

    end_time  = 1.0 * unit.hour
    time_step = 0.5 * unit.minute
    show_time = (True,15*unit.minute)

    use_mpi = False  # True for MPI; False for Python multiprocessing

    # System top level
    system = Cortix( use_mpi=use_mpi, splash=True )

    # Network
    plant_net = plant.network = Network()

    #from shutdown_params import shutdown_params
    #params = shutdown_params()

    # Create reactor module
    reactor = UMLRR()

    reactor.name      = 'UMLRR'
    reactor.save      = True
    reactor.time_step = time_step
    reactor.end_time  = end_time
    reactor.show_time = show_time

    # Add reactor module to network
    plant_net.module(reactor)

    # Create the network connectivity
    #plant_net.connect( [reactor, 'none'], [none,'none'] )

    #*****************************************************************************

    plant_net.draw()

    # Run network dynamics simulation
    plant_net.run()

    plot_results = False

    if plot_results and ( plant.use_multiprocessing or plant.rank == 0 ):

        # Reactor graphs
        reactor = plant_net.modules[0]

        (quant, time_unit) = reactor.neutron_phase.get_quantity_history('neutron-dens')

        quant.plot( x_scaling=1/unit.minute, x_label='Time [m]',
                    y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('neutron-dens.png', dpi=300)

        (quant, time_unit) = reactor.neutron_phase.get_quantity_history('delayed-neutrons-cc')
        quant.plot( x_scaling=1/unit.minute, x_label='Time [m]',
                    y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('delayed-neutrons-cc.png', dpi=300)

        (quant, time_unit) = reactor.reactor_phase.get_quantity_history('fuel-temp')

        quant.plot( x_scaling=1/unit.minute, x_label='Time [m]',
                    y_label =quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('fuel-temp.png', dpi=300)

    # Properly shutdow plant
    plant.close()

if __name__ == '__main__':
    main()
