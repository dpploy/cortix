#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
'''

'''

import logging
import scipy.constants as const

from cortix import Cortix
from cortix import Network

from bwr import BWR
from turbine import Turbine
from condenser import Condenser

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

    # Simulation time and stepping input

    end_time  = 4.0 * const.hour
    time_step = 1.0 * const.minute

    use_mpi = False  # True for MPI; False for Python multiprocessing

    plant = Cortix( use_mpi=use_mpi, splash=True )

    plant_net = plant.network = Network()

    # General parameters

    show_time = (True,20)

    params = dict()
    params['turbine-runoff-pressure'] = 1
    params['runoff-pressure'] = params['turbine-runoff-pressure']

    reactor   = BWR(params)
    plant_net.module(reactor)

    turbine   = Turbine(params)
    plant_net.module(turbine)

    condenser = Condenser(params)
    plant_net.module(condenser)
    plant_net.connect( [reactor,'coolant-outflow'], [turbine,'steam-inflow'] )
    plant_net.connect( [turbine,'runoff'], [condenser,'inflow'] )
    plant_net.connect( [condenser,'outflow'], [reactor,'coolant-inflow'] )

    plant_net.draw()
    plant_net.run()
if __name__ == '__main__':
    main()
