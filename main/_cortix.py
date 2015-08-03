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

from ._setupsimulations import _SetupSimulations
#*********************************************************************************

#---------------------------------------------------------------------------------
# Cortix class constructor

def _Cortix( self,
             name = None,
             configFile = 'cortix-config.xml'
           ):

    assert name is not None, 'must give Cortix object a name'

    assert type(configFile) is str, '-> configFile not a str.' 
    self.configFile = configFile

# Create a configuration tree
    self.configTree = ConfigTree( configFileName=self.configFile )

# Read this object's name
    node  = self.configTree.GetSubNode('name')
    self.name = node.text.strip()
 
    # check
    assert self.name == name, 'cortix object name conflicts with cortix-config.xml'

# Read the work directory name
    node  = self.configTree.GetSubNode('workDir')
    wrkDir = node.text.strip()
    if wrkDir[-1] != '/': wrkDir += '/'

    self.workDir = wrkDir + self.name + '-wrk/'

# Create the work directory 
    if os.path.isdir(self.workDir):
      os.system( 'rm -rf ' + self.workDir )

    os.system( 'mkdir -p ' + self.workDir )

# Create the logging facility for each object  
    node = self.configTree.GetSubNode('logger')
    loggerName = self.name
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


    fh = logging.FileHandler(self.workDir+'cortix.log')
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

    self.log = log

    self.log.info('created Cortix logger: '+self.name)

    s = 'logger level: '+loggerLevel
    self.log.debug(s)
    s = 'logger file handler level: '+fhLevel
    self.log.debug(s)
    s = 'logger console handler level: '+chLevel
    self.log.debug(s)

    self.log.info('created Cortix work directory: '+self.workDir)

# Setup simulations (one or more as specified in the config file)

    self.simulations = list()

    _SetupSimulations( self )

    self.log.info('created Cortix object '+self.name)

    return 
  
#*********************************************************************************
