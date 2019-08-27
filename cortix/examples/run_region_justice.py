#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
'''
Crimninal justice network dynamics modeling.

This example uses 7 modules:
    - Community
    - Arrested
    - Adjudication
    - Jail
    - Prison
    - Probation
    - Parole
and a population balance model is used to follow the offenders population
groups between modules.

To run this case using MPI you should compute the number of
processes as follows:

    `nprocs = 7 + 1 cortix`

then issue the MPI run command as follows (replace `nprocs` with a number):

     `mpiexec -n nprocs run_justice.py`

To run this case with the Python multiprocessing library, just run this file at the
command line as

    `run_justice.py`

'''

import scipy.constants as const

import matplotlib.pyplot as plt

from cortix import Cortix
from cortix import Network

from cortix.examples.state import State
from cortix.examples.city_justice.prison import Prison
from cortix.examples.city_justice.parole import Parole
from cortix.examples.city_justice.adjudication import Adjudication
from cortix.examples.city_justice.jail import Jail
from cortix.examples.city_justice.arrested import Arrested
from cortix.examples.city_justice.probation import Probation
from cortix.examples.city_justice.community import Community

def main():
    '''Cortix run file for a criminal justice network.

    Attributes
    ----------
    n_groups : int
        Number of population groups being followed. This must be the same for all
        modules.
    end_time: float
        End of the flow time in SI unit.
    time_step: float
        Size of the time step between port communications in SI unit.
    use_mpi: bool
        If set to `True` use MPI otherwise use Python multiprocessing.

    '''

    # Configuration Parameters
    n_groups  = 150 # number of population groups
    end_time  = 50 * const.day
    time_step = 0.5 * const.day

    use_mpi = False  # True for MPI; False for Python multiprocessing

    region = Cortix(use_mpi=use_mpi, splash=True)

    region.network = Network()
    ne_net = region.network

    state_1 = State('State-1')
    ne_net.module(state_1)
    state_1.end_time = end_time
    state_1.time_step = time_step

    state_2 = State('State-2')
    ne_net.module(state_2)
    state_2.end_time = end_time
    state_2.time_step = time_step

    ne_net.connect( [state_1,'outflow:1'], [state_2,'inflow:1'] )
    ne_net.connect( [state_2,'outflow:1'], [state_1,'inflow:1'] )
    ne_net.draw()

    '''
    # a_state internal network
    a_state.network = Network()
    a_state = a_state.network

    community_me = Community(n_groups=n_groups, maturity_rate=100/const.day,
            offender_pool_size=10)
    a_state.module(community_me)
    community_me.end_time = end_time
    community_me.time_step = time_step
    community_me.show_time = (True,10*const.day)

    prison_me = Prison(n_groups=n_groups)
    a_state.module(prison_me)
    prison_me.end_time = end_time
    prison_me.time_step = time_step

    parole_me = Parole(n_groups=n_groups)
    a_state.module(parole_me)
    parole_me.end_time = end_time
    parole_me.time_step = time_step

    adjudication_me = Adjudication(n_groups=n_groups)
    a_state.module(adjudication_me)
    adjudication_me.end_time = end_time
    adjudication_me.time_step = time_step

    jail_me = Jail(n_groups=n_groups)
    a_state.module(jail)
    jail_me.end_time = end_time
    jail_me.time_step = time_step

    arrested_me = Arrested(n_groups=n_groups)
    a_state.module(arrested_me)
    arrested_me.end_time = end_time
    arrested_me.time_step = time_step

    probation_me = Probation(n_groups=n_groups)
    a_state.module(probation_me)
    probation_me.end_time = end_time
    probation_me.time_step = time_step


    a_state.connect( prison, parole, 'bidirectional' )
    a_state.connect( adjudication, prison )
    a_state.connect( jail, prison )
    a_state.connect( adjudication, jail )
    a_state.connect( arrested, jail )
    a_state.connect( arrested, adjudication )
    a_state.connect( arrested, probation )
    a_state.connect( probation, jail )
    a_state.connect( adjudication, probation )

    a_state.connect( arrested, community )
    a_state.connect( jail, community )
    a_state.connect( probation, community )
    a_state.connect( adjudication, community )
    a_state.connect( prison, community )
    a_state.connect( parole, community )

    a_state.draw()
    '''

    #region.run()

    # Properly shutdow region
    region.close()

if __name__ == '__main__':
    main()
