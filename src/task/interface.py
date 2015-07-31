#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io, time
from src.utils.configtree import ConfigTree

# constructor helper
from ._task import _Task

from ._execute import _Execute
#*********************************************************************************

#*********************************************************************************
class Task():

 def __init__( self,
               parentWorkDir = None,
               taskConfigNode = ConfigTree()
             ):

  _Task( self, parentWorkDir, taskConfigNode )

  return

#---------------------------------------------------------------------------------
# Accessors (note: all accessors of member data can potentially change the
# python object referenced to). See NB below.

 def GetName(self): 
  return self.name

 def GetWorkDir(self): 
  return self.workDir

 def GetEvolveTime(self):
  return self.evolveTime

 def GetEvolveTimeUnit(self):
  return self.evolveTimeUnit

 def GetTimeStep(self):
  return self.timeStep

 def GetTimeStepUnit(self):
  return self.timeStepUnit

 def SetRuntimeCortixParamFile(self, fullPath):
  self.runtimeCortixParamFile = fullPath

 def GetRuntimeCortixParamFile(self):
  return self.runtimeCortixParamFile

#---------------------------------------------------------------------------------
# Execute task              

 def Execute(self, application ):

  _Execute( self, application)

  return 

#*********************************************************************************
# Unit testing. Usage: -> python application.py
if __name__ == "__main__":
  print('Unit testing for Task')
