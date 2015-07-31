#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Cortix is a library and it is used by means of a driver. This file is a simple example
of a driver. Many Cortix objects can be ran simultaneously; a single object
may be sufficient since many simulation/tasks can be ran via one object.

As Cortix evolves additional complexity may be added to this driver and/or other
driver examples can be created.

Cortix is written in python language and it is imported as an namespace package
as of python 3.3 or later.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import sys, os
from main.interface import Cortix
#*********************************************************************************

def Main():

 pwd                = os.path.dirname(__file__)
 fullPathConfigFile = os.path.join(pwd, 'input/cortix-config.xml')

 # NB: if another instantiation of Cortix occurs, the cortix wrk directory specified
 #     in the cortix configuration file must be different, else the logging facility 
 #     will have log file collision.
 cortix1 = Cortix( 'cortix1', fullPathConfigFile )

# sys.exit(0)

# tested
# cortix1.RunSimulations( taskName='solo-fueldepot' )
# cortix1.RunSimulations( taskName='solo-shear' )
# cortix1.RunSimulations( taskName='solo-dissolve' )
 cortix1.RunSimulations( taskName='fueldepot-chopper' )
# cortix1.RunSimulations( taskName='fueldepot-chopper-storage' )

# untested
# cortix1.RunSimulations( taskName='shear-dissolve-offgas' )
# cortix1.RunSimulations( taskName='solo-fuel-accum' )
# cortix1.RunSimulations( taskName='solo-dissolve' )
# cortix1.RunSimulations( taskName='shear-dissolve' )
# cortix1.RunSimulations( taskName='shear-double-dissolve-single-condense' )

#*********************************************************************************
# Usage: -> python cortix-main.py or ./cortix-main.py
if __name__ == "__main__":
 Main()
