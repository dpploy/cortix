#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import scipy.constants as const

from cortix.src.module import Module
from cortix.src.cortix_main import Cortix

from cortix.examples.prison import Prison
from cortix.examples.parole import Parole
from cortix.examples.adjudication import Adjudication
from cortix.examples.jail import Jail

'''
Crimninal justice example in progress.
'''

if __name__ == "__main__":

    # Configuration Parameters
    use_mpi = False # True for MPI; False for Python multiprocessing

    end_time  = 200 * const.day
    time_step = 0.5 * const.day
    n_groups  = 5   # number of population groups

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

    prison.connect( 'parole', parole.get_port('prison') )
    adjudication.connect( 'prison', prison.get_port('adjudication') )
    jail.connect( 'prison', prison.get_port('jail') )
    jail.connect( 'adjudication', adjudication.get_port('jail') )

    cortix.draw_network('network.png')

    cortix.run()
