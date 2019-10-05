#!/usr/bin/env python

import os

def test_send_recv():
    assert(os.system("mpirun --oversubscribe -np 3 python mpi_test_send_recv.py") == 0)

if __name__ == "__main__":
    test_send_recv()
