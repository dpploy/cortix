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

import importlib
import sys

def test_matplotlib():
    '''
    Test for the matplotlib dependency
    '''
    try:
        import matplotlib
        found = True
        del sys.modules["matplotlib"]
    except ImportError:
        found = False
    assert found == True


if __name__ == "__main__":
    test_matplotlib()
