#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

from cortix.src.module import Module
from cortix.src.port import Port
from cortix.src.cortix_main import Cortix

from cortix.examples.dataplot import DataPlot
from cortix.examples.droplet import Droplet
from cortix.examples.vortex import Vortex

'''
This example uses three modules instantiated many times in two different networks.
Each network configuration uses a different amount of module instances and a different
network topology. This example can be executed with MPI (if mpi4py is available) or
with the Python multiprocessing library. These choices are made by variables listed
below in the executable portion of this run file.

Single Plot
-----------

The first network case is named "single plot". Here one DataPlot module is connected
to all Droplet modules. To run this case using MPI you should compute the number of
processes as follows:

    `nprocs = n_droplets + 1 vortex + 1 data_plot + 1 cortix`

Then issue the MPI run command as follows (replace `nprocs`:

     `mpiexec -n nprocs run_droplet.py`

To run this case with the Python multiprocessing library, just run this file at the
command line as

     `run_droplet.py`

Multiple Plot
-------------

The second network case is named "multiple plot". Here each Droplet is connected to an
instance of the DataPlot module, therefore many more nodes are added to the network
when compared to the first network case. To run this case using MPI

    `nprocs = 2*n_droplets + 1 vortex + 1 cortix`

Then issue the MPI run command as follows (replace `nprocs`:

    `mpiexec -n nprocs run_droplet.py`

To run this case with the Python multiprocessing library, just run this file at the
command line as

    `run_droplet.py`
'''

if __name__ == "__main__":

    # Configuration Parameters
    use_single_plot = True  # True for a single plot output
                            # False for multiple plot files and network
    use_mpi         = True

    n_droplets = 5
    end_time   = 30
    time_step  = 0.1

    cortix = Cortix(use_mpi=use_mpi)

    # Network for a single plot case
    if use_single_plot:

        # Vortex module (single).
        vortex = Vortex()
        #cortix.add_module(vortex)
        vortex.show_time = (True,100)
        vortex.end_time = end_time
        vortex.time_step = time_step
        vortex.plot_velocity()

        # DataPlot module (single).
        data_plot = DataPlot()
        #cortix.add_module(data_plot)
        data_plot.title = 'Droplet Trajectories'
        data_plot.same_axes = True
        data_plot.dpi = 300

        for i in range(n_droplets):

            # Droplet modules.
            droplet = Droplet()
            #cortix.add_module(droplet)
            droplet.end_time = end_time
            droplet.time_step = time_step
            droplet.bounce = False
            droplet.slip = False
            # Ports def.
            external_flow = Port('external-flow')
            droplet.add_port(external_flow)
            visualization = Port('visualization')
            droplet.add_port(visualization)

            # DataPlot module ports def.
            plot = Port('viz-data:{:05}'.format(i))
            data_plot.add_port(plot)

            # Vortex module ports def.
            fluid_flow = Port('fluid-flow:{}'.format(i))
            vortex.add_port(fluid_flow)

            # Network connectivity (connect ports)
            external_flow.connect(fluid_flow)
            visualization.connect(plot)

            cortix.add_module(droplet)

        cortix.add_module(vortex)
        cortix.add_module(data_plot)

    # Network for a multiple plot case
    if not use_single_plot:

        # Vortex module (single).
        vortex = Vortex()
        #cortix.add_module(vortex)
        vortex.show_time = (True,100)
        vortex.end_time = end_time
        vortex.time_step = time_step
        vortex.plot_velocity()

        for i in range(n_droplets):

            # Droplet modules.
            droplet = Droplet()
            #cortix.add_module(droplet)
            droplet.end_time = end_time
            droplet.time_step = time_step
            droplet.bounce = False
            droplet.slip = False
            # Ports def.
            external_flow = Port('external-flow')
            droplet.add_port(external_flow)
            visualization = Port('visualization')
            droplet.add_port(visualization)

            # DataPlot modules (multiple).
            data_plot = DataPlot()
            #cortix.add_module(data_plot)
            data_plot.title = 'Droplet Trajectory '+str(i)
            data_plot.dpi = 300
            # Ports def.
            plot = Port('viz-data:{:05}'.format(i))
            data_plot.add_port(plot)

            # Vortex module.
            # Ports def.
            fluid_flow = Port('fluid-flow:{}'.format(i))
            vortex.add_port(fluid_flow)

            # Network connectivity (connect ports)
            external_flow.connect(fluid_flow)
            visualization.connect(plot)

            cortix.add_module(droplet)
            cortix.add_module(data_plot)

        cortix.add_module(vortex)

    cortix.draw_network('network.png')

    cortix.run()
