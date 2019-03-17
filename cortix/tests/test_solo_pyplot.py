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

import os
from cortix import Cortix

def test_solo_pyplot():
    '''
    Run solo_pyplot and make sure the correct output is generated
    '''
    pwd = os.path.dirname(__file__)
    full_path_config_file = os.path.join(
        pwd, 'input/cortix-config-pyplot.xml')
#    os.system('cp input/state.xml /tmp')
    cortix1 = Cortix('cortix-dev1', full_path_config_file)
    cortix1.run_simulations(task_name='solo-pyplot')
    for i in range(14):
        assert os.path.exists('pyplot_0-timeseq-dashboard-%02d.png' % i)
    os.system('rm -f *.png')
    os.system('rm -f *.pickle')

if __name__ == "__main__":
    test_solo_pyplot()
