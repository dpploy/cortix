#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Sat Jun  6 22:43:33 EDT 2015
"""
#*********************************************************************************
import os, sys, io, time, datetime
from threading import Thread

import importlib
#*********************************************************************************

#---------------------------------------------------------------------------------
# Launcher class constructor

def _Launcher( self, modLibName, modLibFullParentDir, moduleName, slotId,
                     inputFullPathFileName, 
                     cortexParamFullPathFileName,
                     cortexCommFullPathFileName,
                     runtimeStatusFullPathFileName ):

    self.moduleName                    = moduleName
    self.slotId                        = slotId
    self.inputFullPathFileName         = inputFullPathFileName 
    self.cortexParamFullPathFileName   = cortexParamFullPathFileName 
    self.cortexCommFullPathFileName    = cortexCommFullPathFileName 
    self.runtimeStatusFullPathFileName = runtimeStatusFullPathFileName 

    modulePath = modLibName+'.'+moduleName+'.cortix-driver'
    self.module = importlib.import_module(modulePath)

    return

#*********************************************************************************
