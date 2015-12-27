"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
from cortix.utils.configtree import ConfigTree
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

# Inherit a configuration tree
  assert type(modConfigNode) is ConfigTree, '-> modConfigNode is invalid.' 
  self.configNode = modConfigNode

# Read the module name and type
  self.modName = self.configNode.GetNodeName()
  self.modType = self.configNode.GetNodeType()

# Specify module library with upstream information (override in _Setup() if needed)
  self.modLibParentDir = modLibParentDir
  self.modLibName      = modLibName

  self.executableName = 'null-executableName'
  self.executablePath = 'null-executablePath'
  self.inputFileName  = 'null-inputFileName'
  self.inputFilePath  = 'null-inputFilePath'

  self.ports = list()  # list of (portName, portType, portMultiplicity)

  _Setup( self )  

  return

#*********************************************************************************
