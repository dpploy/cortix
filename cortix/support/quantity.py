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
'''
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

This Quantity class is to be used with other classes in plant-level process modules.

For unit testing do at the linux command prompt:
    python quantity.py

Sat Sep  5 12:51:34 EDT 2015
'''
#*********************************************************************************
import os
import sys
import numpy as npy
#*********************************************************************************

class Quantity():
    '''
    todo: this probably should not have a "value" for the same reason as Specie.
          this needs some thinking.
    '''

#*********************************************************************************
# Construction
#*********************************************************************************

    def __init__(self,
                 name       = 'null-quantity',
                 formalName = 'null-quantity',
                 value      = float(0.0),  # this can be any type
                 unit       = 'null-unit'
                ):

        # Sanity tests here
        assert isinstance(name, str), 'oops not string.'
        self._name = name

        assert isinstance(formalName, str), 'oops not string.'
        self._formalName = formalName

        self.__value = value

        assert isinstance(name, str), 'oops not string.'
        self.__unit = unit

        self.__name = name
        self._formalName = formalName
        self.__value = value
        self.__unit = unit

        return

#*********************************************************************************
# Public member functions
#*********************************************************************************

    def SetName(self, n):
        self.__name = n

    def get_name(self):
        return self.__name
    name = property(get_name, SetName, None, None)

    def SetValue(self, v):
        self.__value = v

    def GetValue(self):
        return self.__value
    value = property(GetValue, SetValue, None, None)

    def SetFormalName(self, fn):
        self._formalName = fn

    def GetFormalName(self):
        return self._formalName
    formalName = property(GetFormalName, SetFormalName, None, None)
    formal_name = property(GetFormalName, SetFormalName, None, None)

    def SetUnit(self, f):
        self.__unit = f

    def GetUnit(self):
        return self.__unit
    unit = property(GetUnit, SetUnit, None, None)

    def __str__(self):
        s = '\n\t Quantity(): \n\t name=%s; formal name=%s; value=%s[%s]'
        return s % (self.name, self.formalName, self.value, self.unit)

    def __repr__(self):
        s = '\n\t Quantity(): \n\t name=%s; formal name=%s; value=%s[%s]'
        return s % (self.name, self.formalName, self.value, self.unit)

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

#======================= end class Quantity ======================================
