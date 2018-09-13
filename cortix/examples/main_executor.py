#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/...
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/COPYRIGHT
#
# Licensed under the GNU General Public License v. 3, please see LICENSE file.
# https://www.gnu.org/licenses/gpl-3.0.txt
"""
Cortix: a program for system-level modules coupling, execution, and analysis.

Cortix is a library and it is used by means of a driver. This file is a simple example
of a driver. Many Cortix objects can be ran simultaneously; a single object
may be sufficient since many simulation/tasks can be ran via one object.

As Cortix evolves additional complexity may be added to this driver and/or other
driver examples can be created.
"""
#*********************************************************************************
import os
from mpi4py import MPI
from mpi4py.futures import MPIPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from cortix import Cortix 
#*********************************************************************************

def main():

 pwd                   = os.path.dirname(__file__)
 full_path_config_file = os.path.join(pwd, 'input/cortix-config.xml')

 # NB: if another instantiation of Cortix occurs, the cortix wrk directory specified
 #     in the cortix configuration file must be different, else the logging facility 
 #     will have log file collision.

# comm = MPI.COMM_WORLD
# size = comm.Get_size()
# rank = comm.Get_rank()
# print('size = ',size)
# print('rank = ',rank)

# if (rank == 0):
# Create a PoolExecutor (only one excutor is allowed; to avoid recursion)
# at the moment, this precludes multiple instantiations of Cortix.
# Todo: modify in the future if multiple instances of Cortix will be used 
# in the user code.
#
# MPI development (pool status: broken)
# pool_executor = MPIPoolExecutor()
# usage: mpiexec -n 4 python -m mpi4py.futures main.py
# pool_executor.bootup(wait=True)

# concurrent.futures development (pool status: working for thread, issues for process)
 pool_executor = ThreadPoolExecutor()
# pool_executor = ProcessPoolExecutor()
#
 cortix1 = Cortix( 'cortix-dev1', full_path_config_file, pool_executor ) # see cortix-config.xml
#
# usage: uncomment only one at a time
# cortix1.run_simulations( task_name='solo-pyplot' )
 cortix1.run_simulations( task_name='solo-fueldepot' )
# cortix1.run_simulations( task_name='fueldepot-chopper' )
#---------------------- end def main():-------------------------------------------

#*********************************************************************************
# Usage: -> python cortix-main.py or ./cortix-main.py
if __name__ == "__main__":
 main()
