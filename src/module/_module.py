"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
from src.utils.configtree import ConfigTree
from ._setup import _Setup
#*********************************************************************************

#---------------------------------------------------------------------------------
# Module class constructor

def _Module( self, parentWorkDir = None, 
                   modLibName = None, 
                   modLibParentDir = None,
                   modConfigNode = ConfigTree() 
           ):

  assert type(parentWorkDir) is str, '-> parentWorkDir is invalid.' 

# Locate the module library

  self.modLibName      = modLibName
  self.modLibParentDir = modLibParentDir

# Inherit a configuration tree
  assert type(modConfigNode) is ConfigTree, '-> modConfigNode is invalid.' 
  self.configNode = modConfigNode

# Read the module name and type
  self.modName = self.configNode.GetNodeName()
  self.modType = self.configNode.GetNodeType()

  self.executableName = 'null'
  self.executablePath = 'null'
  self.inputFileName  = 'null'
  self.inputFilePath  = 'null'

  self.ports = list()  # list of (portName, portType, portMultiplicity)

  _Setup( self )  

  return

#*********************************************************************************
