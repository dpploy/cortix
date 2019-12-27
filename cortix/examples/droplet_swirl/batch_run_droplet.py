#!/usr/bin/env python

import os
import time

def main():
    num_drops = 2
    while num_drops < 2**10:
        num_procs = 2 * num_drops + 1
        cmd = "mpirun -np {} run_droplet_swirl.py {}".format(num_procs, num_drops)
        before = time.time()
        os.system(cmd)
        elapsed_time = time.time() - before
        num_drops *= 2

if __name__ == "__main__":
    main()
