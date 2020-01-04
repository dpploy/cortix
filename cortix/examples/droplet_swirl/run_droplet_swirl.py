#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
'''
This example uses two modules instantiated many times. It be executed with MPI
(if `mpi4py` is available) or with the Python multiprocessing library. These choices
are made by variables listed below in the executable portion of this run file.

To run this case using MPI you should compute the number of
processes as follows:

    `nprocs = 2 * n_droplets + 1 cortix`

then issue the MPI run command as follows (replace `nprocs` with a number):

     `mpiexec -n nprocs run_droplet.py`

To run this case with the Python multiprocessing library, just run this file at the
command line as

    `run_droplet.py`

'''

import scipy.constants as const

from cortix import Cortix
from cortix import Network
from cortix.examples.droplet_swirl.droplet import Droplet
from cortix.examples.droplet_swirl.vortex import Vortex

def main(n_droplets = 5, end_time = 3 * const.minute, time_step = 0.2, create_plots = False):
    '''Cortix run file for a `Droplet`-`Vortex` network.

    Attributes
    ----------
    n_droplets: int
        Number of droplets to use (one per process).
    end_time: float
        End of the flow time in SI unit.
    time_step: float
        Size of the time step between port communications in SI unit.
    create_plots: bool
        Create various plots and save to files. (all data collected in the
        parent process; it may run out of memory).
    plot_vortex_profile: bool
        Whether to plot (to a file) the vortex function used.
    use_mpi: bool
        If set to `True` use MPI otherwise use Python multiprocessing.

    '''

    if n_droplets >= 2000:
        create_plots = False

    plot_vortex_profile = False # True may crash the X server.

    use_mpi = False # True for MPI; False for Python multiprocessing

    swirl = Cortix(use_mpi=use_mpi, splash=True)

    swirl.network = Network()

    for i in range(n_droplets):
        # Vortex module 1-to-1
        vortex = Vortex()
        swirl.network.module(vortex)
        vortex.show_time = (True, 1*const.minute)
        vortex.end_time = end_time
        vortex.time_step = time_step
        if plot_vortex_profile:
            vortex.plot_velocity()

        # Droplet modules (multiple)
        droplet = Droplet(save=create_plots)
        swirl.network.module(droplet)
        droplet.end_time = end_time
        droplet.time_step = time_step
        droplet.bounce = False
        droplet.slip = False
        droplet.save = True

        # Network port connectivity (connect modules through their ports)
        swirl.network.connect( [droplet,'external-flow'],
                               [vortex, vortex.get_port('fluid-flow:{}'.format(i))],
                               'bidirectional' )
    swirl.network.draw()

    swirl.run()

    # Plot all droplet trajectories
    if create_plots:
        modules = swirl.network.modules

        if swirl.use_multiprocessing or swirl.rank == 0:
            from mpl_toolkits.mplot3d import Axes3D
            import matplotlib.pyplot as plt
            import numpy as np

            # Extract droplets' trajectory from modules
            positions = [m.positions for m in swirl.network.modules if type(m) is Droplet]
            velocities = [m.velocities for m in swirl.network.modules if type(m) is Droplet]

            fig = plt.figure(1)
            ax = fig.add_subplot(111,projection='3d')
            ax.set_title('Droplet Trajectories')
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_zlabel('z')
            for pos in positions:
                x = [i[0] for i in pos]
                y = [i[1] for i in pos]
                z = [i[2] for i in pos]
                ax.plot(x, y, z)
            fig.savefig('trajectories.png', dpi=300)

            # All droplets' speed
            fig = plt.figure(2)
            plt.xlabel('Time [min]')
            plt.ylabel('Speed [m/s]')
            plt.title('All Droplets')

            for m in modules:
                if type(m) is Droplet:
                    speeds = [(i , np.linalg.norm(vel)) for (i, vel) in enumerate(m.velocities)]
                    plt.plot(speeds)

            plt.grid()
            fig.savefig('speeds.png', dpi=300)

            # All droplets' radial position
            fig = plt.figure(3)
            plt.xlabel('Time [min]')
            plt.ylabel('Radial Position [m]')
            plt.title('All Droplets')

            for m in modules:
                if type(m) is Droplet:
                    radial_positions = [(i , np.linalg.norm(vel[0:2])) for (i, vel) in enumerate(m.velocities)]
                    plt.plot(radial_positions)

            plt.grid()
            fig.savefig('radialpos.png', dpi=300)

    # This properly ends the program
    swirl.close()

if __name__ == '__main__':
    import sys
    num_drops = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    main(n_droplets=num_drops, create_plots=True)
