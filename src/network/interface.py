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
from src.configtree import ConfigTree
from .network import network
#*********************************************************************************

#*********************************************************************************
class Network():

 def __init__( self, netConfigNode = ConfigTree() ):

  network( self, netConfigNode ) # constructor
 
  return

#---------------------------------------------------------------------------------
# "Approved" accessors 
# NB: if you access private data through other means, you will get what you deserve

 def GetName(self):
  return self.name

 def GetConnectivity(self):
  return self.connectivity

 def GetModuleNames(self):
  return self.moduleNames

 def SetRuntimeCortixCommFile(self, moduleName, fullPathFileName):
  self.runtimeCortixCommFile[ moduleName ] = fullPathFileName

 def GetRuntimeCortixCommFile(self, moduleName):
     if moduleName in self.runtimeCortixCommFile: 
        return self.runtimeCortixCommFile[ moduleName ]
     return None

#*********************************************************************************
# Printing utilities

 def __str__( self ):
   s = 'Network data members: name=%5s'
   return s % (self.name)

 def __repr__( self ):
   s = 'Network data members: name=%5s'
   return s % (self.name)

#*********************************************************************************
# Unit testing. Usage: -> python network.py
if __name__ == "__main__":
  print('Unit testing for Network')
