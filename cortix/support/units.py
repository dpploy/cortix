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

   examples:
   size = 10*unit.meter
   temp = 10*unit.kelvin

   temp = convert_temp(10, 'C', 'K')

   incorrect: temp = 20*unit.F
   correct:   temp = unit.convert_temperature(20, 'F', 'K')
"""

import scipy.constants as scipy_cte

class Units:

    # make scipy constants available
    scipy_cte = scipy_cte

    # all class data

    # unit prefix
    mega = scipy_cte.mega
    kilo = scipy_cte.kilo
    centi = scipy_cte.centi
    milli = scipy_cte.milli

    # time
    second = 1.0
    minute = scipy_cte.minute
    sec = second
    min = minute
    hour = scipy_cte.hour
    day = scipy_cte.day
    year = scipy_cte.year

    # event driven or iterative processes
    event = 1.0
    step = 1.0

    # number
    mole = 1.00

    # mass
    gram = scipy_cte.gram
    kg = kilo*gram
    lb = scipy_cte.lb

    # length
    meter = 1.0
    cm = centi*meter
    ft = scipy_cte.foot
    foot = ft
    inch = scipy_cte.inch

    # area
    barn = 1.0e-28 * meter**2 # nuclear cross section

    # volume
    cc = (centi*meter)**3
    liter = scipy_cte.liter
    L = liter
    mL = milli*L
    gallon = scipy_cte.gallon

    # energy/power/pressure
    joule = 1.0
    kj = kilo*joule
    watt = 1.0
    btu = scipy_cte.Btu
    Btu = btu
    pascal = 1.0
    bar = scipy_cte.bar
    psi = scipy_cte.psi
    atm = scipy_cte.atm

    # charge/electric potential/current
    coulomb = 1.0
    volt = joule/coulomb
    ampere = coulomb/second
    var = volt*ampere # reactive electric power

    ppm = 1.0

    # temperature difference
    F = scipy_cte.convert_temperature(2,'F','K') - scipy_cte.convert_temperature(1,'F','K')
    C = scipy_cte.convert_temperature(2,'C','K') - scipy_cte.convert_temperature(1,'C','K')
    K = 1.0
    kelvin = 1.0

    # temperature conversion
    # static method
    def convert_temperature(val, from_scale_name, to_scale_name):
        return scipy_cte.convert_temperature(val, from_scale_name, to_scale_name)
