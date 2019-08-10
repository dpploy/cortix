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
from multiprocessing import Process, Queue
from cortix.src.module import Module

class Cortix:
    '''Cortix main class definition.

    The typical Cortix workflow:

    1. Create the `Cortix` object
    2. Add and connect Modules
    3. Run the simulation

    Attributes
    ----------
    use_mpi: bool
        True for MPI, False for multiprocessing.
    splash: bool
        Show the Cortix splash image.
    comm: mpi4py.MPI.Intracomm
        MPI.COMM_WORLD (if using MPI else None).
    rank: int
        The current MPI rank (if using MPI else None).
    size: int
        size of the group associated with MPI.COMM_WORLD.
    '''

    def __init__(self, use_mpi=False, splash=False):
        '''Construct a Cortix simulation object.

        Parameters
        ----------
        use_mpi: bool
            True for MPI, False for multiprocessing.
        splash: bool
            Show the Cortix splash image.
        '''

        self.use_multiprocessing = True
        self.use_mpi = use_mpi
        if self.use_mpi:
            self.use_multiprocessing = False
        self.comm = None
        self.rank = None
        self.size = None
        self.splash = splash

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

            if self.splash:
                self.log.info('Created Cortix object %s', self.__get_splash(begin=True))
            else:
                self.log.info('Created Cortix object')

            self.wall_clock_time_start = time.time()

            self.wall_clock_time_end = self.wall_clock_time_start
            self.end_run_date = datetime.datetime.today().strftime('%d%b%y %H:%M:%S')

        return

    def add_module(self, m):
        '''Add a Module object to the Cortix Simulation

        Parameters
        ----------
        m: Module
            The Module object to be added
        '''

        assert isinstance(m, Module), 'm must be a module'
        if m not in self.modules:
            m.use_mpi = self.use_mpi
            self.modules.append(m)

    def get_modules(self):
        '''Return a list of all the Cortix modules from the master process.

        If the `run()` method has completed, the list is updated with data
        from the other processes.

        Returns
        -------
        modules: list(Module)
            The list of modules in the Cortix simulation
        '''

        if self.rank == 0 or self.use_multiprocessing:
            return self.modules

    def run(self):
        '''Run the Cortix simulation.

        This function concurrently executes the `cortix.src.module.run` function
        for each module in the simulation. Modules are run using either MPI or
        Multiprocessing, depending on the user configuration.
        '''

        # Running under MPI
        #------------------
        if self.use_mpi:

            # Synchronize in the beginning
            assert self.size == len(self.modules) + 1,\
                'Incorrect number of processes (Required %r, got %r)'%\
                (len(self.modules) + 1, self.size)
            self.comm.Barrier()

            # Assign an mpi rank to all ports of a module using the module list index
            for m in self.modules:
                rank = self.modules.index(m)+1
                for port in m.ports:
                    port.rank = rank

            # Assign a unique port id to all ports
            i = 0
            for mod in self.modules:
                for port in mod.ports:
                    port.use_mpi = self.use_mpi
                    port.id = i
                    i += 1

            # Parallel run module in MPI
            if self.rank != 0:
                mod = self.modules[self.rank-1]
                self.log.info('Launching Module {}'.format(mod))
                mod.run()

            # Synchronize at the end
            self.comm.Barrier()

            # Collect at the root process all state data from modules
            if self.rank == 0:
                state = None
            else:
                state = self.modules[self.rank-1].state

            modules_state = self.comm.gather( state, root=0 )

            if self.rank == 0:
                for i in range(self.size-1):
                    self.modules[i].state = modules_state[i+1]

        # Running under Python multiprocessing
        #-------------------------------------
        else:

            # Parallel run all modules in Python multiprocessing
            processes = list()

            modules_new_state = Queue() # for sharing data with master process if used

            count_mods_status_attr = 0
            for mod in self.modules:
                self.log.info('Launching Module {}'.format(mod))
                if mod.state: # if not None pass arguments for user: run(self,*args)
                    p = Process( target=mod.run,
                            args=( self.modules.index(mod), modules_new_state ) )
                    count_mods_status_attr += 1
                else: # if None pass no arguments for user: run(self)
                    p = Process( target=mod.run )
                processes.append(p)
                p.start()

            for i in range(count_mods_status_attr):
                (mod_idx, new_state) = modules_new_state.get()
                self.modules[mod_idx].state = new_state
                self.log.info('Module {} getting new state'.format(self.modules[mod_idx]))

            # Synchronize at the end
            for p in processes:
                p.join()

        # Record time at the end of the run method
        if self.rank == 0 or not self.use_mpi:
            self.end_run_date = datetime.datetime.today().strftime('%d%b%y %H:%M:%S')
            self.wall_clock_time_end = time.time()

        return

    def get_network(self):
        '''Constructs and returns a the module network.

        Returns a networkx MultiGraph representation of the module network.

        Returns
        -------
        g: networkx.classes.multigraph.MultiGraph
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
                                    if id(port.connected_port) == id(p2):
                                        mod_two_name = "{}_{}".format(mod_two.__class__.__name__, self.modules.index(mod_two))
                                        if mod_two_name not in g or mod_one_name not in g.neighbors(mod_two_name):
                                            g.add_edge(mod_one_name, mod_two_name)
                self.nx_graph = g
            return self.nx_graph

    def draw_network(self, file_name='network.png', dpi=220):
        '''Draws the networkx Module network graph to an image

        Parameters
        ----------
        file_name: str, optional
            The resulting network diagram output file name
        dpi: int, optional
            dpi used for generating the network image

        '''

        if not self.use_mpi or self.rank == 0:
            g = self.nx_graph if self.nx_graph else self.get_network()
            colors = ['blue', 'red', 'green', 'pink', 'orange', 'brown', 'cyan']
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

    def close(self):
        '''Closes the cortix object properly before destruction.

        User is advised to call this method at the end of the run file.
        '''

        if self.rank == 0 or self.use_multiprocessing:

            if self.splash:
                self.log.info('Closed Cortix object on '+self.end_run_date+
                        self.__get_splash(end=True))
            else:
                self.log.info('Closed Cortix object on '+self.end_run_date)

            self.log.info('Elapsed wall clock time [s]: '+
                    str(round(self.wall_clock_time_end-self.wall_clock_time_start,2)))
        return

    def __create_logger(self):
        '''A helper function to setup the logging facility.'''

        # File removal
        if self.rank == 0 or self.use_multiprocessing:
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

        return

    def __get_splash(self, begin=None, end=None):
        '''Returns the Cortix splash logo.

        Note
        ----
        Call this internal method with one argument only. Either `begin=True` or
        `end=True`.

        Parameters
        ----------
        begin: bool
            True for the beginning message, false for the ending.

        Returns
        -------
        splash: str
            The Cortix splash logo.
        '''

        assert begin==None or end==None
        if begin:
            end=False
        elif end:
            begin=False


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

    def __del__(self):
        '''Destructs a Cortix simulation object.

        Warning
        -------
        By the time the body of this function is executed, the machinery of
        variables may have been deleted already. For example, `logging` is no longer
        there; do the least amount of work here.
        '''

        pass

if __name__ == '__main__':
    c = Cortix()
