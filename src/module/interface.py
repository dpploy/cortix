#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io, time
from src.configtree import ConfigTree

# constructor helper
from ._module import _Module

from ._execute import _Execute
#*********************************************************************************

#*********************************************************************************
# Module interface
# Note to developer: internal implementation in separate files in this directory.

class Module():

 def __init__( self,
               parentWorkDir = None,
               modLibName = None, modLibParentDir = None, 
               modConfigNode = ConfigTree()
             ):

  _Module( self, parentWorkDir, 
                 modLibName, modLibParentDir, 
                 modConfigNode )

  return

#---------------------------------------------------------------------------------
# Accessors (note: all accessors of member data can potentially change the
# python object referenced to). See NB below.

 def GetName(self):
  return self.modName

 def GetPorts(self):
  return self.ports  

 def GetPortType(self, portName):
     portType = None
     for port in self.ports:
       if port[0] == portName:
          portType = port[1] 

     return portType        

 def GetPortMode(self, portName):
     portMode = None
     for port in self.ports:
       if port[0] == portName:
          portMode = port[2] 

     return portMode        

 def GetPortNames(self):
     portNames = list()
     for port in self.ports:
        portNames.append( port[0] )

     return portNames

 def HasPortName(self, portName):
     for port in self.ports:
       if port[0] == portName: return True

     return False
#---------------------------------------------------------------------------------
# Execute module            

 def Execute(self, slotId, runtimeCortixParamFile, runtimeCortixCommFile ):

  runtimeModuleStatusFile = _Execute( self, slotId, 
                                      runtimeCortixParamFile, runtimeCortixCommFile )

  return runtimeModuleStatusFile

#*********************************************************************************
# Unit testing. Usage: -> python module.py
if __name__ == "__main__":
  print('Unit testing for Module')
