"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

An Application object is the composition of Module objects and Network objects.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import logging
from cortix.utils.configtree import ConfigTree

from cortix.network.interface import Network
#*********************************************************************************

#---------------------------------------------------------------------------------
# Setup network             

def _SetupNetworks(self):

  s = 'start _SetupNetworks()'
  self.log.debug(s)

  for netNode in self.configNode.get_all_sub_nodes('network'):

   netConfigNode = ConfigTree( netNode )
   assert netConfigNode.get_node_name() == netNode.get('name'), 'check failed'

   network = Network( netConfigNode )

   self.networks.append( network )

   s = 'appended network ' + netNode.get('name')
   self.log.debug(s)

  s = 'end _SetupNetworks()'
  self.log.debug(s)

  return

#*********************************************************************************
