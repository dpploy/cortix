#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
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

then issue the MPI run command as follows (replace `nprocs` with a number):

     `mpiexec -n nprocs run_droplet.py`

To run this case with the Python multiprocessing library, just run this file at the
command line as

     `run_droplet.py`

Multiple Plot
-------------

The second network case is named "multiple plot". Here each Droplet is connected to an
instance of the DataPlot module, therefore many more nodes are added to the network
when compared to the first network case. To run this case using MPI compute

    `nprocs = 2*n_droplets + 1 vortex + 1 cortix`

then issue the MPI run command as follows (replace `nprocs`:

    `mpiexec -n nprocs run_droplet.py`

To run this case with the Python multiprocessing library, just run this file at the
command line as

    `run_droplet.py`
'''

import scipy.constants as const

from cortix import Cortix
from cortix import Network

from cortix.tests.dataplot import DataPlot
from cortix.examples.droplet_swirl.droplet import Droplet
from cortix.examples.droplet_swirl.vortex import Vortex

if __name__ == '__main__':

    # Configuration Parameters
    use_single_plot = True   # True for a single plot output
                            # False for multiple plot files and network
    use_mpi         = False # True for MPI; False for Python multiprocessing

    plot_vortex_profile = False # True may crash the X server.

    n_droplets = 10
    end_time   = 3*const.minute
    time_step  = 0.2

    cortix = Cortix(use_mpi=use_mpi, splash=True)
    cortix_net = Network()
    cortix.network = cortix_net

    # Network for a single plot case
    if use_single_plot:

        # Vortex module (single).
        vortex = Vortex()
        cortix_net.add_module(vortex)
        vortex.show_time = (True,1*const.minute)
        vortex.end_time = end_time
        vortex.time_step = time_step
        if plot_vortex_profile:
            vortex.plot_velocity()

        # DataPlot module (single).
        data_plot = DataPlot()
        cortix_net.add_module(data_plot)
        data_plot.title = 'Droplet Trajectories'
        data_plot.same_axis = True
        data_plot.dpi = 300

        for i in range(n_droplets):

            # Droplet modules (multiple).
            droplet = Droplet()
            cortix_net.add_module(droplet)
            droplet.end_time = end_time
            droplet.time_step = time_step
            droplet.bounce = False
            droplet.slip = False

            # Network port connectivity (connect modules through their ports)
            cortix_net.connect( [droplet,'external-flow'],
                                [vortex, vortex.get_port('fluid-flow:{}'.format(i))],
                               'bidirectional')
            cortix_net.connect( [droplet,'visualization'],
                             [data_plot, data_plot.get_port('viz-data:{:05}'.format(i))] )

    # Network for a multiple plot case
    if not use_single_plot:

        # Vortex module (single).
        vortex = Vortex()
        cortix_net.add_module(vortex)
        vortex.show_time = (True,100)
        vortex.end_time = end_time
        vortex.time_step = time_step
        if plot_vortex_profile:
            vortex.plot_velocity()

        for i in range(n_droplets):

            # Droplet modules (multiple).
            droplet = Droplet()
            cortix_net.add_module(droplet)
            droplet.end_time = end_time
            droplet.time_step = time_step
            droplet.bounce = False
            droplet.slip = False

            # DataPlot modules (multiple).
            data_plot = DataPlot()
            cortix_net.add_module(data_plot)
            data_plot.title = 'Droplet Trajectory '+str(i)
            data_plot.dpi = 300

            # Network port connectivity (connect modules through their ports)
            cortix_net.connect( [droplet,'external-flow'],
                                [vortex, vortex.get_port('fluid-flow:{}'.format(i))],
                               'bidirectional')
            cortix_net.connect( [droplet,'visualization'],
                             [data_plot, data_plot.get_port('viz-data:{:05}'.format(i))] )

    cortix_net.draw()

    cortix.run()

    # This properly ends the program
    cortix.close()
