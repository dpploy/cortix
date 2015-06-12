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
import networkx as nx
#*********************************************************************************

#---------------------------------------------------------------------------------
# Setup network             

def setup(self):
  
  for child in self.configNode.GetNodeChildren():

    ( tag, attributes, text ) = child

    if tag == 'connect':
     assert text is None, 'non empty text, %r, in %r network: ' % (text,self.name)

    tmp = dict()

    if tag == 'connect': 

     for (key,value) in attributes: 
          assert key not in tmp.keys(), 'repeated key in attribute of %r network' % self.name
          tmp[key] = value

     self.connectivity.append( tmp )

     for (key,val) in tmp.items():
       if key == 'fromModule': self.runtimeCortixCommFile[ val ] = 'null'
       if key == 'toModule'  : self.runtimeCortixCommFile[ val ] = 'null'

#  print('\t\tCortix::Simulation::Application::Network: connectivity',self.connectivity)

  self.moduleNames = [ name for name in self.runtimeCortixCommFile.keys() ]

#  print('\t\tCortix::Simulation::Application::Network: modules',self.moduleNames)

  return

#*********************************************************************************
