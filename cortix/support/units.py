#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org
"""Cortix module.
Convenient non-SI (and SI) units to be transformed to SI.

Usage
-----

On guest code.py:

from cortix import Units as unit

size = 10*unit.meter
temp = 10*unit.kelvin

"""

import scipy.constants as spc

class Units:
    second = 1.0
    minute = spc.minute
    hour = spc.hour
    day = spc.day
    kg = spc.kilo*spc.gram
    meter = 1.0
    joule = 1.0
    pascal = 1.0
    watt = 1.0
    kelvin = 1.0
    liter = spc.liter
    gallon = spc.gallon

    ppm = 1.0

    cm = spc.centi*meter
    ft = spc.foot
    cc = (spc.centi*meter)**3
    kj = spc.kilo*joule
    btu = spc.Btu
    barn = 1.0e-28 * meter**2
    F = spc.convert_temperature(2,'F','K') - spc.convert_temperature(1,'F','K')
    C = spc.convert_temperature(2,'C','K') - spc.convert_temperature(1,'C','K')
    K = 1.0
