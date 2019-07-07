#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import os
import shutil
import logging
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
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

    def save_network(self, file_name):
        if self.rank == 0:
            conn = []
            g = nx.MultiDiGraph()
            for mod_one in self.modules:
                for mod_two in self.modules:
                    if mod_one != mod_two:
                        for port in mod_one.ports:
                            if port.connected in mod_two.ports:
                                mod_one_name = "{}_{}".format(mod_one.__class__.__name__, self.modules.index(mod_one))
                                mod_two_name = "{}_{}".format(mod_two.__class__.__name__, self.modules.index(mod_two))
                                mod_pair = (mod_one_name, mod_two_name)
                                if mod_pair not in conn and mod_pair[::-1] not in conn:
                                    g.add_edge(mod_one_name, mod_two_name)
                                    conn.append(mod_pair)
            f = plt.figure()
            pos = nx.shell_layout(g)
            nx.draw(g, pos, ax=f.add_subplot(111), with_labels=True)
            f.savefig(file_name, dpi=220)


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
