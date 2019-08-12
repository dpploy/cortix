#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import logging
from multiprocessing import Process, Queue

from cortix.src.module import Module
from cortix.src.port import Port

class Network:
    '''Cortix network.

    Attributes
    ----------

    n_networks: int
        Number of instances of this class.

    '''

    n_networks = 0

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

        self.id = Network.n_networks

        self.name = 'network-'+str(self.id)
        self.log = logging.getLogger('cortix')

        self.max_n_modules_for_data_copy_on_root = 1000

        self.modules = list()

        self.gv_edges = list()

        self.use_mpi = None
        self.use_multiprocessing = None

        Network.n_networks += 1

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

    def connect(self, module_port_a, module_port_b, info=None):
        '''Connect two modules using either their ports directly or inferred ports.

        A connection always opens a channel for data communication in both ways.
        That is both sends and receives are allowed.

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
            assert isinstance(info,str)

        if isinstance(module_port_a, Module) and isinstance(module_port_b, Module):

            module_a = module_port_a
            module_b = module_port_b

            assert module_a.name and module_b.name  # sanity check

            assert module_a in self.modules,'module %r not in network.'%module_a.name
            assert module_b in self.modules,'module %r not in network.'%module_b.name

            idx_a = self.modules.index(module_a)
            idx_b = self.modules.index(module_b)
            self.gv_edges.append( (str(idx_a),str(idx_b)) )

            if info=='bidirectional':
                self.gv_edges.append( (str(idx_b),str(idx_a)) )

            port_a = module_a.get_port(module_b_name.lower())
            port_b = module_b.get_port(module_a_name.lower())

            port_a.connect(port_b)

        elif isinstance(module_port_a, list) and isinstance(module_port_b, list):

            assert len(module_port_a) == 2 and isinstance(module_port_a[0],Module) and\
                  (isinstance(module_port_a[1],str) or isinstance(module_port_a[1],Port))

            assert len(module_port_b) == 2 and isinstance(module_port_b[0],Module) and\
                  (isinstance(module_port_b[1],str) or isinstance(module_port_b[1],Port))

            module_a = module_port_a[0]
            module_b = module_port_b[0]

            assert module_a.name and module_b.name  # sanity check

            assert module_a in self.modules,'module %r not in network.'%module_a.name
            assert module_b in self.modules,'module %r not in network.'%module_b.name

            idx_a = self.modules.index(module_a)
            idx_b = self.modules.index(module_b)
            self.gv_edges.append( (str(idx_a),str(idx_b)) )

            if info=='bidirectional':
                self.gv_edges.append( (str(idx_b),str(idx_a)) )

            if isinstance(module_port_a[1],str):
                port_a = module_a.get_port(module_port_a[1])
            elif isinstance(module_port_a[1],Port):
                port_a = module_port_a[1]
            else:
                assert False, 'help!'

            if isinstance(module_port_b[1],str):
                port_b = module_b.get_port(module_port_b[1])
            elif isinstance(module_port_b[1],Port):
                port_b = module_port_b[1]
            else:
                assert False, 'help!'

            port_a.connect(port_b)

        else:
            assert False,' not implemented.'

        return

    def run(self):
        '''Run the network simulation.

        This function concurrently executes the `cortix.src.module.run` function
        for each module in the network. Modules are run using either MPI or
        Multiprocessing, depending on the user configuration.

        Note
        ----
        When using multiprocessing, data from the modules state are copied to the master
        process after the `run()` method of the modules is finished. When running in MPI,
        this is not done here. Only if the `get_modules()` method is called by all
        processes.

        '''
        assert len(self.modules) >= 1, 'the network must have a list of modules.'

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

            # Sync here at the end
            self.comm.Barrier()

            if len(self.modules) > self.max_n_modules_for_data_copy_on_root:
                return

            # TODO: monitor memory usage by the root process
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

            # TODO: verify limit of memory by the master process 
            modules_new_state = Queue() # for sharing data with master process if used

            count_states = 0
            for mod in self.modules:
                self.log.info('Launching Module {}'.format(mod))
                if mod.state: # if not None pass arguments for user: run(self,*args)
                    p = Process( target=mod.run,
                            args=( self.modules.index(mod), modules_new_state ) )
                    count_states += 1
                else: # if None pass no arguments for user: run(self)
                    p = Process( target=mod.run )
                processes.append(p)
                p.start()

            for i in range(count_states):
                (mod_idx, new_state) = modules_new_state.get()
                self.modules[mod_idx].state = new_state
                self.log.info('Module {} getting new state'.format(
                    self.modules[mod_idx]))

            # Synchronize at the end
            for p in processes:
                p.join()

        return

    def draw(self, graph_attr=None, node_attr=None, engine=None):

        from graphviz import Digraph

        use_graph_attr = {'splines':'true','overlap':'scale','ranksep':'1.5'}
        if graph_attr:
            use_graph_attr.update(graph_attr)

        use_node_attr = {'shape':'hexagon','style':'filled'}
        if node_attr:
            use_node_attr.update(node_attr)

        use_engine = 'twopi'
        if engine:
            use_engine = engine

        g = Digraph( name=self.name,comment='Network::graphviz',format='png',
                       graph_attr=use_graph_attr,node_attr=use_node_attr,
                       engine=use_engine )

        for m in self.modules:
            idx = self.modules.index(m)
            g.node(str(idx), m.name)

        for e in self.gv_edges:
            g.edge( e[0], e[1] )

        g.render()
