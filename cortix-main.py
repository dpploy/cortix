#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for integrating system-level modules

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import datetime
from cortix import Cortix
#*********************************************************************************

def main():

 cortix = Cortix( "cortix-config.xml" )

# cortix.RunSimulations( taskName='solo-dissolve' )
 cortix.RunSimulations( taskName='shear-dissolve' )

#*********************************************************************************
# Usage: -> python cortix-main.py or ./cortix-main.py
if __name__ == "__main__":
  main()
