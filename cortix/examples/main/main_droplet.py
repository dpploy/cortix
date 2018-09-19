#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/...
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/COPYRIGHT
#
# Licensed under the GNU General Public License v. 3, please see LICENSE file.
# https://www.gnu.org/licenses/gpl-3.0.txt
"""
Cortix: a program for system-level modules coupling, execution, and analysis.

Cortix is a library and it is used by means of a driver. This file is a simple example
of a driver. Many Cortix objects can be ran simultaneously; a single object
may be sufficient since many simulation/tasks can be ran via one object.

As Cortix evolves additional complexity may be added to this driver and/or other
driver examples can be created.
"""
#*********************************************************************************
import os
from cortix import Cortix 
#*********************************************************************************

def main():

 pwd                   = os.path.dirname(__file__)
 full_path_config_file = os.path.join(pwd, 'input/cortix-config-droplet.xml')

 # NB: if another instantiation of Cortix occurs, the cortix wrk directory specified
 #     in the cortix configuration file must be different, else the logging facility 
 #     will have log file collision.

 cortix1 = Cortix( 'cortix-droplet', full_path_config_file ) # see cortix-config-droplet.xml
#
# cortix1.run_simulations( task_name='solo-droplet-fall' )
 cortix1.run_simulations( task_name='droplet-fall' )
# cortix1.run_simulations( task_name='solo-pyplot' )

#---------------------- end def main():-------------------------------------------

#*********************************************************************************
# Usage: -> python cortix-main.py or ./cortix-main.py
if __name__ == "__main__":
 main()
