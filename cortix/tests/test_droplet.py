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

import os
from cortix import Cortix

def test_droplet():
    '''
    Run the droplet example
    '''
    pwd = os.path.dirname(__file__)
    full_path_config_file = os.path.join(pwd, 'input/cortix-config-droplet.xml')
    cortix1 = Cortix('cortix-droplet', full_path_config_file)
    cortix1.run_simulations(task_name="droplet-fall")

if __name__ == "__main__":
    test_droplet()
