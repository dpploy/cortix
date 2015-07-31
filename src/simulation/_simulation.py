"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import logging
from src.configtree import ConfigTree
from src.application.interface import Application
#*********************************************************************************

#---------------------------------------------------------------------------------
# Simulation class constructor

def _Simulation( self, parentWorkDir = None, simConfigNode = ConfigTree() ):

  assert type(parentWorkDir) is str, '-> parentWorkDir invalid.' 

# Inherit a configuration tree
  assert type(simConfigNode) is ConfigTree, '-> simConfigNode invalid.' 
  self.configNode = simConfigNode

# Read the simulation name
  self.name = simConfigNode.GetNodeName()

# Create the cortix/simulation work directory
  wrkDir = parentWorkDir 
  wrkDir += 'sim_' + self.name + '/'
  self.workDir = wrkDir

  os.system( 'mkdir -p ' + self.workDir )

# Create the logging facility for each object

  node = simConfigNode.GetSubNode('logger')
  loggerName = self.name
  log = logging.getLogger(loggerName)
  log.setLevel(logging.NOTSET)

  loggerLevel = node.get('level').strip()
  if   loggerLevel == 'DEBUG': log.setLevel(logging.DEBUG)
  elif loggerLevel == 'INFO':  log.setLevel(logging.INFO)
  elif loggerLevel == 'WARN':  log.setLevel(logging.WARN)
  elif loggerLevel == 'ERROR':  log.setLevel(logging.ERROR)
  elif loggerLevel == 'CRITICAL':  log.setLevel(logging.CRITICAL)
  elif loggerLevel == 'FATAL':  log.setLevel(logging.FATAL)
  else:
    assert True, 'logger level for %r: %r invalid' % (loggerName, loggerLevel)

  self.log = log

  fh = logging.FileHandler(self.workDir+'sim.log')
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

  s = 'created logger: '+self.name
  self.log.info(s)

  s = 'logger level: '+loggerLevel
  self.log.debug(s)
  s = 'logger file handler level: '+fhLevel
  self.log.debug(s)
  s = 'logger console handler level: '+chLevel
  self.log.debug(s)

#------------
# Application
#------------
  for appNode in self.configNode.GetAllSubNodes('application'):

    appConfigNode = ConfigTree( appNode )
    assert appConfigNode.GetNodeName() == appNode.get('name'), 'check failed'

    self.application = Application( self.workDir, appConfigNode )

    s = 'created application: '+appNode.get('name')
    self.log.debug(s)

#------------
# Tasks
#------------
  self.tasks = list() # holds the task(s) created by the Execute method

  s = 'created simulation: '+self.name
  self.log.info(s)


  return

#*********************************************************************************
