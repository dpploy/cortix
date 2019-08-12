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

# Specific modules
from cortix.examples.state import State

def main():
    '''Cortix run file for a system.

    '''

    # Create the top system
    usa = Cortix()

    # Create the top system network
    usa.network = Network()

    # Create modules for the network
    maine   = State('Maine')
    vermont = State('Vermont')

    # Add modules to the network
    usa.network.module(maine)
    usa.network.module(vermont)

    # Connect the modules in the network
    usa.network.connect(maine,vermont,'bidirectional')
    usa.network.draw()

    # Run system (this will run any nested underlying networks)
    #usa.run()

    # Properly shutdow usa
    usa.close()

if __name__ == '__main__':
    main()
