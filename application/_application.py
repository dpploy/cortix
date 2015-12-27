"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

An Application object is the composition of Module objects and Network objects.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import logging
from cortix.utils.configtree import ConfigTree

from ._setupmodules import _SetupModules
from ._setupnetworks import _SetupNetworks
#*********************************************************************************

#---------------------------------------------------------------------------------
# Application class constructor

def _Application( self,
                   appWorkDir = None,
                   appConfigNode = ConfigTree()
                 ):

  assert type(appWorkDir) is str, '-> appWorkDir is invalid' 

# Inherit a configuration tree
  assert type(appConfigNode) is ConfigTree, '-> appConfigNode invalid' 
  assert type(appConfigNode.GetNodeTag()) is str, 'empty xml tree.'
  self.configNode = appConfigNode

# Read the application name
  self.name = self.configNode.GetNodeName()

# Set the work directory (previously created)

  self.workDir = appWorkDir
  assert os.path.isdir( appWorkDir ), 'work directory not available.'

# Set the module library for the whole application

  node = appConfigNode.GetSubNode('moduleLibrary')
  self.moduLibName = node.get('name').strip()

  subnode = ConfigTree( node )
  assert subnode.GetNodeTag() == 'moduleLibrary', ' fatal.'
  for child in subnode.GetNodeChildren():
   (elem, tag, attributes, text) = child
   if tag == 'parentDir': self.moduLibFullParentDir = text.strip()
 
  if self.moduLibFullParentDir[-1] == '/': self.moduLibFullParentDir.strip('/') 

  # add library full path to python module search
  sys.path.insert(1,self.moduLibFullParentDir)

# Create the logging facility for the singleton object
  node = appConfigNode.GetSubNode('logger')
  loggerName = self.name + '.app' # postfix to avoid clash of loggers
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

  fh = logging.FileHandler(self.workDir+'app.log')
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

  self.log = log

  s = 'created Application logger: ' + self.name
  self.log.info(s)

  s = 'logger level: '+loggerLevel
  self.log.debug(s)
  s = 'logger file handler level: '+fhLevel
  self.log.debug(s)
  s = 'logger console handler level: '+chLevel
  self.log.debug(s)

#--------
# modules        
#--------
  self.modules = list()
  _SetupModules( self )

#--------
# networks
#--------
  self.networks = list()
  _SetupNetworks( self )

  s = 'created application: '+self.name
  self.log.info(s)


  return

#*********************************************************************************
