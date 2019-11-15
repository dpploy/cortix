#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
'''

'''

import logging
import scipy.constants as const

from cortix.src.cortix_main import Cortix
from cortix.src.network import Network

from bwr import BWR

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

    bwr = Cortix( use_mpi=use_mpi, splash=True )

    bwr_net = bwr.network = Network()

    # General parameters

    show_time = (True,10)

if __name__ == '__main__':
    main()