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
import networkx as nx
import matplotlib.pyplot as plt
#*********************************************************************************

#---------------------------------------------------------------------------------
# Private method: Setup network    

def setup(self):

  self.connectivity = list(dict()) # connectivity information of the network
  self.moduleNames  = list()        # modules involved in the network

  self.runtimeCortixCommFile = dict() # cortix communication file for modules

  self.nxGraph = nx.MultiDiGraph(name=self.name) # graph of the network
  
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

     vtx1 = tmp['fromModule']
     vtx2 = tmp['toModule']
#     print(vtx1,vtx2)
     self.nxGraph.add_edge( vtx1, vtx2, 
                           fromPort=tmp['fromPort'],
                           toPort=tmp['toPort'])

#  print('\t\tCortix::Simulation::Application::Network: connectivity',self.connectivity)

  self.moduleNames = [ name for name in self.runtimeCortixCommFile.keys() ]

#  print('\t\tCortix::Simulation::Application::Network: modules',self.moduleNames)

#  print(self.connectivity)

#  print(self.nxGraph.name)
#  print(self.nxGraph.nodes())
#  print(self.nxGraph.edges())
#  print(list(self.nxGraph.edges_iter(data=True)))

#  pos = nx.circular_layout(self.nxGraph,scale=3)
#  nx.draw(self.nxGraph,pos,with_labels=True)
#  plt.savefig(self.name+'.png')

#  sys.exit(0)

  return

#*********************************************************************************
