#!/usr/bin/env python
from cortix import Cortix
from cortix import Module
from cortix import Network
from cortix import Port
from body import Body
import pickle
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import os
import numpy as np

def main():
    um = False
    sim_time = 365 * 24 * 3600 # 157788000.0 * 10
    time_step = 24 * 3600 # 25000.0

    universe_rad = 2.5e11

    cortix = Cortix(use_mpi=um)
    cortix.network = Network()

    earth_mass = 5.9740e+24
    earth_pos = np.array([1.4960e+11, 0.0, 0.0])
    earth_vel = np.array([(0.0, 2.9800e+04, 0.0)])
    earth = Body(earth_mass, earth_pos, earth_vel, sim_time, time_step)
    earth.name = "earth"
    cortix.network.module(earth)

    mars_mass = 6.4190e+23
    mars_pos = np.array([2.2790e+11, 0.0, 0.0])
    mars_vel = np.array([0.0, 2.4100e+04, 0.0])
    mars = Body(mars_mass, mars_pos, mars_vel, sim_time, time_step)
    mars.name = "mars"
    cortix.network.module(mars)

    mercury_mass = 3.3020e+23
    mercury_pos = np.array([5.7900e+10, 0.0, 0.0])
    mercury_vel = np.array([0.0, 4.7900e+04, 0.0])
    mercury = Body(mercury_mass, mercury_pos, mercury_vel, sim_time, time_step)
    mercury.name = "mercury"
    cortix.network.module(mercury)

    venus_mass = 4.8690e+24
    venus_pos = np.array([1.0820e+11, 0.0, 0.0])
    venus_vel = np.array([0.0, 3.5000e+04 , 0.0])
    venus = Body(venus_mass, venus_pos, venus_vel, sim_time, time_step)
    venus.name = "venus"
    cortix.network.module(venus)

    sun_mass = 1.9890e+30
    sun_pos = np.array([0.0, 0.0, 0.0])
    sun_vel = np.array([0.0, 0.0, 0.0])
    sun = Body(sun_mass, sun_pos, sun_vel, sim_time, time_step)
    sun.name = "sun"
    cortix.network.module(sun)

    for x, i in enumerate(cortix.network.modules):
        i.save = True
        i.dt = time_step
        i.time = sim_time
        for y, j in enumerate(cortix.network.modules):
            pi = Port("body_{}".format(y), um)

            if x != y and pi not in i.ports:
                i.ports.append(pi)

                pj = Port("body_{}".format(x), um)
                j.ports.append(pj)

                pj.connect(pi)
                cortix.network.gv_edges.append((str(x), str(y)))

    cortix.run()
    cortix.network.draw()

    return [(b.name, b.trajectory) for b in cortix.network.modules]

def parse_trajectory(file_name):
    traj = []
    with open(file_name, "r") as f:
        lines = [l.strip().split(",") for l in f.readlines()]
        for line in lines:
            traj.append([float(i) for i in line])
    return trajectories

def plot_trajectories(trajectories):
    au = (149.6e6 * 1000)
    scale = 250 / au

    fig = plt.figure(1)
    ax = fig.gca(projection='3d')
    patches = []
    plt.draw()
    plt.pause(.1)

    for t in trajectories:
        x = [i[0] * scale for i in t]
        y = [i[1] * scale for i in t]
        z = [i[2] * scale for i in t]
        ax.plot(x, y, z)
    plt.savefig("planets.png")


if __name__ == "__main__":
    #main()
    import matplotlib
    matplotlib.use("GTK3Agg")

    trajectories = []
    for file in os.listdir("."):
        if file.endswith(".csv"):
            trajectories.append(parse_trajectory(file))
    plot_trajectories(trajectories)
    plt.show()
