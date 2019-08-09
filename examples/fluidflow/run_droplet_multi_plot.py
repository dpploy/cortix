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

'''
MPI-active version of the droplet application.
Each Droplet is connected to a DataPlot and all Droplets are connected to a single
Vortex.

Run with

nprocs = 2*n_droplets + 1 vortex + 1 cortix  processes

Usage: mpirun -np nprocs run_droplet_multi_plot.py
'''

if __name__ == "__main__":

    # Parameters
    n_droplets = 3
    end_time   = 500
    time_step  = 0.1

    cortix = Cortix(use_mpi=True)

    # Vortex module (single).
    vortex = Vortex()
    vortex.show_time = (True,100)
    vortex.end_time = end_time
    vortex.time_step = time_step
    vortix.plot_velocity()

    for i in range(n_droplets):

        # Droplet modules.
        droplet = Droplet()
        droplet.end_time = end_time
        droplet.time_step = time_step
        droplet.bounce = False
        droplet.slip = False
        # Ports def.
        external_flow = Port('external-flow')
        droplet.add_port(external_flow)
        visualization = Port('visualization')
        droplet.add_port(visualization)

        # DataPlot modules.
        data_plot = DataPlot()
        data_plot.title = 'Droplet Trajectory '+str(i)
        data_plot.dpi = 300
        # Ports def.
        plot = Port('viz-data:{:05}'.format(i))
        data_plot.add_port(plot)

        # Vortex module.
        # Ports def.
        fluid_flow = Port('fluid-flow:{}'.format(i))
        vortex.add_port(fluid_flow)

        # Network connectivity
        external_flow.connect(fluid_flow)
        visualization.connect(plot)

        # Add modules to Cortix
        cortix.add_module(droplet)
        cortix.add_module(data_plot)

    cortix.add_module(vortex)

    cortix.run()
