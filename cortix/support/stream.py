# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/cortix
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/cortix/blob/master/COPYRIGHT.txt
#
# Licensed under the GNU General Public License v. 3, please see LICENSE file.
# https://www.gnu.org/licenses/gpl-3.0.txt
"""
Author: Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Stream container

VFdALib support classes

Sat Aug 15 17:24:02 EDT 2015
"""

# *******************************************************************************
import os
import sys
import pandas

from cortix.support.specie import Specie
from cortix.support.quantity import Quantity
# *******************************************************************************

# *******************************************************************************


class Stream():

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


# *******************************************************************************
# Setters and Getters methods
# -------------------------------------------------------------------------------
# These are passing arguments by value effectively. Because the python objects
# passed into/out of the function are immutable.

    def GetTimeStamp(self):
        return self.timeStamp

    def GetActors(self):
        return list(self.stream.columns)

    def GetSpecie(self, name):
        for specie in self.species:
            if specie.name == name:
                return specie
        return None

    def GetSpecies(self):
        return self.species

    def GetQuantities(self):
        return self.quantities

    def SetSpecieId(self, name, val):
        for specie in self.species:
            if specie.name == name:
                specie.flag = val
                return

    def GetQuantity(self, name):
        for quant in self.quantities:
            if quant.name == name:
                return quant
        return None

    def GetRow(self, timeStamp=None):
        if timeStamp is None:
            return list(self.stream.loc[self.timeStamp, :])
        else:
            assert timeStamp in self.stream.index, 'timeStamp = %r' % (
                timeStamp)
            return list(self.stream.loc[timeStamp, :])

    def GetValue(self, actor, timeStamp=None):
        assert actor in self.stream.columns
        if timeStamp is None:
            return self.stream.loc[self.timeStamp, actor]
        else:
            assert timeStamp in self.stream.index
            return self.stream.loc[timeStamp, actor]

    def SetValue(self, actor, value=None, timeStamp=None):
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

# *******************************************************************************
# Printing of data members
# def __str__( self ):
#     s = ' %5s %5s %5s '+' molar mass: %6s '+' molar cc: %6s '+' mass cc: %6s '+' flag: %s '+'# atoms: %s'+' atoms: %s\n'
#     return s % (self.name, self.formulaName, self.phase, self.molarMass, self.molarCC, self.massCC, self.flag, self.nAtoms, self.atoms)
#
# def __repr__( self ):
#     s = ' %5s %5s %5s '+' molar mass: %6s '+' molar cc: %6s '+' mass cc: %6s '+' flag: %s '+'# atoms: %s'+' atoms: %s\n'
#     return s % (self.name, self.formulaName, self.phase, self.molarMass, self.molarCC, self.massCC, self.flag, self.nAtoms, self.atoms)
# *******************************************************************************
