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
Cortix: a program for system-level modules coupling, execution, and analysis.
'''
#*********************************************************************************
import os
from cortix import Cortix
#*********************************************************************************

def run():
    '''
    Run the Cortix Droplet example. If Cortix and its dependencies are installed,
    this program should be executed at the command prompt inside the directory
    this program resides, namely, cortix/cortix/example/console_run/ directory.
    At the end of execution a directory with all logging and outputs is left in the
    work directory, as specified in the cortix-config-droplet.xml file. In this case,
    /tmp/cortix-droplet-wrk/.
    '''

    pwd = os.path.dirname(__file__)
    full_path_config_file = os.path.join(pwd, '../input/cortix-config-droplet.xml')

    # Create the cortix object and name it so it matches the <name></name> element
    # in the XML config file.
    cortix = Cortix('cortix-droplet', full_path_config_file)

    # This is a test of the droplet module alone and it needs no input.
    cortix.run_simulations(task_name="solo-droplet")

    # This is a test of the pyplot module alone: it needs an input file: state.xml which
    # is provided in ../input/. The input file ../input/pyplot.input points to this
    # file at runtime. 
    cortix.run_simulations(task_name="solo-pyplot")

    # This is a test of the droplet and pyplot connected.
    cortix.run_simulations(task_name="droplet-fall")

    # WARNING: the tasks are interferring with each other and threads are left running.
    # note how the droplet-fall runs two droplet instances...FIX ME.

#*********************************************************************************
if __name__ == "__main__":
    run()
