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

# constructor helper
from ._launcher import _Launcher

from ._run import _Run
#*********************************************************************************

#*********************************************************************************
class Launcher(Thread):
                     
 def __init__( self, modLibName, moduleName, slotId,
                     inputFullPathFileName, 
                     execFullPathFileName,
                     workDir,
                     cortexParamFullPathFileName,
                     cortexCommFullPathFileName,
                     runtimeStatusFullPathFileName ):

  _Launcher( self, modLibName, moduleName, slotId,
                   inputFullPathFileName, 
                   execFullPathFileName,
                   workDir,
                   cortexParamFullPathFileName,
                   cortexCommFullPathFileName,
                   runtimeStatusFullPathFileName )

  super(Launcher, self).__init__()

#---------------------------------------------------------------------------------
 def run( self ):

   _Run( self )

   return

#*********************************************************************************
# Usage: -> python launcher.py or ./launcher.py
if __name__ == "__main__":
   Launcher()
