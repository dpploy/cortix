#!/usr/bin/env python

import os
import time
import matplotlib
matplotlib.use('Agg', warn=False)
import matplotlib.pyplot as plt

def main():
    num_drops = 2
    max_drops = 1024
    runs = []
    while num_drops < max_drops:
        num_procs = 2 * num_drops + 1
        cmd = "mpirun -np {} run_droplet_swirl.py {}".format(num_procs, num_drops)
        before = time.time()
        print("Running with {} droplets and {} processes...".format(num_drops, num_procs))
        os.system(cmd)
        elapsed_time = time.time() - before
        print("Elapsed time: {}".format(elapsed_time))
        num_drops *= 2
        runs.append((num_drops, elapsed_time))

    with open("output.csv", "w") as f:
        for (drops, elapsed_time) in runs:
            f.write("{},{}\n".format(drops, elapsed_time))

    plt.plot([x for (x, y) in runs], [y for (x, y) in runs])
    plt.title("Number of droplets vs Run time")
    plt.xlabel("Number of Droplets")
    plt.ylabel("Elapsed time (s)")
    plt.savefig("runs.png")

if __name__ == "__main__":
    main()
