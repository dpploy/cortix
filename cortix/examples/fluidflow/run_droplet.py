#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

from cortix.src.module import Module
from cortix.src.port import Port
from cortix.util.dataplot import DataPlot
from cortix.src.cortix_main import Cortix

from cortix.examples.fluidflow.droplet import Droplet
from cortix.examples.fluidflow.vortex import Vortex

"""
MPI-active version of droplet
Run with

nprocs = 2*n_droplets + 2 processes

Usage: mpirun -np nprocs run_droplet.py
"""

if __name__ == "__main__":

    c = Cortix(use_mpi=True)

    # Vortex module (single).
    vortex = Vortex()
    vortex.end_time = 1000

    n_droplets = 5

    for i in range(n_droplets):

        # Droplet modules.
        droplet = Droplet()
        droplet.end_time = 1000

        flow_velocity_port   = Port('flow-velocity')
        position_port        = Port('position')
        state_port           = Port('state')
        ext_fluid_props_port = Port('external-fluid-properties')

        droplet.add_port(flow_velocity_port)
        droplet.add_port(position_port)
        droplet.add_port(state_port)
        droplet.add_port(ext_fluid_props_port)

        # DataPlot modules.
        data_plot = DataPlot()
        data_plot.title = 'Droplet Position Over Time'

        plot_port = Port("plot-data:{}".format(i))

        data_plot.add_port(plot_port)

        # Vortex module.
        velocity_port    = Port("velocity:{}".format(i))
        #fluid_props_port = Port("fluid-properties:{}".format(i))

        vortex.add_port(velocity_port)
        #vortex.add_port(fluid_props_port)

        # Connect ports
        flow_velocity_port.connect(velocity_port)
        #ext_fluid_props_port.connect(fluid_props_port)
        position_port.connect(plot_port)

        # Add modules to Cortix
        c.add_module(droplet)
        c.add_module(data_plot)

    c.add_module(vortex)
    c.run()
