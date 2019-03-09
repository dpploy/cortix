#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/cortix/blob/master/COPYRIGHT.txt
#
# Licensed under the University of Massachusetts Lowell LICENSE:
# https://github.com/dpploy/cortix/blob/master/LICENSE.txt
"""
Cortix: a program for system-level modules coupling, execution, and analysis.

Cortix is a library and it is used by means of a driver. This file is a simple example
of a driver. Many Cortix objects can be ran simultaneously; a single object
may be sufficient since many simulation/tasks can be ran via one object.

As Cortix evolves additional complexity may be added to this driver and/or other
driver examples can be created.
"""
# *********************************************************************************
import os
from mpi4py import MPI
from cortix import Cortix
# *********************************************************************************


def main():

    pwd = os.path.dirname(__file__)
    full_path_config_file = os.path.join(pwd, '../input/cortix-config.xml')

    # NB: if another instantiation of Cortix occurs, the cortix wrk directory specified
    #     in the cortix configuration file must be different, else the logging facility
    #     will have log file collision.

    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    if (rank == 0):
        cortix1 = Cortix('cortix1', full_path_config_file)
        cortix1.run_simulations( task_name='solo-pyplot')  # see cortix-config.xml

#  cortix1 = Cortix( 'cortix1', full_path_config_file )
#  cortix1.run_simulations( task_name='solo-fueldepot' ) # see cortix-config.xml
# ---------------------- end def main():----------------------------------


# *********************************************************************************
if __name__ == "__main__":
    main()
