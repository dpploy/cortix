#!/usr/bin/env python

import os
import time

def main():
    num_drops = 2
    max_drops = 32
    record = []
    while num_drops < max_drops:
        num_procs = 2 * num_drops + 1
        cmd = "mpirun -np {} run_droplet_swirl.py {} > /dev/null 2>&1".format(num_procs, num_drops)
        before = time.time()
        print("Running with {} droplets and {} processes...".format(num_drops, num_procs))
        os.system(cmd)
        elapsed_time = time.time() - before
        print("Elapsed time: {}".format(elapsed_time))
        num_drops *= 2
        runs.append((num_drops, elapsed_time))

if __name__ == "__main__":
    main()
