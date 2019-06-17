#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
# Licensed under the University of Massachusetts Lowell LICENSE:
# https://github.com/dpploy/cortix/blob/master/LICENSE.txt

from enum import Enum

class Units(Enum):
    """
    Enum for quantitative units used in Cortix
    """
    SEC = 0
    MIN = 1
    HOUR = 2
