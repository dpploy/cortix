#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import os
import shutil
import logging
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from multiprocessing import Process
from cortix.src.module import Module

class Cortix:
    '''
    The main Cortix class definition:
    1. Create the object
    2. Add modules
    3. Run the simulation
    '''

    def __init__(self, use_mpi=False):
        self.use_mpi = use_mpi

        if self.use_mpi:
            from mpi4py import MPI
            self.comm = MPI.COMM_WORLD
            self.rank = self.comm.Get_rank()
            self.size = self.comm.size

        # Setup the global logger
        self.__create_logger()
        self.modules = []
        self.log.info('Created Cortix object')
        self.nx_graph = None

    def add_module(self, m):
        assert isinstance(m, Module), "m must be a module"
        if m not in self.modules:
            self.modules.append(m)
            if self.use_mpi:
                m.rank = len(self.modules)
                for port in m.ports:
                    port.rank = m.rank

    def run(self):
        '''
        Run the Cortix simulation
        '''
        if self.use_mpi:
            assert self.size == len(self.modules) + 1, "Incorrect number of \
            processes (Required {}, got {})".format(len(self.modules) + 1, self.size)

        # Set port ids
        i = 0
        for mod in self.modules:
            for port in mod.ports:
                port.use_mpi = self.use_mpi
                port.id = i
                i += 1

        for mod in self.modules:
            if not self.use_mpi:
                self.log.info("Launching Module {}".format(mod))
                p = Process(target=mod.run)
                p.start()
            elif self.rank == mod.rank:
                self.log.info("Launching Module {} on rank {}".format(mod, self.rank))
                mod.run()

    def get_network(self):
        """
        Constructs and returns a networkx graph object representation of the
        Cortix module network.
        """
        if not self.use_mpi or self.rank == 0:
            if not self.nx_graph:
                g = nx.MultiGraph()
                for mod_one in self.modules:
                    class_name = mod_one.__class__.__name__
                    index = self.modules.index(mod_one)
                    mod_one_name = "{}_{}".format(class_name, index)
                    for mod_two in self.modules:
                        if mod_one != mod_two:
                            for port in mod_one.ports:
                                if port.connected in mod_two.ports:
                                    mod_two_name = "{}_{}".format(mod_two.__class__.__name__, self.modules.index(mod_two))
                                    if mod_two_name not in g or mod_one_name not in g.neighbors(mod_two_name):
                                        g.add_edge(mod_one_name, mod_two_name)
                self.nx_graph = g
            return self.nx_graph

    def draw_network(self, file_name="network.png", dpi=220):
        """
        Draws the networkx Module network graph using matplotlib

        `file_name`: The resulting network diagram output file name
        `dpi`: dpi used for generating the network image
        """
        g = self.nx_graph if self.nx_graph else self.get_network()
        colors = ["blue", "red", "green", "teal"]
        class_map = {}
        color_map = {}
        for node in g.nodes():
            class_name = "_".join(node.split("_")[:-1])
            if class_name not in class_map:
                class_map[class_name] = colors[len(class_map) % len(colors)]
            color_map[node] = class_map[class_name]
        f = plt.figure()
        pos = nx.spring_layout(g, k=0.15, iterations=20)
        nx.draw(g, pos, node_color=[color_map[n] for n in g.nodes], ax=f.add_subplot(111), linewidths=0.01)
        patches = []
        for c in class_map:
            patch = mpatches.Patch(color=class_map[c], label=c)
            patches.append(patch)
        plt.legend(handles=patches)
        f.savefig(file_name, dpi=dpi)

    def __create_logger(self):
        '''
        A helper function to setup the logging facility used in constructor
        '''
        self.log = logging.getLogger("cortix")
        self.log.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler("cortix.log")
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Formatter added to handlers
        if self.use_mpi:
            fs = "[{}] %(asctime)s - %(name)s - %(levelname)s - %(message)s".format(self.rank)
        else:
            fs = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        formatter = logging.Formatter(fs)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # add handlers to logger
        self.log.addHandler(file_handler)
        self.log.addHandler(console_handler)

if __name__ == "__main__":
    c = Cortix()
