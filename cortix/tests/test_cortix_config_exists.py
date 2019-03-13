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


def test_cortix_config_exists():
    '''
    Test to make sure a configuration file exists
    in the input directory.
    '''

    assert os.path.isfile("input/cortix-config-pyplot.xml")
    assert os.path.isfile("input/cortix-config-droplet.xml")

if __name__ == "__main__":
    test_cortix_config_exists()
