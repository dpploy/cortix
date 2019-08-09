#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
# Licensed under the University of Massachusetts Lowell LICENSE:
# https://github.com/dpploy/cortix/blob/master/LICENSE.txt

from cortix.src.utils.cortix_units import Units

class CortixTime:
    """
    This class wraps a time value + a time unit
    """

    def __init__(self, time=0.0, unit=Units.SEC):
        self.time = time
        self.set_unit(unit)

    def set_time(self, time):
        self.time = time

    def set_unit(self, unit):
        assert isinstance(unit, Units), "time unit must be of type Unit"
        self.unit = unit
