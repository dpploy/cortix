#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules: integration, coupling, execution, 
        and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import datetime
from src.cortix import Cortix
#*********************************************************************************


def Main():

 pwd                = os.path.dirname(__file__)
 fullPathConfigFile = os.path.join(pwd, 'cortix-config.xml')

 # NB: if another instantiation of Cortix occur, the cortix wrk directory specified
 #     in the cortix configuration file must be different, else the logging facility 
 #     will have log file collision.
 cortix1 = Cortix( 'cortix1', fullPathConfigFile )

# cortix1.RunSimulations( taskName='solo-fuel-accum' )
# cortix1.RunSimulations( taskName='solo-dissolve' )
 cortix1.RunSimulations( taskName='shear-dissolve' )
# cortix1.RunSimulations( taskName='demuth1' )

#*********************************************************************************
# Usage: -> python cortix-main.py or ./cortix-main.py
if __name__ == "__main__":
  Main()
