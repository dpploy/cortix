#!/usr/bin/env python
from cortix import Cortix
from cortix import Module
from cortix import Network
from cortix import Port
from body import Body

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

import numpy as np

def main():
    um = False
    num_bodies = 10

    universe_rad = 2.5e11

    cortix = Cortix(use_mpi=um)
    cortix.network = Network()

    earth_mass = 5.9740e+24
    earth_pos = np.array([1.4960e+11, 0.0, 0.0])
    earth_vel = np.array([(0.0, 2.9800e+04, 0.0)])
    earth = Body(earth_mass, earth_pos, earth_vel)
    cortix.network.module(earth)

    mars_mass = 6.4190e+23
    mars_pos = np.array([2.2790e+11, 0.0, 0.0])
    mars_vel = np.array([0.0, 2.4100e+04, 0.0])
    mars = Body(mars_mass, mars_pos, mars_vel)
    cortix.network.module(mars)

    mercury_mass = 3.3020e+23
    mercury_pos = np.array([5.7900e+10, 0.0, 0.0])
    mercury_vel = np.array([0.0, 4.7900e+04, 0.0])
    mercury = Body(mercury_mass, mercury_pos, mercury_vel)
    cortix.network.module(mercury)

    venus_mass = 4.8690e+24
    venus_pos = np.array([1.0820e+11, 0.0, 0.0])
    venus_vel = np.array([0.0, 3.5000e+04 , 0.0])
    venus = Body(venus_mass, venus_pos, venus_vel)
    cortix.network.module(venus)

    sun_mass = 1.9890e+30
    sun_pos = np.array([0.0, 0.0, 0.0])
    sun_vel = np.array([0.0, 0.0, 0.0])
    sun = Body(sun_mass, sun_pos, sun_vel)
    cortix.network.module(sun)

    for x, i in enumerate(cortix.network.modules):
        i.save = True
        for y, j in enumerate(cortix.network.modules):
            pi = Port("body_{}".format(y), um)

            if x != y and pi not in i.ports:
                i.ports.append(pi)

                pj = Port("body_{}".format(x), um)
                j.ports.append(pj)

                pj.connect(pi)

    cortix.run()

    fig = plt.figure(1)
    ax = fig.add_subplot(111, projection='3d')
    trajectories = [b.trajectory for b in cortix.network.modules]

    import pickle
    with open("traj.pkl", "wb") as f:
        pickle.dump(trajectories, f)

    for t in trajectories:
        t = t[1]
        x = [0 if np.isnan(i[0]) else i[0] for i in t]
        y = [0 if np.isnan(i[1]) else i[1] for i in t]
        z = [0 if np.isnan(i[2]) else i[2] for i in t]
        print(t)
        ax.autoscale = False
        ax.plot(x, y, z)

    plt.savefig("planets.png")

if __name__ == "__main__":
    main()
