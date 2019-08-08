#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import scipy.constants as const

from cortix.src.module import Module
from cortix.src.cortix_main import Cortix

from cortix.examples.droplet import Droplet
from cortix.examples.vortex import Vortex

'''
This example uses two modules instantiated many times.
This example can be executed with MPI (if mpi4py is available) or
with the Python multiprocessing library. These choices are made by variables listed
below in the executable portion of this run file.

To run this case using MPI you should compute the number of
processes as follows:

    `nprocs = n_droplets + 1 vortex + 1 cortix`

then issue the MPI run command as follows (replace `nprocs` with a number):

     `mpiexec -n nprocs run_droplet.py`

To run this case with the Python multiprocessing library, just run this file at the
command line as

    `run_droplet.py`
'''

if __name__ == '__main__':

    # Configuration Parameters
    use_mpi         = False # True for MPI; False for Python multiprocessing

    plot_vortex_profile = False # True may crash the X server.

    n_droplets = 10
    end_time   = 3*const.minute
    time_step  = 0.2

    cortix = Cortix(use_mpi=use_mpi)

    # Network for a single plot case

    # Vortex module (single).
    vortex = Vortex()
    cortix.add_module(vortex)
    vortex.show_time = (True,1*const.minute)
    vortex.end_time = end_time
    vortex.time_step = time_step
    if plot_vortex_profile:
        vortex.plot_velocity()

    for i in range(n_droplets):

        # Droplet modules (multiple).
        droplet = Droplet()
        cortix.add_module(droplet)
        droplet.end_time = end_time
        droplet.time_step = time_step
        droplet.bounce = False
        droplet.slip = False

        # Network port connectivity (connect modules through their ports)
        droplet.connect('external-flow', vortex.get_port('fluid-flow:{}'.format(i)))

    cortix.draw_network('network.png')

    cortix.run()

    # Plot all droplet trajectories
    modules = cortix.get_modules()

    if not use_mpi or cortix.rank == 0:

        from mpl_toolkits.mplot3d import Axes3D
        import matplotlib.pyplot as plt

        position_histories = list()
        for m in cortix.modules[1:]:
            position_histories.append( m.state.get_quantity_history('position')[0].value )

        fig = plt.figure(1)
        ax = fig.add_subplot(111,projection='3d')
        ax.set_title('Droplet Trajectories')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        for p in position_histories:
            x = [u[0] for u in p]
            y = [u[1] for u in p]
            z = [u[2] for u in p]
            ax.plot(x,y,z)

        fig.savefig('trajectories.png', dpi=300)

