#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Sat Jun  6 22:43:33 EDT 2015
"""
#*********************************************************************************
import os, sys, io, time, datetime
import logging
from threading import Thread

import importlib
#*********************************************************************************

#---------------------------------------------------------------------------------
# Launcher class constructor

def _Launcher( self, modLibName, moduleName, slotId,
                     inputFullPathFileName, 
                     execFullPathFileName,
                     workDir,
                     cortexParamFullPathFileName,
                     cortexCommFullPathFileName,
                     runtimeStatusFullPathFileName ):

  self.moduleName                    = moduleName
  self.slotId                        = slotId
  self.inputFullPathFileName         = inputFullPathFileName 
  self.cortexParamFullPathFileName   = cortexParamFullPathFileName 
  self.cortexCommFullPathFileName    = cortexCommFullPathFileName 
  self.runtimeStatusFullPathFileName = runtimeStatusFullPathFileName 

  self.execFullPathFileName = execFullPathFileName
  self.workDir              = workDir

#.................................................................................
# Create logger for this driver and its imported pymodule 
  log = logging.getLogger('launcher-'+self.moduleName+'_'+str(self.slotId))
  log.setLevel(logging.DEBUG)
# create file handler for logs
  fullPathTaskDir = self.cortexCommFullPathFileName[:self.cortexCommFullPathFileName.rfind('/')]+'/'
  fh = logging.FileHandler(fullPathTaskDir+'launcher.log')
  fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
  ch = logging.StreamHandler()
  ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  fh.setFormatter(formatter)
  ch.setFormatter(formatter)
# add the handlers to the logger
  log.addHandler(fh)
  log.addHandler(ch)

  self.log = log

  s = 'created logger'
  log.info(s)

  s = 'input file: ' + self.inputFullPathFileName
  log.debug(s)

  s = 'param file: ' + self.cortexParamFullPathFileName
  log.debug(s)

  s = 'comm file: ' + self.cortexCommFullPathFileName
  log.debug(s)

  libModuleDriver = modLibName+'.'+moduleName+'.cortix-driver'

  s = 'module driver: ' + libModuleDriver
  log.info(s) 
 
  # import the python module driver
  self.pyModule = importlib.import_module(libModuleDriver)

  s = 'imported pyModule: ' + str(self.pyModule)
  log.info(s) 

  return

#*********************************************************************************
