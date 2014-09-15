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
from src.configtree import ConfigTree
from src.simulation import Simulation
#*********************************************************************************

#*********************************************************************************
class Cortix(object):

# Private member data
# __slots__ = [

 def __init__( self,
               name = None,
               configFile = 'cortix-config.xml'
             ):

    assert name is not None, 'must give Cortix object a name'

    assert type(configFile) is str, '-> configFile not a str.' 
    self.__configFile = configFile

# Create a configuration tree
    self.__configTree = ConfigTree( configFileName=self.__configFile )

# Read this object's name
    node  = self.__configTree.GetSubNode('name')
    self.__name = node.text.strip()
 
    # check
    assert self.__name == name, 'cortix object name conflicts with cortix-config.xml'

# Read the work directory name
    node  = self.__configTree.GetSubNode('workDir')
    wrkDir = node.text.strip()
    if wrkDir[-1] != '/': wrkDir += '/'

    self.__workDir = wrkDir + self.__name + '-wrk/'

# Create the work directory 
    if os.path.isdir(self.__workDir):
      os.system( 'rm -rf ' + self.__workDir )

    os.system( 'mkdir -p ' + self.__workDir )

# Create the logging facility for each object  
    node = self.__configTree.GetSubNode('logger')
    loggerName = self.__name
    log = logging.getLogger(loggerName)
    log.setLevel(logging.NOTSET)

    loggerLevel = node.get('level').strip()
    if   loggerLevel == 'DEBUG': log.setLevel(logging.DEBUG)
    elif loggerLevel == 'INFO':  log.setLevel(logging.INFO)
    elif loggerLevel == 'WARN': log.setLevel(logging.WARN)
    elif loggerLevel == 'ERROR': log.setLevel(logging.ERROR)
    elif loggerLevel == 'CRITICAL': log.setLevel(logging.CRITICAL)
    elif loggerLevel == 'FATAL': log.setLevel(logging.CRITICAL)
    else:
      assert True, 'logger level for %r: %r invalid' % (loggerName, loggerLevel)

    self.__log = log

    fh = logging.FileHandler(self.__workDir+'cortix.log')
    fh.setLevel(logging.NOTSET)

    ch = logging.StreamHandler()
    ch.setLevel(logging.NOTSET)

    for child in node:
     if child.tag == 'fileHandler':
        # file handler
        fhLevel = child.get('level').strip()
        if   fhLevel == 'DEBUG': fh.setLevel(logging.DEBUG)
        elif fhLevel == 'INFO': fh.setLevel(logging.INFO)
        elif fhLevel == 'WARN': fh.setLevel(logging.WARN)
        elif fhLevel == 'ERROR': fh.setLevel(logging.ERROR)
        elif fhLevel == 'CRITICAL': fh.setLevel(logging.CRITICAL)
        elif fhLevel == 'FATAL': fh.setLevel(logging.FATAL)
        else:
          assert True, 'file handler log level for %r: %r invalid' % (loggerName, fhLevel)
     if child.tag == 'consoleHandler':
        # console handler
        chLevel = child.get('level').strip()
        if   chLevel == 'DEBUG': ch.setLevel(logging.DEBUG)
        elif chLevel == 'INFO': ch.setLevel(logging.INFO)
        elif chLevel == 'WARN': ch.setLevel(logging.WARN)
        elif chLevel == 'ERROR': ch.setLevel(logging.ERROR)
        elif chLevel == 'CRITICAL': ch.setLevel(logging.CRITICAL)
        elif chLevel == 'FATAL': ch.setLevel(logging.FATAL)
        else:
          assert True, 'console handler log level for %r: %r invalid' % (loggerName, chLevel)
    # formatter added to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add handlers to logger
    log.addHandler(fh)
    log.addHandler(ch)

    self.__log.info('created logger: '+self.__name)

    s = 'logger level: '+loggerLevel
    self.__log.debug(s)
    s = 'logger file handler level: '+fhLevel
    self.__log.debug(s)
    s = 'logger console handler level: '+chLevel
    self.__log.debug(s)

    self.__log.info('created work directory: '+self.__workDir)

# Setup simulations (one or more as specified in the config file)

    self.__simulations = list()

    self.__SetupSimulations()

    self.__log.info('created Cortix object '+self.__name)

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

