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

import importlib


def test_mpi4py():
    '''
    Test for the mpi4py dependency
    '''
    try:
        import mpi4py
        found = True
    except ImportError:
        found = False
    assert found == True


if __name__ == "__main__":
    test_mpi4py()
