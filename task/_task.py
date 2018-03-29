"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io, time
import logging
from cortix.utils.configtree import ConfigTree
from ._setup import _Setup
#*********************************************************************************

#---------------------------------------------------------------------------------
# Task class constructor

def _Task( self, parentWorkDir = None, 
                 taskConfigNode = ConfigTree() ):

  assert type(parentWorkDir) is str, '-> parentWorkDir invalid.' 

# Inherit a configuration tree
  assert type(taskConfigNode) is ConfigTree, '-> taskConfigNode not a ConfigTree.' 
  self.configNode = taskConfigNode

# Read the simulation name
  self.name = self.configNode.get_node_name()

# Set the work directory (previously created)
  assert os.path.isdir( parentWorkDir ), 'work directory not available.'
  self.workDir = parentWorkDir + 'task_' + self.name + '/'
  os.system( 'mkdir -p ' + self.workDir )

# Create the logging facility for the object
  node = taskConfigNode.get_sub_node('logger')
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
    assert False, 'logger level for %r: %r invalid' % (loggerName, loggerLevel)

  self.log = log

  fh = logging.FileHandler(self.workDir+'task.log')
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
        assert False, 'file handler log level for %r: %r invalid' % (loggerName, fhLevel)
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
        assert False, 'console handler log level for %r: %r invalid' % (loggerName, chLevel)
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

  self.startTime     = 0.0
  self.startTimeUnit = 'null-startTimeUnit'

  self.evolveTime     = 0.0
  self.evolveTimeUnit = 'null-evolveTimeUnit'

  self.timeStep     = 0.0
  self.timeStepUnit = 'null-timeStepUnit'

  self.runtimeCortixParamFile = 'null-runtimeCortixParamFile'

#---------------------------------------------------------------------------------
# Setup this object

  _Setup( self )

#---------------------------------------------------------------------------------

  s = 'created task: '+self.name
  self.log.info(s)


  return

#*********************************************************************************
