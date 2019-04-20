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

def run(task_name=None):
    '''
    Run the Cortix Droplet example in a Jupyter Notebook for the following tasks:
     1. solo-droplet
     2. solo-pyplot
     3. droplet-fall

    In a Jupyter Notebook cell enter:
   `    import cortix.examples.main.main_droplet as droplet
        droplet.run(`task_name`)
    '''
    pwd = os.path.dirname(__file__)
    full_path_config_file = os.path.join(pwd, '../input/cortix-config-droplet.xml')
    cortix = Cortix('cortix-droplet', full_path_config_file)

    assert task_name == 'droplet-fall' or task_name == 'solo-droplet' or\
            task_name == 'solo-pyplot','FATAL: task name %r invalid.'%task_name

    cortix.run_simulations(task_name=task_name)

    return cortix.simulations

#*********************************************************************************
if __name__ == "__main__":
    run()
