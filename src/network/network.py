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
from .setup import setup
#*********************************************************************************

#*********************************************************************************
def network(self, netConfigNode):  # constructor

  assert type(netConfigNode) is ConfigTree, '-> netConfigNode is invalid.' 

  self.configNode = netConfigNode

  self.name = self.configNode.GetNodeName()
#  print('\t\tCortix::Simulation::Application::Network::network: name:',self.name)
#  print(__name__,self.name)

  self.connectivity = list(dict()) # connectivity information of the network
  self.moduleNames  = list()        # modules involved in the network

  self.runtimeCortixCommFile = dict() # cortix communication file for modules

  setup( self )

  return

#*********************************************************************************
