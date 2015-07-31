#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

An Application object is the composition of Module objects and Network objects.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
from src.configtree import ConfigTree

# constructor helper
from ._application import _Application
#*********************************************************************************

#*********************************************************************************
class Application(): # this is meant to be a singleton class

 def __init__( self,
               appWorkDir = None,
               appConfigNode = ConfigTree()
             ):

  _Application( self, appWorkDir, appConfigNode )

  return

#---------------------------------------------------------------------------------
# Getters

 def GetNetworks(self):
  return self.networks

 def GetNetwork(self, name):
  for net in self.networks:
     if net.GetName() == name: return net
  return None

 def GetModules(self):
  return self.modules

 def GetModule(self, name):
  for mod in self.modules:
     if mod.GetName() == name: return mod
  return None

#*********************************************************************************
# Unit testing. Usage: -> python application.py
if __name__ == "__main__":
  print('Unit testing for Application')
