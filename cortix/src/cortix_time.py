#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
# Licensed under the University of Massachusetts Lowell LICENSE:
# https://github.com/dpploy/cortix/blob/master/LICENSE.txt

class CortixTime:
    """
    This class wraps a time value + a time unit
    """
    time_units = ["sec", "min", "hour"]

    def __init__(self, time=0.0, unit="SEC"):
        self.time = time
        self.set_unit(unit)

    def set_time(self, time):
        self.time = time

    def set_unit(self, unit):
        assert unit.lower() in time_units, "Time unit must be one of: {}".format(time_units)
        self.unit = unit
