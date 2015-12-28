"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import datetime
import networkx as nx
import matplotlib.pyplot as plt
#*********************************************************************************

#---------------------------------------------------------------------------------
# Private method: Setup network    

def _Setup(self):

  self.connectivity = list(dict()) # connectivity information of the network
  self.slotNames  = list()         # modules involved in the network

  self.runtimeCortixCommFile = dict() # cortix communication file for modules

  self.nxGraph = nx.MultiDiGraph(name=self.name) # graph of the network
  
  for child in self.configNode.GetNodeChildren():

    ( elem, tag, attributes, text ) = child

    if tag == 'connect':
     assert text is None, 'non empty text, %r, in %r network: ' % (text,self.name)

    tmp = dict()

    if tag == 'connect': 

     for (key,value) in attributes: 
       assert key not in tmp.keys(), 'repeated key in attribute of %r network' % self.name
      
       value = value.strip()
       if key == 'fromModuleSlot': value = value.replace(':','_')
       if key == 'toModuleSlot'  : value = value.replace(':','_')

       tmp[key] = value

     self.connectivity.append( tmp )

     for (key,val) in tmp.items():
       if key == 'fromModuleSlot': self.runtimeCortixCommFile[ val ] = 'null-runtimeCortixCommFile'
       if key == 'toModuleSlot'  : self.runtimeCortixCommFile[ val ] = 'null-runtimeCortixCommFile'

     vtx1 = tmp['fromModuleSlot']
     vtx2 = tmp['toModuleSlot']
#     print(vtx1,vtx2)
     self.nxGraph.add_edge( vtx1, vtx2, 
                            fromPort=tmp['fromPort'],
                            toPort=tmp['toPort'])

#  print('\t\tCortix::Simulation::Application::Network: connectivity',self.connectivity)

  self.slotNames = [ name for name in self.runtimeCortixCommFile.keys() ]

#  print('\t\tCortix::Simulation::Application::Network: modules',self.slotNames)

#  print(self.connectivity)

#  print(self.nxGraph.name)
#  print(self.nxGraph.nodes())
#  print(self.nxGraph.nodes())
#  print(self.nxGraph.edges())
#  print(list(self.nxGraph.edges_iter(data=True)))

#  H = nx.Graph(self.nxGraph)
#  pos = nx.circular_layout(self.nxGraph,scale=6)
#  pos=nx.spring_layout(H,iterations=30)
#  nx.draw_networkx_nodes(self.nxGraph,pos,node_size=200,node_color='b',alpha=1.0)
#  nx.draw_networkx_nodes(H,pos,node_size=200,node_color='b',alpha=1.0)
#  nx.draw_networkx_labels(self.nxGraph,pos,fontsize=18)
#  nx.draw_networkx_labels(H,pos,fontsize=18)
#  nx.draw_networkx_edges(H,pos,alpha=0.4,node_size=0,width=1,edge_color='k')
#  nx.draw(self.nxGraph,pos,with_labels=True)
#  nx.draw_networkx_labels(self.nxGraph,pos,fontsize=18)
#  plt.savefig(self.name+'.png')

#  sys.exit(0)

  return

#*********************************************************************************
