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
from cortix.examples.prison import Prison
from cortix.examples.prison_campus import PrisonCampus
from cortix.examples.parole import Parole
from cortix.examples.jail import Jail

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

    # Maine sub-system
    maine.network = Network(n_modules=3)

    prison_A = Prison(style='A')
    maine.network.module(prison_A)

    parole_A = Parole(style='A')
    maine.network.module(parole_A)

    jail_A = Jail(style='A')
    maine.network.module(jail_A)

    maine.network.connect(prison_A,parole_A)
    maine.network.connect(jail_A,prison_A)
    maine.network.draw('network.png')

    # Vermont sub-system
    vermont.network = Network(n_modules=2)

    prison_B = Prison(style='B')
    vermont.network.module(prison_B)

    jail_B = Jail(style='B')
    vermont.network.module(jail_B)

    vermont.network.connect(jail_B,prison_B)
    vermont.network.draw('network.png')

    # Prison A-style sub-system
    prison_A.network = Network(n_modules=2)

    p1 = PrisonCampus('1')
    prison_A.network.module(p1)

    p2 = PrisonCampus('2')
    prison_A.network.module(p2)

    prison_A.network.connect(p1,p2)
    prison_A.network.draw()

    # Run system (this will run all nested underlying networks)
    cortix.run(usa)

    # Properly shutdow cortix
    cortix.close()

if __name__ == '__main__':
    main()
