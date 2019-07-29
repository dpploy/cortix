#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import os
import logging
import time
import datetime
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
        self.comm = None
        self.rank = None
        self.size = None

        # Fall back to multiprocessing if mpi4py is not available
        if self.use_mpi:
            try:
                from mpi4py import MPI
                self.comm = MPI.COMM_WORLD
                self.rank = self.comm.Get_rank()
                self.size = self.comm.size
            except ImportError:
                self.use_mpi = False

        # Setup the global logger 

        self.__create_logger()

        # Setup the network graph
        if self.rank == 0 or not self.use_mpi:
            self.nx_graph = None

        # Modules storage
        self.modules = list()

        # Done
        if self.rank == 0 or not self.use_mpi:
            self.log.info('Created Cortix object %s', self.__get_splash(begin=True))
            self.wall_clock_time_start = time.time()

            self.wall_clock_time_end = self.wall_clock_time_start
            self.end_run_date = datetime.datetime.today().strftime('%d%b%y %H:%M:%S')

        return

    def __del__(self):
        '''
        Note: by the time the body of this function is executed, the machinery of
        variables may have been deleted already. For example, `logging` is no longer
        there; do the least amount of work here.
        '''

        if self.rank == 0 or not self.use_mpi:
            print('Destroyed Cortix object on '+self.end_run_date+
                    self.__get_splash(begin=False))
            print('Elapsed wall clock time [s]: '+
                    str(round(self.wall_clock_time_end-self.wall_clock_time_start,2)))

    def add_module(self, m):
        '''
        Add a module to the Cortix object

        `m`: An instance of a class that inherits from the Module base class
        '''
        assert isinstance(m, Module), 'm must be a module'
        if m not in self.modules:
            self.modules.append(m)
            if self.use_mpi:
                m.rank = len(self.modules)
                for port in m.ports:
                    port.rank = m.rank

    def run(self):
        '''
        Run the Cortix simulation with MPI if available o.w. fallback to multiprocessing
        '''

        # Synchronize in the beginning
        if self.use_mpi:
            self.comm.Barrier()
            assert self.size == len(self.modules) + 1,\
                'Incorrect number of processes (Required %r, got %r)'%\
                (len(self.modules) + 1, self.size)

        # Set port ids
        i = 0
        for mod in self.modules:
            for port in mod.ports:
                port.use_mpi = self.use_mpi
                port.id = i
                i += 1

        # Run all modules in parallel
        for mod in self.modules:
            if not self.use_mpi:
                processes = list()
                self.log.info('Launching Module {}'.format(mod))
                p = Process(target=mod.run)
                processes.append(p)
                p.start()
            elif self.rank == mod.rank:
                self.log.info('Launching Module {} on rank {}'.format(mod, self.rank))
                mod.run()

        # Synchronize at the end
        if self.use_mpi:
            self.comm.Barrier()
        else:
            for p in processes:
                p.join()

        if self.rank == 0 or not self.use_mpi:
            self.end_run_date = datetime.datetime.today().strftime('%d%b%y %H:%M:%S')
            self.wall_clock_time_end = time.time()

        return

    def get_network(self):
        '''
        Constructs and returns a networkx graph representation of the module network.
        '''
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
                                for p2 in mod_two.ports:
                                    if id(port.connected) == id(p2):
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
        if self.use_mpi and self.rank != 0:
            return

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
        A helper function to setup the logging facility used in the constructor.
        '''

        # File removal
        if self.rank == 0 or not self.use_mpi:
            if os.path.isfile('cortix.log'):
                os.system('rm -rf cortix.log')

        # Sync here to allow for file removal
        if self.use_mpi:
            self.comm.Barrier()

        self.log = logging.getLogger('cortix')

        self.log.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler('cortix.log')
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Formatter added to handlers
        if self.use_mpi:
            fs = '[rank:{}] %(asctime)s - %(name)s - %(levelname)s - %(message)s'.format(self.rank)
        else:

            fs = "[{}] %(asctime)s - %(name)s - %(levelname)s - %(message)s".format(os.getpid())

        formatter = logging.Formatter(fs)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        self.log.addHandler(file_handler)
        self.log.addHandler(console_handler)

    def __get_splash(self, begin=True):

        splash = \
        '_____________________________________________________________________________\n'+\
        '      ...                                        s       .     (TAAG Fraktur)\n'+\
        '   xH88"`~ .x8X                                 :8      @88>\n'+\
        ' :8888   .f"8888Hf        u.      .u    .      .88      %8P      uL   ..\n'+\
        ':8888>  X8L  ^""`   ...ue888b   .d88B :@8c    :888ooo    .     .@88b  @88R\n'+\
        'X8888  X888h        888R Y888r ="8888f8888r -*8888888  .@88u  ""Y888k/"*P\n'+\
        '88888  !88888.      888R I888>   4888>"88"    8888    ''888E`    Y888L\n'+\
        '88888   %88888      888R I888>   4888> "      8888      888E      8888\n'+\
        '88888 `> `8888>     888R I888>   4888>        8888      888E      `888N\n'+\
        '`8888L %  ?888   ! u8888cJ888   .d888L .+    .8888Lu=   888E   .u./"888&\n'+\
        ' `8888  `-*""   /   "*888*P"    ^"8888*"     ^%888*     888&  d888" Y888*"\n'+\
        '   "888.      :"      "Y"          "Y"         "Y"      R888" ` "Y   Y"\n'+\
        '     `""***~"`                                           ""\n'+\
        '                             https://cortix.org                              \n'+\
        '_____________________________________________________________________________'

        if begin:
            message = \
            '\n_____________________________________________________________________________\n'+\
            '                             L A U N C H I N G                               \n'

        else:
            message = \
            '\n_____________________________________________________________________________\n'+\
            '                           T E R M I N A T I N G                             \n'

        return message + splash

if __name__ == '__main__':
    c = Cortix()
