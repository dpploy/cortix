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
#import logging.config
from configtree import ConfigTree
from simulation import Simulation
#*********************************************************************************

#logging.config.fileConfig('cortix-log.conf')

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

# create the work directory and logging
    node  = self.__configTree.GetSubNode('workDir')
    wrkDir = node.text.strip()
    if wrkDir[-1] != '/': wrkDir += '/'
    self.__workDir = wrkDir + 'cortix-wrk/'

    if os.path.isdir(self.__workDir):
      os.system( 'rm -rf ' + self.__workDir )

    os.system( 'mkdir -p ' + self.__workDir )

    logging.basicConfig( filename=self.__workDir+'cortix.log' )
    logger = logging.getLogger('cortix')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler( self.__workDir+'cortix.log' )
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.info('work directory:'+self.__workDir)

    self.__logger = logger

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
 
    self.__logger.info('simulation name: '+sim.get('name'))

    simConfigTree = ConfigTree(sim)
    simulation = Simulation( self.__workDir, simConfigTree ) 
    self.__simulations.append( simulation )

  return

#*********************************************************************************
# Unit testing. Usage: -> python cortix.py
if __name__ == "__main__":

  print('Unit testing for Cortix')
  cortix = Cortix("cortix-config.xml")

