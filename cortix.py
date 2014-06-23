#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for integrating system-level modules

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import datetime
from configtree import ConfigTree
from simulation import Simulation
#*********************************************************************************

#*********************************************************************************
class Cortix(object):

# Private member data
# __slots__ = [

 def __init__( self,
               configFile = 'cortix-config.xml'
             ):

    assert type(configFile) == str, '-> configFile Not a str.' 
    self.__configFile = configFile

# create a configuration tree
    self.__configTree = ConfigTree( configFileName=self.__configFile )

# setup simulations
    self.__simulations = list()
    self.__SetupSimulations()

#---------------------------------------------------------------------------------
# Simulate                  

 def RunSimulations(self, taskName=None):

  for sim in self.__simulations: sim.Execute( taskName )
  
  return

#---------------------------------------------------------------------------------
# Build Cortix simulations

 def __SetupSimulations(self):

  for sim in self.__configTree.GetAllSubNodes('simulation'):
 
    print('Cortix::__SetupSimulations(): ',sim.get('name'))

    simConfigTree = ConfigTree(sim)
    simulation = Simulation( simConfigTree ) 
    self.__simulations.append( simulation )

  return

#*********************************************************************************
# Unit testing. Usage: -> python cortix.py
if __name__ == "__main__":

  print('Unit testing for Cortix')
  cortix = Cortix("cortix-config.xml")

