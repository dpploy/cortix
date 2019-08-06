#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import scipy.constants as const

from cortix.src.cortix_main import Cortix

from cortix.examples.prison import Prison
from cortix.examples.parole import Parole
from cortix.examples.adjudication import Adjudication
from cortix.examples.jail import Jail
from cortix.examples.arrested import Arrested
from cortix.examples.probation import Probation
from cortix.examples.community import Community

'''
Crimninal justice example in progress.
'''

if __name__ == "__main__":

    # Configuration Parameters
    use_mpi = False  # True for MPI; False for Python multiprocessing

    end_time  = 50 * const.day
    time_step = 0.5 * const.day
    n_groups  = 150 # number of population groups

    cortix = Cortix(use_mpi=use_mpi)

    prison = Prison(n_groups=n_groups)
    cortix.add_module(prison)
    prison.end_time = end_time
    prison.time_step = time_step

    parole = Parole(n_groups=n_groups)
    cortix.add_module(parole)
    parole.end_time = end_time
    parole.time_step = time_step

    adjudication = Adjudication(n_groups=n_groups)
    cortix.add_module(adjudication)
    adjudication.end_time = end_time
    adjudication.time_step = time_step

    jail = Jail(n_groups=n_groups)
    cortix.add_module(jail)
    jail.end_time = end_time
    jail.time_step = time_step

    arrested = Arrested(n_groups=n_groups)
    cortix.add_module(arrested)
    arrested.end_time = end_time
    arrested.time_step = time_step

    probation = Probation(n_groups=n_groups)
    cortix.add_module(probation)
    probation.end_time = end_time
    probation.time_step = time_step

    community = Community(n_groups=n_groups, maturity_rate=100/const.day, offender_pool_size=10)
    cortix.add_module(community)
    community.end_time = end_time
    community.time_step = time_step
    community.show_time = (True,10*const.day)

    prison.connect( 'parole', parole.get_port('prison') )
    adjudication.connect( 'prison', prison.get_port('adjudication') )
    jail.connect( 'prison', prison.get_port('jail') )
    jail.connect( 'adjudication', adjudication.get_port('jail') )
    arrested.connect( 'jail', jail.get_port('arrested') )
    arrested.connect( 'adjudication', adjudication.get_port('arrested') )
    probation.connect( 'arrested', arrested.get_port('probation') )
    probation.connect( 'jail', jail.get_port('probation') )
    probation.connect( 'adjudication', adjudication.get_port('probation') )
    community.connect( 'arrested', arrested.get_port('community') )
    community.connect( 'jail', jail.get_port('community') )
    community.connect( 'probation', probation.get_port('community') )
    community.connect( 'adjudication', adjudication.get_port('community') )
    community.connect( 'prison', prison.get_port('community') )
    community.connect( 'parole', parole.get_port('community') )

    cortix.draw_network('network.png')

    cortix.run()
