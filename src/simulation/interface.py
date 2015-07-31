#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
from src.utils.configtree import ConfigTree
from src.application.interface import Application

# constructor helper
from ._simulation import _Simulation

from ._execute import _Execute
#*********************************************************************************

#*********************************************************************************
class Simulation():

 def __init__( self,
               parentWorkDir = None,
               simConfigNode = ConfigTree()
             ):

  _Simulation( self, parentWorkDir, simConfigNode )

  return

#---------------------------------------------------------------------------------
# Execute  

 def Execute( self, taskName=None ):

  _Execute( self, taskName )

  return

#*********************************************************************************
# Unit testing. Usage: -> python simulation.py
if __name__ == "__main__":
  print('Unit testing for Simulation')
