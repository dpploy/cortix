#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

from cortix.src.module import Module
from cortix.src.cortix_main import Cortix

from cortix.examples.dataplot import Prison
from cortix.examples.droplet import Parole

'''
Crimninal justice example in progress.
'''

if __name__ == "__main__":

    # Configuration Parameters
    use_mpi = True  # True for MPI; False for Python multiprocessing

    end_time   = 300
    time_step  = 0.1

    cortix = Cortix(use_mpi=use_mpi)

    prison = Prison()
    cortix.add_module(prison)

    parole = Parole()
    cortix.add_module(parole)

    prison.connect('parole',parole.get_port('prison'))

    cortix.draw_network('network.png')

    cortix.run()
