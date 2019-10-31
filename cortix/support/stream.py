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
Author: Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Stream container

VFdALib support classes

Sat Aug 15 17:24:02 EDT 2015
'''
#*********************************************************************************
import os
import sys
import pandas

from cortix.support.specie import Specie
from cortix.support.quantity import Quantity
#*********************************************************************************

class Stream:

#*********************************************************************************
# Construction
#*********************************************************************************

    def __init__(self,
                 timeStamp,
                 species=None,
                 quantities=None,
                 values=float(0.0)
                 ):

        # constructor
        # THIS WILL CREATE AN ORDERED "STREAM"; values must be in order!

        assert isinstance(timeStamp, float)

        self.timeStamp = timeStamp

        if species is not None:
            assert isinstance(species, list)
            if len(species) > 0:
                assert isinstance(species[-1], Specie)

        if quantities is not None:
            assert isinstance(quantities, list)
            if len(quantities) > 0:
                assert isinstance(quantities[-1], Quantity)

#  assert type(value) == type(float())

# List of quantities and species objects
        self.species = species       # list
        self.quantities = quantities    # list

        names = list()  # note order of names; values must be in the same order; caution

        for specie in self.species:
            names.append(specie.name)

        for quant in self.quantities:
            names.append(quant.name)

# ORDERED data; caution!!
# Table data stream
        self.stream = pandas.DataFrame(index=[timeStamp], columns=names)
        if isinstance(values, float):
            self.stream.fillna(values, inplace=True)
        else:
            self.stream.fillna(0.0, inplace=True)

        if isinstance(values, list) and len(values) == len(names):
            for (name, val) in zip(names, values):
                self.stream.loc[timeStamp, name] = val

        return

#*********************************************************************************
# Public Member Functions
#*********************************************************************************

    def GetTimeStamp(self):
        '''
        Returns the time stamp of the stream.

        Returns
        -------
        self.timeStamp: float
        '''

        return self.timeStamp

    def GetActors(self):
        '''
        Returns the actors present in the stream of data.

        Returns
        -------
        list(self.stream.columns): list
        '''

        return list(self.stream.columns)

    def GetSpecie(self, name):
        '''
        Returns a specie named "name" from the stream.

        Parameters
        ----------
        name: str

        Returns
        -------
        specie: obj
        '''

        for specie in self.species:
            if specie.name == name:
                return specie
        return None

    def GetSpecies(self):
        '''
        Returns a list of all species in the stream.

        Returns
        -------
        self.species: list
        '''

        return self.species

    def GetQuantities(self):
        '''
        Returns all the quantities given by the stream.

        Returns
        -------
        self.quantities: list
        '''

        return self.quantities

    def SetSpecieId(self, name, val):
        '''
        Sets the numerical id of the specie of name "name" to val.

        Parameters
        ----------
        name: str
        val: int
        '''

        for specie in self.species:
            if specie.name == name:
                specie.flag = val
                return

    def GetQuantity(self, name):
        '''
        Returns the specified quantity called "name" from the stream, or none
        if the specified name does not exist.

        Parameters
        ----------
        name: str

        Returns
        -------
        quant: float
        '''

        for quant in self.quantities:
            if quant.name == name:
                return quant
        return None

    def GetRow(self, timeStamp=None):
        '''
        Returns an entire row of data from the stream. A row of data is all
        the data in a dataframe at a specified time stamp, given by timeStamp.
        If timeStamp is not specified, this function will return the entire
        stream dataframe.

        Parameters
        ----------
        timeStamp: float

        Returns
        -------
        self.stream.loc[self.timestamp, :]) or self.stream.loc[timeStamp, :]):
        list
        '''

        if timeStamp is None:
            return list(self.stream.loc[self.timeStamp, :])
        else:
            assert timeStamp in self.stream.index, 'timeStamp = %r' % (
                timeStamp)
            return list(self.stream.loc[timeStamp, :])

    def GetValue(self, actor, timeStamp=None):
        '''
        Returns the value associated with a specified "actor" at a specified
        "timeStamp". If no timeStamp is specified, then the function will
        return all values associated with the specified actor at all time
        stamps.

        Parameters
        ----------
        actor: str
        timeStamp: float

        Returns
        -------
        self.stream.loc[self.timeStamp, actor] or self.stream.loc[timeStamp,
        actor]: list or float, respectively.
        '''

        assert actor in self.stream.columns
        if timeStamp is None:
            return self.stream.loc[self.timeStamp, actor]
        else:
            assert timeStamp in self.stream.index
            return self.stream.loc[timeStamp, actor]

    def SetValue(self, actor, value=None, timeStamp=None):
        '''
        Sets the value associated with a specified actor at a specified
        timeStamp to "value". If no value is specified, the value will default
        to 0.0. If no timeStamp is specified, it will set all values associated
        with actor to the specified value (or 0.0 if value = None).

        Parameters
        ----------
        actor: str
        value: float
        timeStamp: float
        '''

        assert actor in self.stream.columns
        if timeStamp is None:
            if value is None:
                self.stream.loc[self.timeStamp, actor] = float(0.0)
            else:
                self.stream.loc[self.timeStamp, actor] = float(value)
        else:
            assert timeStamp in self.stream.index, 'timeStamp = %r' % (
                timeStamp)
            if value is None:
                self.stream.loc[timeStamp, actor] = float(0.0)
            else:
                self.stream.loc[timeStamp, actor] = float(value)

# def __str__( self ):
#     s = ' %5s %5s %5s '+' molar mass: %6s '+' molar cc: %6s '+' mass cc: %6s '+' flag: %s '+'# atoms: %s'+' atoms: %s\n'
#     return s % (self.name, self.formulaName, self.phase, self.molarMass, self.molarCC, self.massCC, self.flag, self.nAtoms, self.atoms)
#
# def __repr__( self ):
#     s = ' %5s %5s %5s '+' molar mass: %6s '+' molar cc: %6s '+' mass cc: %6s '+' flag: %s '+'# atoms: %s'+' atoms: %s\n'
#     return s % (self.name, self.formulaName, self.phase, self.molarMass, self.molarCC, self.massCC, self.flag, self.nAtoms, self.atoms)

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

#============================= end class Stream ==================================
