"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import datetime
from   src.configtree import ConfigTree
from   .setup import setup
#*********************************************************************************

#*********************************************************************************
def network(self, netConfigNode):  # network class constructor

  assert type(netConfigNode) is ConfigTree, '-> netConfigNode is invalid.' 

  self.configNode = netConfigNode

  self.name = self.configNode.GetNodeName()

  setup( self )

  return

#*********************************************************************************
