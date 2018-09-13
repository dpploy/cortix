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

Phase *history* container. When you think of a phase value, think of that value at
a specific point in time.

----------
ATTENTION:
----------
The species (list of Specie) AND quantities (list of Quantity) data members
have ARBITRARY density values either at an arbitrary point in the history or at
no point in the history. This needs to be removed in the future.

To obtain history values, associated to the phase, at a particular point in time,
use the GetValue() method to access the history data frame (pandas) via columns and
rows. The corresponding values in species and quantities are OVERRIDEN and NOT to
be used through the phase interface.

VFdALib support classes

Sat Sep  5 01:26:53 EDT 2015
"""
# *******************************************************************************
import os
import sys
from copy import deepcopy
import pandas

from cortix.support.specie import Specie
from cortix.support.quantity import Quantity
# *******************************************************************************


class Phase():

    def __init__(self,
                 timeStamp=None,
                 species=None,
                 quantities=None,
                 # note: remove this later and let 0.0 be default
                 value=float(0.0)
                 ):
        # Value needs to be removed; makes no sense

        if timeStamp is None:
            timeStamp = 0.0
        assert isinstance(timeStamp, float)

        if species is not None:
            assert isinstance(species, list)
            if len(species) > 0:
                assert isinstance(species[-1], Specie)

        if quantities is not None:
            assert isinstance(quantities, list)
            if len(quantities) > 0:
                assert isinstance(quantities[-1], Quantity)

        assert isinstance(value, float)

# List of species and quantities objects; columns of data frame are named
# by objects
        # a new object held by a Phase() object
        self._species = deepcopy(species)
        # a new object held by a Phase() object
        self._quantities = deepcopy(quantities)

        names = list()

        if species is not None:
            for specie in self._species:
                names.append(specie.name)
                specie.massCC = value   # massCC in specie is overriden here on local copy

        if quantities is not None:
            for quant in self._quantities:
                names.append(quant.name)
                quant.value = value       # value in quant is overriden here on local copy

# Table data phase
        self._phase = pandas.DataFrame(index=[timeStamp], columns=names)
        self._phase.fillna(float(value), inplace=True)

        return

# *******************************************************************************
# Setters and Getters methods
# -------------------------------------------------------------------------------
# These are passing arguments by value effectively. Because the python objects
# passed into/out of the function are immutable.

    def GetActors(self):
        return list(self._phase.columns)  # return all names in order

    def GetTimeStamps(self):
        return list(self._phase.index)  # return all time stamps
    timeStamps = property(GetTimeStamps, None, None, None)

    def GetSpecie(self, name):
        for specie in self._species:
            if specie.name == name:
                return specie
        return None

    def GetSpecies(self):
        return self._species
    species = property(GetSpecies, None, None, None)

    def GetQuantities(self):
        return self._quantities
    quantities = property(GetQuantities, None, None, None)

    def SetSpecieId(self, name, val):
        for specie in self._species:
            if specie.name == name:
                specie.flag = val
                return

    def GetQuantity(self, name):
        for quant in self._quantities:
            if quant.name == name:
                return quant
        return None

    def AddSpecie(self, newSpecie):
        assert isinstance(newSpecie, Specie)
        assert newSpecie.name not in list(
            self._phase.columns), 'quantity: %r exists. Current names: %r' % (newQuant, self._phase.columns)
        speciesFormulae = [specie.formulaName for specie in self._species]
        assert newSpecie.formulaName not in speciesFormulae
        self._species.append(newSpecie)
        newName = newSpecie.name
        col = pandas.DataFrame(
            index=list(
                self._phase.index),
            columns=[newName])
        tmp = self._phase
        df = tmp.join(col, how='outer')
        self._phase = df.fillna(0.0)

    def AddQuantity(self, newQuant):
        assert isinstance(newQuant, Quantity)
        assert newQuant.name not in list(
            self._phase.columns), 'quantity: %r exists. Current names: %r' % (newQuant, self._phase.columns)
        quantFormalNames = [quant.formalName for quant in self._quantities]
        assert newQuant.formalName not in quantFormalNames
        self._quantities.append(newQuant)
        newName = newQuant.name
        col = pandas.DataFrame(
            index=list(
                self._phase.index),
            columns=[newName])
        tmp = self._phase
        df = tmp.join(col, how='outer')
        self._phase = df.fillna(0.0)

    def AddRow(self, timeStamp, rowValues):

        assert timeStamp not in self._phase.index

        assert len(rowValues) == len(self._phase.columns)
        tmp = dict()
        for (i, v) in zip(self._phase.columns, rowValues):
            tmp[i] = float(v)
        row = pandas.DataFrame(
            tmp, index=[timeStamp], columns=list(
                self._phase.columns))
        frames = [self._phase, row]
        self._phase = pandas.concat(frames)
        return

    def GetRow(self, timeStamp=None):
        if timeStamp is None:
            timeStamp = self._phase.index[-1]
        else:
            assert timeStamp in self._phase.index, 'no timeStamp = %r' % (
                timeStamp)
        return list(self._phase.loc[timeStamp, :])

    def GetColumn(self, actor):
        assert actor in self._phase.columns
        return list(self._phase.loc[:, actor])

    def ScaleRow(self, timeStamp, value):
        assert timeStamp in self._phase.index
        self._phase.loc[timeStamp, :] *= float(value)
        return

    # set species and quantities of history to a given value (default to zero value)
    # all time stamps are preserved
    def ClearHistory(self, value=0.0):
        self._phase.loc[:, :] = float(value)
        return

    # set species and quantities of history to a given value (default to zero value)
    # only one time stamp is preserved (default to last time stamp)
    def ResetHistory(self, timeStamp=None, value=None):
        if timeStamp is None:
            values = self.GetRow()
            timeStamp = self._phase.index[-1]
        else:
            values = self.GetRow(timeStamp)

        columns = list(self._phase.columns)
        assert len(columns) == len(values), 'FATAL: oops internal error.'

        self._phase = pandas.DataFrame(index=[timeStamp], columns=columns)
        self._phase.fillna(0.0, inplace=True)

        if value is None:
            for v in values:
                idx = values.index(v)
                self._phase.loc[timeStamp, columns[idx]] = v
        else:
            self._phase.loc[timeStamp, :] = float(value)

        return

    def GetValue(self, actor, timeStamp=None):
        if timeStamp is None:
            timeStamp = self._phase.index[-1]
        else:
            assert timeStamp in self._phase.index
        assert actor in self._phase.columns
        return self._phase.loc[timeStamp, actor]

# old def SetValue(self, timeStamp, actor, value):
# new
    def SetValue(self, actor, value, timeStamp=None):
        if timeStamp is None:
            timeStamp = self._phase.index[-1]
        else:
            assert timeStamp in self._phase.index, 'missing timeStamp = %r' % (
                timeStamp)
        assert isinstance(actor, str)
        assert actor in self._phase.columns
        self._phase.loc[timeStamp, actor] = float(value)
        return

    def WriteHTML(self, fileName):
        assert isinstance(fileName, str)
        tmp = pandas.DataFrame(self._phase)
        columnNames = tmp.columns
        speciesNames = [specie.name for specie in self._species]
        quantityNames = [quantity.name for quantity in self._quantities]
        for col in columnNames:
            if col in speciesNames:
                idx = speciesNames.index(col)
                specie = self._species[idx]
                tmp.rename(columns={col: specie.formulaName}, inplace=True)
            elif col in quantityNames:
                idx = quantityNames.index(col)
                quant = self._quantities[idx]
                tmp.rename(
                    columns={
                        col: col + '[' + quant.unit + ']'},
                    inplace=True)
            else:
                assert False, 'oops fatal.'
        tmp.to_html(fileName)

# *******************************************************************************
# Printing of data members
# def __str__( self ):
        s = '\n\t **Phase()**: \n\t *quantities*: %s\n\t *species*: %s\n\t *history* #timeStamps=%s\n\t *history end* @%s\n%s'
        return s % (self._quantities, self._species, len(self._phase.index),
                    self._phase.index[-1], self._phase.loc[self._phase.index[-1], :])
#

    def __repr__(self):
        s = '\n\t **Phase()**: \n\t *quantities*: %s\n\t *species*: %s\n\t *history* #timeStamps=%s\n\t *history end* @%s\n%s'
        return s % (self._quantities, self._species, len(self._phase.index),
                    self._phase.index[-1], self._phase.loc[self._phase.index[-1], :])
# *******************************************************************************
