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

# constructor helper
from ._network import _network
#*********************************************************************************

#*********************************************************************************
# Network interface
# Note to developer: internal implementation in separate files in this directory.

class Network():

 def __init__( self, netConfigNode = ConfigTree() ):

  _network( self, netConfigNode ) # non-member constructor (external implementation)
 
  return

#---------------------------------------------------------------------------------
# Accessors for "private" data
# Note to user: if you access through other means, you will get what you deserve

 def GetName(self): return self.name

 def GetConnectivity(self): return self.connectivity

 def GetSlotNames(self): return self.slotNames

 def SetRuntimeCortixCommFile(self, slotName, fullPathFileName):
     self.runtimeCortixCommFile[ slotName ] = fullPathFileName

 def GetRuntimeCortixCommFile(self, slotName):
     if slotName in self.runtimeCortixCommFile: 
        return self.runtimeCortixCommFile[ slotName ]
     return None

 def GetNXGraph(self): return self.nxGraph

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
