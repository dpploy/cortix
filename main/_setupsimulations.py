#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import datetime
import logging
from cortix.utils.configtree import ConfigTree
from cortix.simulation.interface import Simulation
#*********************************************************************************

#---------------------------------------------------------------------------------
# Build Cortix simulations

def _SetupSimulations(self):

  for sim in self.configTree.GetAllSubNodes('simulation'):
 
    s = '_SetupSimulations(): simulation name: '+sim.get('name')
    self.log.debug(s)

    simConfigTree = ConfigTree(sim)

    simulation = Simulation( self.workDir, simConfigTree ) 

    self.simulations.append( simulation )

  return

#*********************************************************************************
