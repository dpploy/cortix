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

class Quantity:
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

        '''
        Sets the name of the quantity in question to n.

        Parameters
        ----------
        n: str

        Returns
        -------
        empty
        '''
        self.__name = n

    def get_name(self):

        '''
        Returns the name of the quantity.

        Parameters
        ----------
        empty

        Returns
        -------
        name: str
        '''

        return self.__name
    name = property(get_name, SetName, None, None)

    def SetValue(self, v):

        '''
        Sets the numerical value of the quantity to v.

        Parameters
        ----------
        v: float

        Returns
        -------
        empty

        '''
        self.__value = v

    def GetValue(self):

        '''
        Gets the numerical value of the quantity.

        Parameters
        ----------
        empty

        Returns
        -------
        value: float
        '''

        return self.__value
    value = property(GetValue, SetValue, None, None)

    def SetFormalName(self, fn):
        '''
        Sets the formal name of the property to fn.

        Parameters
        ----------
        fn: str

        Returns
        -------
        empty
        '''

        self._formalName = fn

    def GetFormalName(self):

        '''
        Returns the formal name of the quantity.

        Parameters
        ----------
        empty

        Returns
        -------
        formalName: str
        '''

        return self._formalName
    formalName = property(GetFormalName, SetFormalName, None, None)
    formal_name = property(GetFormalName, SetFormalName, None, None)

    def SetUnit(self, f):

        '''
        Sets the units of the quantity to f (for example, density would be in
        units of g/cc.

        Parameters
        ----------
        f: str

        Returns
        -------
        empty
        '''

        self.__unit = f

    def GetUnit(self):

        '''
        Returns the units of the quantity.

        Parameters
        ----------
        empty

        Returns
        -------
        unit: str
        '''

        return self.__unit
    unit = property(GetUnit, SetUnit, None, None)

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

    def __str__(self):

        '''
        Used to print the data stored by the quantity class. Will print out
        name, formal name, the value of the quantity and its unit.

        Parameters
        ----------
        empty

        Returns
        -------
        s: str
        '''

        s = '\n\t Quantity(): \n\t name=%s; formal name=%s; value=%s[%s]'
        return s % (self.name, self.formalName, self.value, self.unit)

    def __repr__(self):

        '''
        Used to print the data stored by the quantity class. Will print out
        name, formal name, the value of the quantity and its unit.

        Parameters
        ----------
        empty

        Returns
        -------
        s: str
        '''

        s = '\n\t Quantity(): \n\t name=%s; formal name=%s; value=%s[%s]'
        return s % (self.name, self.formalName, self.value, self.unit)

#======================= end class Quantity ======================================
