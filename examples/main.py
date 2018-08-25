# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/cortix
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/cortix/blob/master/COPYRIGHT.txt
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

Cortix is written in python language and it is imported as an namespace package
as of python 3.3 or later.
"""
#*********************************************************************************
import os
from mpi4py import MPI
from cortix import Cortix 
#*********************************************************************************

def main():

 pwd                   = os.path.dirname(__file__)
 full_path_config_file = os.path.join(pwd, 'input/cortix-config.xml')

 # NB: if another instantiation of Cortix occurs, the cortix wrk directory specified
 #     in the cortix configuration file must be different, else the logging facility 
 #     will have log file collision.

 comm = MPI.COMM_WORLD
 size = comm.Get_size()
 rank = comm.Get_rank()

 if (rank == 0):
  cortix1 = Cortix( 'cortix-dev1', full_path_config_file )
#  cortix1.run_simulations( task_name='solo-pyplot' )
  cortix1.run_simulations( task_name='solo-fueldepot' )
# sys.exit(0)

# tested
#cortix1.run_simulations( task_name='solo-pyplot' )
 #cortix1.run_simulations( task_name='solo-fueldepot' )
# cortix1.RunSimulations( taskName='solo-shear' )     # oldchopper
# cortix1.RunSimulations( taskName='solo-dissolverA' ) # olddissolver
# cortix1.RunSimulations( taskName='solo-plume' )
# cortix1.RunSimulations( taskName='solo-cooltower' )
# cortix1.RunSimulations( taskName='fueldepot-chopper' )
# cortix1.RunSimulations( taskName='fueldepot-chopper-storage' )
# cortix1.RunSimulations( taskName='fueldepot-chopper-dissolver' )
# cortix1.RunSimulations( taskName='fueldepot-chopper-dissolver-tank' )
# cortix1.RunSimulations( taskName='fueldepot-chopper-dissolver-tank-feedprep' )
# cortix1.RunSimulations( taskName='solo-condenser' )
# cortix1.RunSimulations( taskName='solo-tank' )
# cortix1.RunSimulations( taskName='tank-feedprep' )

# testing
# cortix1.RunSimulations( taskName='solo-solventxtract' )

# untested
# cortix1.RunSimulations( taskName='shear-dissolve-offgas' )
# cortix1.RunSimulations( taskName='solo-fuel-accum' )
# cortix1.RunSimulations( taskName='shear-dissolve' )
# cortix1.RunSimulations( taskName='shear-double-dissolve-single-condense' )

#*********************************************************************************
# Usage: -> python cortix-main.py or ./cortix-main.py
if __name__ == "__main__":
 main()
