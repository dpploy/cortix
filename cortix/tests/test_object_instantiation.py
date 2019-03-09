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

def test_object_instantiation():
    '''
    Test for successful object instantiation
    '''
    pwd = os.path.dirname(__file__)
    full_path_config_file = os.path.join(
        pwd, 'input/cortix-config-pyplot.xml')
    cortix1 = Cortix('cortix-dev1', full_path_config_file)
    assert cortix1 is not None

if __name__ == "__main__":
    test_object_instantiation()
