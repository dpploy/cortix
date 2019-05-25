#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/cortix/blob/master/COPYRIGHT.txt
#
# Licensed under the University of Massachusetts Lowell LICENSE:
# https://github.com/dpploy/cortix/blob/master/LICENSE.txt
'''
Simulation class of Cortix.

Cortix: a program for system-level modules coupling, execution, and analysis.
'''
#*********************************************************************************
import os
import logging
import datetime
from cortix.src.utils.xmltree       import XMLTree
from cortix.src.utils.set_logger_level import set_logger_level

from cortix.src.task        import Task
from cortix.src.application import Application
#*********************************************************************************

class Simulation:
    '''
    Cortix Simulation element as defined in the Cortix configuration.
    Simulation class members:

    __name: str
        Name of the simulation.

    __work_dir: str
       Work directory for files pertaining to the simulation.

    '''

#*********************************************************************************
# Construction 
#*********************************************************************************

    def __init__(self, parent_work_dir, config_xml_tree):

        # Sanity checks
        assert isinstance(parent_work_dir, str),\
                'ctx::sim parent_work_dir invalid.'
        assert isinstance(config_xml_tree, XMLTree),\
                'ctx::sim config_xml_tree invalid.'
        assert config_xml_tree.tag == 'simulation',\
                'ctx:sim: invalid simulation xml node tag.'

        # Read the simulation name, e.g. <simulation name='droplet'></simulation>
        self.__name = config_xml_tree.get_attribute('name')

        # Create the cortix/simulation work directory
        self.__work_dir = parent_work_dir + 'sim_' + self.__name + '/'
        os.system('mkdir -p ' + self.__work_dir)

        # Create the logging facility 
        self.__create_logging( config_xml_tree )
        self.__log.debug('start __init__()')

        #======================
        # Create application(s)
        #======================
        for app_config_xml_node in config_xml_tree.get_all_sub_nodes('application'):

            assert app_config_xml_node.tag == 'application'

            # Create the application for this simulation (same work directory)
            self.__application = Application( self.__work_dir, app_config_xml_node )

            self.__log.debug('created application: %s',
                    app_config_xml_node.get_attribute('name'))

        # Stores the task(s) created by the execute method
        self.__tasks = list() # not needed now; in the future for task parallelism

        # Save configuration information for setting up task in execute()
        self.__config_xml = config_xml_tree

        self.__log.info('created simulation: %s', self.__name)

        return

    def __del__(self):

        self.__log.info("destroyed simulation: %s", self.__name)

        return

#*********************************************************************************
# Public member functions
#*********************************************************************************

    def __get_application(self):
        '''
        Returns the application singleton object.

        Parameters
        ----------
        empty:

        Returns
        -------
        self.__application: Application
        '''

        return self.__application

    application = property(__get_application,None,None,None)

    def __get_tasks(self):
        '''
        Returns the application tasks object.
        Many tasks can be scheduled for a given application.

        Parameters
        ----------
        empty:

        Returns
        -------
        self.__tasks: Task
        '''

        return self.__tasks

    tasks = property(__get_tasks,None,None,None)

    def execute(self, task_name=None):
        '''
        This method allows for the execution of a simulation by executing each
        task, if any. Execution proceeds one task at a time.
        '''

        self.__log.debug("prepare to execute(%s)", task_name)

        if task_name is not None:

            # Create the task object for each task
            self.__setup_task( task_name )

            for task in self.__tasks:

                if task.name == task_name:

                    self.__log.debug("call execute(%s)", task_name)

                    task.execute(self.__application)

                    self.__log.debug(
                        'called task.execute() on task %s', task_name)

        self.__log.debug("end execute(%s)", task_name)

        return

    def __str__(self):
        '''
        Simulation to string conversion used in a print statement.
        '''

        s = 'Simulation data members:\n \t name=%s\n \t work dir=%s\n \t application=%s\n \t tasks=%s'
        return s % (self.__name, self.__work_dir, self.__application,
                    self.__tasks)

    def __repr__(self):
        '''
        Simulation to string conversion.
        '''

        s = 'Simulation data members:\n \t name=%s\n \t work dir=%s\n \t application=%s\n \t tasks=%s'
        return s % (self.__name, self.__work_dir, self.__application,
                    self.__tasks)

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

    def __create_logging( self, config_xml_tree ):
        '''
        A helper function to setup the logging facility used in self.__init__()
        '''

        logger_name = 'sim:' + self.__name

        self.__log = logging.getLogger(logger_name)
        self.__log.setLevel(logging.NOTSET)

        node = config_xml_tree.get_sub_node('logger')

        logger_level = node.get_attribute('level')
        self.__log = set_logger_level(self.__log, logger_name, logger_level)

        file_handler = logging.FileHandler(self.__work_dir + 'sim.log')
        file_handler.setLevel(logging.NOTSET)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.NOTSET)

        for child in node.children:
            (elem,tag,attributes,text) = child
            elem = XMLTree( elem ) # fixme: remove wrapping
            if tag == 'file_handler':
                file_handler_level = elem.get_attribute('level')
                file_handler = set_logger_level(file_handler, logger_name,
                                                file_handler_level)

            if tag == 'console_handler':
                console_handler_level = elem.get_attribute('level')
                console_handler = set_logger_level(console_handler, logger_name,
                                                   console_handler_level)

        # formatter added to handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # add handlers to logger
        self.__log.addHandler(file_handler)
        self.__log.addHandler(console_handler)

        self.__log.info('created Simulation logger: %s', self.__name)
        self.__log.debug('logger level: %s', logger_level)
        self.__log.debug('logger file handler level: %s', file_handler_level)
        self.__log.debug('logger console handler level: %s', console_handler_level)

        return

    def __setup_task(self, task_name):
        '''
        This is a helper function used by the execute() method. It creates a
        Task object and sets up the communication file for the task at hand.
        There must be only one nework for this task and this network will be
        used to generate the communication file for each module where the ports
        will point to files. Each module will have in its runtime directory, an
        XML file which maps a port name and type to a file. If the port type is a
        provide type, the file pointed to resides on the same directory as the
        communication file. If the port type is a use type, the file pointed to
        resides in the directory of the module whose corresponding provide port is
        connected to. The communication XML file contains a root tag
        <cortix_comm>, and a series of XML port tags with three attributes and no
        content as follows:

            <port name=port_name type=port_type file=full_path_file_name />

        '''

        self.__log.debug('start __setup_task(%s)', task_name)

        task = None  # initialize the task object

        # loop over all elements with a <task></task> tag in this simulation 
        for task_config_xml_node in self.__config_xml.get_all_sub_nodes('task'):

            if task_config_xml_node.get_attribute('name') != task_name:
                continue

            # create task
            task = Task( self.__work_dir, task_config_xml_node )

            self.__tasks.append(task)

            self.__log.debug('appended task: %s', \
                    task_config_xml_node.get_attribute('name'))

        if task is None:
            self.__log.info('no task to exectute; done here.')
            self.__log.info('end __setup_task(%s)', task_name)
            return

        # create subdirectory with task name
        task_name = task.name
        task_work_dir = task.work_dir
        assert os.path.isdir(task_work_dir), 'directory %r invalid.' % task_work_dir

        # set the parameters for the task in the cortix param file
        task_file = task_work_dir + 'cortix-param.xml'

        fout = open(task_file, 'w')
        fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        fout.write('<!-- Written by Simulation::__setup_task() -->\n')
        today = datetime.datetime.today()
        fout.write('<!-- ' + str(today) + ' -->\n')

        fout.write('<cortix_param>\n')

        start_time = task.start_time
        start_time_unit = task.start_time_unit
        fout.write('<start_time unit="' + start_time_unit + '"' + '>' +
                           str(start_time) + '</start_time>\n')

        evolve_time = task.evolve_time
        evolve_time_unit = task.evolve_time_unit
        fout.write('<evolve_time unit="' + evolve_time_unit + '"' + '>' +
                           str(evolve_time) + '</evolve_time>\n')

        time_step = task.time_step
        time_step_unit = task.time_step_unit
        fout.write('<time_step unit="' + time_step_unit + '"' + '>' +
                           str(time_step) + '</time_step>\n')

        real_time = task.real_time
        fout.write('<real_time>' + real_time + '</real_time>\n')

        fout.write('</cortix_param>')
        fout.close()

        task.runtime_cortix_param_file = task_file

        # Using the task and network objects create the runtime module directories and 
        # cortix comm files; one comm file per module inside the module runtime directory

        networks = self.__application.networks

        for net in networks:

            if net.name != task_name:
                s = '__setup_task():: net name: ' + \
                    net.name + ' not equal to task name: ' + task_name + '; ignored.'
                self.__log.warn(s)
                continue

            elif net.name == task_name:  # net and task names must match

                connect = net.connectivity
                to_module_to_port_visited = dict() # providers

                for con in connect:

                    #==========================================================
                    # start with the ports that will function as a provide port 
                    #==========================================================
                    provide_module_slot = con['provide_module_slot']
                    provide_port = con['provide_port']

                    if provide_module_slot not in to_module_to_port_visited.keys():
                        to_module_to_port_visited[provide_module_slot] = list()

                    provide_module_name = provide_module_slot.rsplit('_',1)[0]
                    provide_module = self.__application.get_module(provide_module_name)

                    assert provide_module is not None, \
                        'module %r does not exist in application'%provide_module_name

                    assert provide_module.has_port_name(provide_port),\
                            'network %r, module %r has no port %r.'%\
                            (net.name, provide_module.name, provide_port)

                    assert provide_module.get_port_type(provide_port) is not None,\
                        'network name: %r, module name: %r, provide port: %r port type \
                    invalid %r' % (net.name, provide_module.name, provide_port,
                                   type(provide_module.get_port_type(provide_port)))

                    provide_module_slot_work_dir = task_work_dir+provide_module_slot+'/'

                    assert provide_module.get_port_type(provide_port) == 'provide',\
                            'port type %r invalid. Module %r, port %r'%\
                            (provide_module.get_port_type(provide_port),
                                    provide_module.name, provide_port)

                    provide_module_slot_comm_file = provide_module_slot_work_dir + \
                        'cortix-comm.xml'

                    if not os.path.isdir(provide_module_slot_work_dir):
                        os.system('mkdir -p ' + provide_module_slot_work_dir)

                    if not os.path.isfile(provide_module_slot_comm_file):
                        fout = open(provide_module_slot_comm_file,'w')
                        fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                        fout.write('<!-- Written by Simulation::__setup_task() -->\n')
                        today = datetime.datetime.today()
                        fout.write('<!-- ' + str(today) + ' -->\n')
                        fout.write('<cortix_comm>\n')

                    # a provide module/port only writes once no matter how many times it
                    # is used
                    if provide_port not in to_module_to_port_visited[provide_module_slot]:
                        fout = open(provide_module_slot_comm_file,'a')
                        # this is the cortix info for modules providing data
                        provide_port_mode = provide_module.get_port_mode(provide_port)
                        if provide_port_mode.split('.')[0] == 'file':
                            ext = provide_port_mode.split('.')[1]
                            log_str = '<port name="' + provide_port + \
                                    '" type="provide" file="' + \
                                    provide_module_slot_work_dir\
                                    + provide_port + '.' + ext + '"/>\n'
                        elif provide_port_mode == 'directory':
                            log_str = '<port name="' + provide_port + \
                                    '" type="provide" directory="' + \
                                    provide_module_slot_work_dir + provide_port + '"/>\n'
                        elif provide_port_mode == 'hardware':
                            log_str = '<port name="' + provide_port + \
                                    '" type="provide" hardware="' + \
                                    provide_module_slot_work_dir + provide_port + '"/>\n'
                        else:
                            assert False, 'invalid port mode. fatal.'

                        fout.write(log_str)
                        fout.close()

                        to_module_to_port_visited[provide_module_slot].append(
                            provide_port)

                    debug_str = '__setup_task():: comm module: ' + provide_module_slot + \
                                '; network: ' + task_name + ' ' + log_str
                    self.__log.debug(debug_str)

                    # register the cortix-comm file for the network
                    net.set_runtime_cortix_comm_file_name( provide_module_slot,
                        provide_module_slot_comm_file )

                    #=================================================
                    # now do the ports that will function as use ports 
                    #=================================================
                    use_module_slot = con['use_module_slot']
                    use_port = con['use_port']
                    use_module_name = '_'.join( use_module_slot.split('_')[:-1] )
                    use_module = self.__application.get_module(use_module_name)

                    assert use_module.has_port_name(use_port),\
                            'module %r has no port %r'%(use_module_name, use_port)

                    assert use_module.get_port_type(use_port) is not None,\
                            'network name: %r, module name: %r, use_port: %r port type\
                            invalid %r'%\
                            (net.name, use_module.name, use_port,
                                    type(use_module.get_port_type(use_port)))

                    use_module_slot_work_dir = task_work_dir + use_module_slot + '/'

                    assert use_module.get_port_type(use_port) == 'use',\
                            'port type %r invalid. Module %r, port %r'%\
                            (use_module.get_port_type(use_port), use_module.name,
                                    use_port)

                    use_module_slot_comm_file = use_module_slot_work_dir+'cortix-comm.xml'

                    if not os.path.isdir(use_module_slot_work_dir):
                        os.system('mkdir -p ' + use_module_slot_work_dir)

                    if not os.path.isfile(use_module_slot_comm_file):
                        fout = open(use_module_slot_comm_file,'w')
                        fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                        fout.write('<!-- Written by Simulation::__setup_task() -->\n')
                        today = datetime.datetime.today()
                        fout.write('<!-- ' + str(today) + ' -->\n')
                        fout.write('<cortix_comm>\n')
                        fout.close() # is this right?

                    fout = open(use_module_slot_comm_file,'a')

                    # this is the cortix info for modules using data
                    assert use_module.get_port_type(use_port) == 'use',\
                            'use_port must be use type.'

                    provide_port_mode = provide_module.get_port_mode(provide_port)
                    if provide_port_mode.split('.')[0] == 'file':
                            ext = provide_port_mode.split('.')[1]
                            log_str = '<port name="' + use_port + \
                                      '" type="use" file="' + \
                                      provide_module_slot_work_dir + provide_port + \
                                      '.' + ext + '"/>\n'
                    elif provide_port_mode == 'directory':
                            log_str = '<port name="' + use_port +\
                                    '" type="use" directory="' +\
                                    provide_module_slot_work_dir + provide_port + '"/>\n'
                    elif provide_port_mode == 'hardware':
                            log_str = '<port name="' + use_port +\
                                    '" type="use" directory="' +\
                                    provide_module_slot_work_dir +\
                                    provide_port + '"/>\n'
                    else:
                            assert False, 'invalid port mode. fatal.'

                    fout.write(log_str)
                    fout.close()

                    debug_str = '__setup_task():: comm module: ' + use_module_slot\
                            + '; network: ' + task_name + ' ' + log_str
                    self.__log.debug(debug_str)

                # register the cortix-comm file for the network
                net.set_runtime_cortix_comm_file_name( use_module_slot,
                        use_module_slot_comm_file )

            #end elif net.name.strip() == task_name.strip():  # net and task names must match
            else:
                assert False, 'this should not happen...'

        #end for net in networks:

        # Now finish forming the XML comm file for each module in each network
        for net in networks:
            for slot_name in net.module_slot_names:
                comm_file = net.get_runtime_cortix_comm_file_name(slot_name)
                if comm_file == 'null-runtime_cortix_comm_file_name':
                    if net.name != task_name:
                       s = '__setup_task():: comm file for ' + slot_name + \
                           ' in network ' + net.name + ' is ' + comm_file
                       self.__log.warn(s)
                       continue
                    else:
                       assert False, 'FATAL ERROR building the comm file for module %r'%\
                                    slot_name
                else:
                    fout = open(comm_file, 'a')
                    fout.write('</cortix_comm>')
                    fout.close()

        self.__log.debug('end __setup_task(%s)', task_name)

        return

#======================= end class Simulation: ===================================
