#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/cortix
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/cortix/blob/master/COPYRIGHT.txt
#
# Licensed under the GNU General Public License v. 3, please see LICENSE file.
# https://www.gnu.org/licenses/gpl-3.0.txt
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
    '''

    pwd = os.path.dirname(__file__)
    full_path_config_file = os.path.join(pwd, '../input/cortix-config-droplet.xml')
    cortix = Cortix('cortix-droplet', full_path_config_file)
    cortix.run_simulations(task_name="droplet-fall")
#---------------------- end def run():--------------------------------------------

#*********************************************************************************
if __name__ == "__main__":
    run()
