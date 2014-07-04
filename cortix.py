#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for integrating system-level modules

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import datetime
import logging
from configtree import ConfigTree
from simulation import Simulation
#*********************************************************************************

# Create log for this python module and those that include this module
log = logging.getLogger('cortix')
log.setLevel(logging.DEBUG)

#*********************************************************************************
class Cortix(object):

# Private member data
# __slots__ = [

 def __init__( self,
               configFile = 'cortix-config.xml'
             ):

    assert type(configFile) is str, '-> configFile Not a str.' 
    self.__configFile = configFile

# Create a configuration tree
    self.__configTree = ConfigTree( configFileName=self.__configFile )

# Create the work directory 
    node  = self.__configTree.GetSubNode('workDir')
    wrkDir = node.text.strip()
    if wrkDir[-1] != '/': wrkDir += '/'
    self.__workDir = wrkDir + 'cortix-wrk/'

    if os.path.isdir(self.__workDir):
      os.system( 'rm -rf ' + self.__workDir )

    os.system( 'mkdir -p ' + self.__workDir )

# Create logging
    self.__log = logging.getLogger('cortix')
    # file handler
    fh = logging.FileHandler(self.__workDir+'cortix.log')
    fh.setLevel(logging.DEBUG)
    # console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # formatter added to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add handlers to logger
    log.addHandler(fh)
    log.addHandler(ch)

    log.info('work directory:'+self.__workDir)

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
 
    s = '__SetupSimulations(): simulation name: '+sim.get('name')
    self.__log.debug(s)

    simConfigTree = ConfigTree(sim)

    simulation = Simulation( self.__workDir, simConfigTree ) 

    self.__simulations.append( simulation )

  return

#*********************************************************************************
# Unit testing. Usage: -> python cortix.py
if __name__ == "__main__":

  print('Unit testing for Cortix')
  cortix = Cortix("cortix-config.xml")

