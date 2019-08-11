#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
'''
Crimninal justice network dynamics modeling.

'''

import scipy.constants as const

import matplotlib.pyplot as plt

from cortix.src.cortix_main import Cortix
from cortix.src.network import Network
from cortix.src.module import Module

# Specific modules
from cortix.examples.country import Country
from cortix.examples.state import State

def main():
    '''Cortix run file for a system.

    '''

    cortix = Cortix(use_mpi=True)

    # Create the top system
    usa = Module() # or Country()
    cortix.system(usa) # only allwed one top system

    # Create network
    usa.network = Network(n_modules=2)

    maine   = State('Maine')
    vermont = State('Vermont')

    usa.network.connect(maine,vermont)
    usa.network.draw('network.png')

    # Run system (this will run any nested underlying networks)
    cortix.run(usa)

    # Properly shutdow cortix
    cortix.close()

if __name__ == '__main__':
    main()
