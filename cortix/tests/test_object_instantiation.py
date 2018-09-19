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
from mpi4py import MPI
from cortix import Cortix

def test_object_instantiation():
    '''
    Test for successful object instantiation
    '''
    pwd = os.path.dirname(__file__)
    full_path_config_file = os.path.join(
        pwd, 'input/cortix-config-pyplot.xml')
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    if rank == 0:
        cortix1 = Cortix('cortix-dev1', full_path_config_file)
        assert cortix1 is not None


if __name__ == "__main__":
    test_object_instantiation()
