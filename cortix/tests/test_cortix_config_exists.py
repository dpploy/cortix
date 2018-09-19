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


def test_cortix_config_exists():
    '''
    Test to make sure a configuration file exists
    in the input directory.
    '''

    assert os.path.isfile("input/cortix-config-pyplot.xml")
    assert os.path.isfile("input/cortix-config-droplet.xml")

if __name__ == "__main__":
    test_cortix_config_exists()
