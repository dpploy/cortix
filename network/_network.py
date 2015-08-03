"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
from   cortix.utils.configtree import ConfigTree
from   ._setup import _Setup
#*********************************************************************************

#---------------------------------------------------------------------------------
# Network class constructor

def _Network(self, netConfigNode):  

  assert type(netConfigNode) is ConfigTree, '-> netConfigNode is invalid.' 

  self.configNode = netConfigNode

  self.name = self.configNode.GetNodeName()

  _Setup( self )

  return

#*********************************************************************************
