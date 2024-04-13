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

    # unit prefix
    mega = spc.mega
    kilo = spc.kilo
    centi = spc.centi
    milli = spc.milli

    # time
    second = 1.0
    minute = spc.minute
    min = minute
    hour = spc.hour
    day = spc.day

    # mass
    gram = spc.gram
    kg = kilo*gram

    # length
    meter = 1.0
    cm = centi*meter
    ft = spc.foot

    # area
    barn = 1.0e-28 * meter**2 # nuclear cross section

    # volume
    cc = (centi*meter)**3
    liter = spc.liter
    L = liter
    mL = milli*L
    gallon = spc.gallon

    # energy/power/pressure
    joule = 1.0
    kj = kilo*joule
    watt = 1.0
    btu = spc.Btu
    pascal = 1.0
    bar = spc.bar

    # charge/electric potential/current
    coulomb = 1.0
    volt = joule/coulomb
    ampere = coulomb/second
    var = volt*ampere # reactive electric power

    ppm = 1.0

    # temperature
    F = spc.convert_temperature(2,'F','K') - spc.convert_temperature(1,'F','K')
    C = spc.convert_temperature(2,'C','K') - spc.convert_temperature(1,'C','K')
    K = 1.0
    kelvin = 1.0
