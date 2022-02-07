#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import os
import shutil
import pickle
import logging
from multiprocessing import Process

from cortix.src.module import Module
from cortix.src.port import Port

class Network:
    """Cortix network.

    Attributes
    ----------

    num_networks: int
        Number of instances of this class.

    """

    num_networks = 0

    def __init__(self):
        '''Module super class constructor.

        Attributes
        ----------
          max_n_modules_for_data_copy_on_root: int
              When using MPI the `network` will copy the data from all modules on the
              root process. This can generate an `out of memory` condition. This variable
              sets the maximum number of processes for which the data will be copied.
              Default is 1000.

       '''

        self.id = Network.num_networks

        self.name = 'network-'+str(self.id)
        self.log = logging.getLogger('cortix')

        self.max_n_modules_for_data_copy_on_root = 1000

        self.modules = list()

        self.gv_edges = list()

        self.use_mpi = None
        self.use_multiprocessing = None

        self.rank = None
        self.size = None
        self.comm = None

        self.save = False # save all network modules

        Network.num_networks += 1

        return

    def module(self, m):
        '''Add a module.

        '''

        assert isinstance(m, Module), 'm must be a module'

        name = m.name
        if not name:
            name = m.__class__.__name__

        if m not in self.modules:
            m.use_mpi = self.use_mpi
            m.use_multiprocessing = self.use_multiprocessing
            self.modules.append(m)
            m.id = len(self.modules)-1  # see module doc for module id

        return

    def add_module(self, m):
        '''Alternative name to `module()`.

        '''

        self.module(m)

        return

    def connect(self, module_port_a, module_port_b, info=None):
        '''Connect two modules using either their ports directly or inferred ports.

        A connection always opens a channel for data communication in both ways.
        That is, both sends and receives are allowed.

        Note
        ----
        The simplest form of usage is with arguments: (`module_a`, `module_b`).
        In this case, a `port` with the name of `module_a` **must** exist in `module_b`,
        and vice-versa (port names as `str` in lower case). In addition, the connect
        must not be called again with these same two modules, else the underlying
        connection will be overriden.

        For more rigorous connection, the user is advised to fully specify the
        module and the port in each list argument.

        Parameters
        ----------
        module_port_a: list([Module,Port]) or list([Module,str]) or Module
            First `module`-`port` to connect.

        module_port_b: list([Module,Port]) or list([Module,str]) or Module
            Second `module`-`port` to connect.

        info: str
            Information on the directionality of the information flow. This is for
            graph visualization purposes only. The default value will use the order
            in the argument list to define the direction. Default: None. If set
            to `bidiretional`, will create a double headed arrow in the graph figure.

        '''

        if info:
            assert isinstance(info, str)

        if isinstance(module_port_a, Module) and isinstance(module_port_b, Module):

            module_a = module_port_a
            module_b = module_port_b

            assert module_a.name and module_b.name  # sanity check

            assert module_a in self.modules, 'module %r not in network.'%module_a.name
            assert module_b in self.modules, 'module %r not in network.'%module_b.name

            # Connect ports
            port_a = module_a.get_port(module_b.name.lower())
            port_b = module_b.get_port(module_a.name.lower())

            port_a.connect(port_b)

            # Record connectivity for graph viz.
            idx_a = self.modules.index(module_a)
            idx_b = self.modules.index(module_b)

            if (str(idx_a), str(idx_b)) not in self.gv_edges:
                self.gv_edges.append((str(idx_a), str(idx_b)))

                if info == 'bidirectional' and (str(idx_b), str(idx_a)) not in self.gv_edges:
                    self.gv_edges.append((str(idx_b), str(idx_a)))

        elif isinstance(module_port_a, list) and isinstance(module_port_b, list):

            assert len(module_port_a) == 2 and isinstance(module_port_a[0], Module) and\
                  (isinstance(module_port_a[1], str) or isinstance(module_port_a[1], Port))

            assert len(module_port_b) == 2 and isinstance(module_port_b[0], Module) and\
                  (isinstance(module_port_b[1], str) or isinstance(module_port_b[1], Port))

            module_a = module_port_a[0]
            module_b = module_port_b[0]

            assert module_a.name and module_b.name  # sanity check

            assert module_a in self.modules, 'module %r not in network.'%module_a.name
            assert module_b in self.modules, 'module %r not in network.'%module_b.name

            idx_a = self.modules.index(module_a)
            idx_b = self.modules.index(module_b)

            self.gv_edges.append((str(idx_a), str(idx_b)))

            if info == 'bidirectional':
                self.gv_edges.append((str(idx_b), str(idx_a)))

            if isinstance(module_port_a[1], str):
                port_a = module_a.get_port(module_port_a[1])
            elif isinstance(module_port_a[1], Port):
                port_a = module_port_a[1]
            else:
                assert False, 'help!'

            if isinstance(module_port_b[1], str):
                port_b = module_b.get_port(module_port_b[1])
            elif isinstance(module_port_b[1], Port):
                port_b = module_port_b[1]
            else:
                assert False, 'help!'

            port_a.connect(port_b)

        else:
            assert False, ' not implemented.'

        return

    def __run(self, save=False):
        """
        Internal method to run the network simulation. Do not use this method, it is
        intended for Cortix to run it.

        This function concurrently executes the `cortix.src.module.run` function
        for each module in the network. Modules are run using either MPI or
        Multiprocessing, depending on the user configuration.

        Note
        ----
        When using multiprocessing, data from the modules state are copied to the master
        process after the `__run()` method of the modules is finished.

        """
        assert len(self.modules) >= 1, 'the network must have a list of modules.'

        # Create directory for saving modules states
        if self.rank == 0 or self.use_multiprocessing:
            shutil.rmtree('.ctx-saved', ignore_errors=True)
            os.makedirs('.ctx-saved')

        # Running under MPI
        #------------------
        if self.use_mpi:

            # Synchronize in the beginning
            assert self.size == len(self.modules) + 1,\
                'Incorrect number of processes (Required %r, got %r)'%\
                (len(self.modules) + 1, self.size)
            self.comm.Barrier()

            # Assign an mpi rank to all ports of a module using the module list index
            # If a port has rank assignment from a previous run; leave it alone
            for mod in self.modules:
                rank = self.modules.index(mod)+1
                for port in mod.ports:
                    if port.rank is None:
                        port.rank = rank

            # Assign a unique port id to all ports
            # If a port has id assignment from a previous run; leave it alone
            i = 0
            for mod in self.modules:
                for port in mod.ports:
                    port.use_mpi = self.use_mpi
                    if port.id is None:
                        port.id = i
                        i += 1

            # Parallel run module in MPI
            if self.rank != 0:
                mod = self.modules[self.rank-1]
                self.log.info('Launching Module {}'.format(mod))
                mod.run_and_save()

            # Sync here at the end
            self.comm.Barrier()

        # Running under Python multiprocessing
        #-------------------------------------
        else:

            # Parallel run all modules in Python multiprocessing
            processes = list()

            for mod in self.modules:
                self.log.info('Launching Module {}'.format(mod))
                proc = Process(target=mod.run_and_save)
                processes.append(proc)
                proc.start()

            # Synchronize at the end
            for proc in processes:
                proc.join()

        # Reload saved modules
        #---------------------
        if self.use_mpi:
            # make double sure all processes are in sync here before reading files
            # from disk
            self.comm.Barrier()

        num_files = 0
        for file_name in os.listdir('.ctx-saved'):

            self.gv_edges = list() # re-initialize since ports were not pickled

            if file_name.endswith('.pkl'):
                num_files += 1
                file_name = os.path.join('.ctx-saved', file_name)
                with open(file_name, 'rb') as fin:
                    module = pickle.load(fin)
                    # reintroduce logging
                    module.log = logging.getLogger('cortix')
                    self.modules[module.id] = module

        if num_files and num_files != len(self.modules):
            self.log.warning('Network::run(): not all modules reloaded from disk.')

        if self.use_mpi:
            # Make double sure all are in sync here before going forward
            # this solves the problem of processes running behind reading files
            # that do not exist anymore
            self.comm.Barrier()

    def draw(self, graph_attr=None, node_attr=None, engine='twopi', lr=False,
             size=None, ports=False, node_shape='hexagon'):
        """Build a `graphviz` graph and draw the network saving it to a file.

        Parameters
        ----------
        graph_attr: dict(str:str)
            Graph attributes per GraphViz library. Use a dictionary of key:value
            strings.

        node_attr: dict(str:str)
            Node attributes per GraphViz library. Use a dictionary of key:value
            strings.

        engine: str
            Name of drawing engine (from GraphViz):
            'dot': draws directed graphs. It works well on directed acyclic graphs
                   and other graphs that can be drawn as hierarchies or have a natural
                   flow.

            'neato': draws  undirected  graphs  using  a  spring model  and reducing
                     the  related  energy.

            'twopi': draws graphs using a radial layout.  Basically,one node is
                     chosen as the center and put at the origin. The remaining nodes
                     are placed onasequence  of  concentric  circles  centered  about
                     the  origin,  each  a  fixed  radial  distance  from  the
                     previous circle.  Allnodes distance 1 from the center are placed
                     on the first circle; all nodes distance 1 from a nodeon the
                     first circle are placed on the second circle; and so forth.

            'circo': draws graphs using a circular layout. The tool identifies
                     biconnected components and draws the nodes of the component
                     on a circle. The block-cutpoint tree is then laid out using a
                     recursive radial algorithm. Edge crossings within acircle  are
                     minimized by placing as manyedges on the circle’s
                     perimeter as possible. In particular,ifthecomponent is
                     outer planar, the component will have a planar layout. If a node
                     belongs to multiple non-triv-ial biconnected components, the
                     layout puts the node in one of them. By default, this is the
                     first non-trivialcomponent found in the search from the root
                     component.

            'fdp': draws undirected graphs using a spring model. It relies on a
                   force-directed approach in the spirit of Fruchterman and Reingold.

            `sfdp` also  draws  undirected  graphs  using  the spring model described
                   above,but  it  uses  a  multi-scaleapproach to produce layouts of
                   large graphs in a reasonably short time.patchworkdraws the graph
                   as a squarified treemap. The clusters of the graph are used to
                   specify the tree.

            'osage' draws the graph using its cluster structure. For a givencluster,
                    each of its subclusters is laid out inter-nally.Then  the
                    subclusters, plus anyremaining  nodes, are repositioned based on
                    the  cluster’s

        lr: boolean
            True draws graph left to right. False draws top down.

        size: str
            Pair of integer numbers in a string: 'a,b'.

        ports: boolean
            Draw name of ports

        node_shape: str
            Select node shape to draw. Options:
            'box', 'polygon', 'ellipse', 'oval',
            'circle', 'point', 'egg', 'triangle',
            'plaintext', 'plain', 'diamond', 'trapezium',
            'parallelogram', 'house', 'pentagon', 'hexagon',
            'septagon', 'octagon', 'doublecircle', 'doubleoctagon',
            'tripleoctagon', 'invtriangle', 'invtrapezium', 'invhouse',
            'Mdiamod', 'Msquare', 'Mcircle', 'rect',
            'rectangle', 'square', 'star', 'none',
            'underline', 'cylinder', 'note', 'tab',
            'folder', 'box3d', 'component', 'promoter',
            'cds', 'terminator', 'utr', 'primersite',
            'restrictionsite', 'fivepoverhang', threepoverhang', 'noverhang',
            'rnastab', 'proteasesite', 'proteinstab', 'rpromoter',
            'rarrow', 'larrow', 'lpromoter'.

        """

        # Delete existing graph files if any.
        if os.path.isfile(self.name+'.gv'):
            os.remove(self.name+'.gv')
        if os.path.isfile(self.name+'.gv.png'):
            os.remove(self.name+'.gv.png')

        # Import here to avoid broken dependency. Only this method needs graphviz.
        from graphviz import Digraph

        if graph_attr is None:
            graph_attr = {'splines':'true', 'overlap':'scale', 'ranksep':'1.5'}

        if node_attr is None:
            node_attr = {'shape':node_shape, 'style':'filled'}

        dgr = Digraph(name=self.name, comment='Network::graphviz', format='png',
                      graph_attr=graph_attr, node_attr=node_attr, engine=engine)

        if lr:
          dgr.attr(rankdir="LR")

        if size:
          dgr.attr(size=size)

        #dgr.attr('node', shape=node_shape)

        for idx, mod in enumerate(self.modules):
            dgr.node(str(idx), mod.name)

        for edg in self.gv_edges:
            dgr.edge(edg[0], edg[1])

        dgr.render()

        return dgr
