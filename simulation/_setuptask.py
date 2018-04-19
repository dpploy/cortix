# -*- coding: utf-8 -*-

"""
This file defines the helper function setup_task which
is used in the Simulation constructor by the execute function
to setup the tasks defined in the Cortix config file.

Valmor F. de Almeida dealmeidav@ornl.gov; vfda
Cortix: a program for system-level modules
        coupling, execution, and analysis.
Tue Dec 10 11:21:30 EDT 2013
"""

#*********************************************************************************
import os
from cortix.utils.configtree import ConfigTree
from cortix.task._task import Task
#*********************************************************************************


#=============================BEGIN SETUP_TASK=====================================
def setup_task(self, task_name):
    """
    This is a helper function used by the execute function in
    the simulation to constructor. It server to setup the
    set of tasks defined in the Cortix config.
    """
    self.log.debug("start _SetupTask()")
    task = None

    for task_node in self.config_node.get_all_sub_nodes('task'):
        if task_node.get('name') != task_name:
            continue

        task_config_node = ConfigTree(task_node)
        task = Task(self.work_dir, task_config_node)
        self.tasks.append(task)

        self.log.debug("appended task: %s", task_node.get("name"))

    if task is None:
        self.log.debug('no task to exectute; done here.')
        self.log.debug('end setup_task')
        return

    networks = self.application.get_networks()

    # create subdirectory with task name
    task_name = task.get_name()
    task_work_dir = task.get_work_dir()
    assert os.path.isdir(task_work_dir), "directory %r invalid." % task_work_dir

    # set the parameters for the task in the cortix param file
    task_file = task_work_dir + 'cortix-param.xml'
    fout = open(task_file, 'w')
    fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    fout.write('<!-- Written by Simulation::_Setup() -->\n')
    fout.write('<cortixParam>\n')
    start_time = task.get_start_time()
    start_time_unit = task.get_start_time_unit()
    fout.write('<startTime unit="'+start_time_unit+'"'+'>'+str(start_time)+'</startTime>\n')
    evolve_time = task.get_evolve_time()
    evolve_time_unit = task.get_evolve_time_unit()
    fout.write('<evolveTime unit="'+evolve_time_unit+'"'+'>'+str(evolve_time)+'</evolveTime>\n')
    time_step = task.get_time_step()
    time_step_unit = task.get_time_step_unit()
    fout.write('<timeStep unit="'+time_step_unit+'"'+'>'+str(time_step)+'</timeStep>\n')
    fout.write('</cortixParam>')
    fout.close()
    task.set_runtime_cortix_param_file(task_file)

    # using the tasks and network create the runtime module directories and comm files
    for net in networks:
        if net.get_name() == task_name: # Warning: net and task name must match
            connect = net.get_connectivity()
            to_module_to_port_visited = dict()
            for con in connect:
                # Start with the ports that will function as a provide port or input port
                to_module_slot = con['toModuleSlot']
                to_port = con['toPort']

                if to_module_slot not in to_module_to_port_visited.keys():
                    to_module_to_port_visited[to_module_slot] = list()

                to_module_name = to_module_slot.split('_')[0]
                to_module = self.application.get_module(to_module_name)

                assert to_module is not None, \
                  'module %r does not exist in application' % to_module_name

                assert to_module.has_port_name(to_port), \
                  'module %r has no port %r.' % (to_module.get_name(), to_port)

                assert to_module.get_port_type(to_port) is not None,\
                  'network name: %r, module name: %r, to_port: %r port type invalid %r' %(\
                  net.get_name(), to_module.get_name(), to_port, type(to_module.get_port_type(to_port)))

                to_module_slot_work_dir = task_work_dir + to_module_slot + '/'

                if to_module.get_port_type(to_port) != 'input':
                    assert to_module.get_port_type(to_port) == 'provide', \
                      'port type %r invalid. Module %r, port %r' \
                      % (to_module.get_port_type(to_port), to_module.get_name(), to_port)

                # "to" is who receives the "call", hence the provider
                to_module_slot_comm_file = to_module_slot_work_dir + 'cortix-comm.xml'

                if not os.path.isdir(to_module_slot_work_dir):
                    os.system("mkdir -p " + to_module_slot_work_dir)

                if not os.path.isfile(to_module_slot_comm_file):
                    fout = open(to_module_slot_comm_file, 'w')
                    fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                    fout.write('<!-- Written by Simulation::_Setup() -->\n')
                    fout.write('<cortixComm>\n')

                if to_port not in to_module_to_port_visited[to_module_slot]:
                    fout = open(to_module_slot_comm_file, 'a')
                    # this is the cortix info for modules providing data
                    to_port_mode = to_module.get_port_mode(to_port)
                    if to_port_mode.split('.')[0] == 'file':
                        ext = to_port_mode.split('.')[1]
                        log_str = '<port name="'+to_port+'" type="provide" file="'\
                                               +to_module_slot_work_dir+to_port+'.'+ext+'"/>\n'
                    elif to_port_mode == 'directory':
                        log_str = '<port name="'+to_port+'" type="provide" directory="'+\
                                               to_module_slot_work_dir+to_port+'"/>\n'
                    else:
                        assert False, 'invalid port mode. fatal.'

                    fout.write(log_str)
                    fout.close()
                    to_module_to_port_visited[to_module_slot].append(to_port)

                debug_str = '_Setup():: comm module: ' + to_module_slot + '; network: '\
                            + task_name + ' ' + log_str
                self.log.debug(debug_str)

                # register the cortix-comm file for the network
                net.set_runtime_cortix_comm_file(to_module_slot, to_module_slot_comm_file)

                # Now do the ports that will function as use ports
                from_module_slot = con['fromModuleSlot']
                from_port = con['fromPort']
                from_module_name = from_module_slot.split('_')[0]
                from_module = self.application.get_module(from_module_name)

                assert from_module.has_port_name(from_port), 'module %r has no port %r'\
                  % (from_module_name, from_port)

                assert from_module.get_port_type(from_port) is not None, \
                  'network name: %r, module name: %r, from_port: %r port type invalid %r'\
                  % (net.get_name(), from_module.get_name(), from_port, \
                     type(from_module.get_port_type(from_port)))

                from_module_slot_work_dir = task_work_dir + from_module_slot + '/'

                if from_module.get_port_type(from_port) != 'output':
                    assert from_module.get_port_type(from_port) == 'use', \
                      'port type %r invalid. Module %r, port %r'\
                      % (from_module.get_port_type(from_port), from_module.get_name(), from_port)

                    # "from" is who makes the "call", hence the user
                    from_module_slot_comm_file = from_module_slot_work_dir + 'cortix-comm.xml'

                    if not os.path.isdir(from_module_slot_work_dir):
                        os.system('mkdir -p '+ from_module_slot_work_dir)

                    if not os.path.isfile(from_module_slot_comm_file):
                        fout = open(from_module_slot_comm_file, 'w')
                        fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                        fout.write('<!-- Written by Simulation::_Setup() -->\n')
                        fout.write('<cortixComm>\n')

                    fout = open(from_module_slot_comm_file, 'a')

                    # this is the cortix info for modules using data
                    assert from_module.get_port_type(from_port) == 'use', 'from_port must be use type.'

                    to_port_mode = to_module.get_port_mode(to_port)
                    if to_port_mode.split('.')[0] == 'file':
                        ext = to_port_mode.split('.')[1]
                        log_str = '<port name="' + from_port + '" type="use" file="' + \
                                  to_module_slot_work_dir + to_port +'.' + ext + '"/>\n'
                    elif to_port_mode == 'directory':
                        log_str = '<port name="' + from_port + '" type="use" directory="' + \
                                  to_module_slot_work_dir + to_port + '"/>\n'
                    else:
                        assert False, 'invalid port mode. fatal.'

                    fout.write(log_str)
                    fout.close()

                    debug_str = "_Setup():: comm module: " + from_module_slot + '; network: '\
                                + task_name + ' ' + log_str
                    self.log.debug(debug_str)

            # register the cortix-comm file for the network
            net.set_runtime_cortix_comm_file(from_module_slot, from_module_slot_comm_file)

    # finish forming the XML documents for port types
    for net in networks:
        slot_names = net.get_slot_names()
        for slot_name in slot_names:
            comm_file = net.get_runtime_cortix_comm_file(slot_name)
            if comm_file == 'null-runtimeCortixCommFile':
                continue
            fout = open(comm_file, 'a')
            fout.write('</cortixComm>')
            fout.close()

    self.log.debug('end _Setup()')

#======================================END SETUP_TASK==================================
