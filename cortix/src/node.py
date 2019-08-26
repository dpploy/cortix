import networkx as nx
from cortix.src.module import Module

class Graph:
    def __init__(self):
        self.g = nx.Digraph()

    def add(self, mod):
        assert(isinstance(mod, Module)), "mod must be of type Module!"
        self.g.add_node(mod)
        mod.id = len(self.f.nodes)

    def connect(self, m1, m2):
        assert(isinstance(m1, Module)), "m1 must be of type Module!"
        assert(isinstance(m2, Module)), "m2 must be of type Module!"
        self.g.add_edge(m1, m2)

