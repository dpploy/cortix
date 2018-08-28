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
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

Fuel segment

VFdALib support classes

Sat Jun 27 14:46:49 EDT 2015
"""
# *******************************************************************************
import os
import sys
import io
import time
import datetime
import math
import random
import pandas

from cortix.support.periodictable import ELEMENTS
from cortix.support.periodictable import SERIES
from cortix.support.specie import Specie
# *******************************************************************************

# *******************************************************************************


class FuelSegment():

    # Todo: Species should not be here. Need to replace by Phase instead.
    #      Chopper will be affected

    def __init__(self,
                 geometry=pandas.Series(),
                 species=list()
                 ):

        assert isinstance(geometry, type(pandas.Series())), 'fatal.'
        assert isinstance(species, type(list())), 'fatal.'
        if isinstance(species, type(list())) and len(species) > 0:
            assert isinstance(species[0], type(Specie()))

        self.attributeNames = \
            ['nSegments',
             'fuelVolume',
             'fuelDiameter',
             'fuelLength',
             'mass',
             'massDens',
             'massCC',
             'nuclides',
             'isotopes',
             'radioactivity',
             'radioactivityDens',
             'gamma',
             'gammaDens',
             'heat',
             'heatDens',
             'molarHeatPwr',
             'molarGammaPwr']

        self._geometry = geometry
        self._species = species


# *******************************************************************************

# *******************************************************************************
# Setters and Getters methods
# -------------------------------------------------------------------------------
# These are passing arguments by value effectively. Because the python objects
# passed into/out of the function are immutable.

    def GetGeometry(self):
        return self._geometry
    geometry = property(GetGeometry, None, None, None)

    def GetSpecies(self):
        return self._species
    species = property(GetSpecies, None, None, None)

    def GetSpecie(self, name):
        for specie in self._species:
            if specie.name == name:
                return specie
        return None
    specie = property(GetSpecie, None, None, None)

    def GetAttribute(self, name, symbol=None, series=None):
        return self.__GetAttribute(name, symbol, series)


# *********************************************************************************

# Get stored fuel segment property either overall or on a nuclide basis

# ---------------------------------------------------------------------------------

    def __GetAttribute(self, attributeName, nuclide=None, series=None):

        assert attributeName in self.attributeNames, ' attribute name: %r; options: %r; fail.' % (
            attributeName, self.attributeNames)

        if nuclide is not None:
            assert len(nuclide.split('*')) == 1  # sanity check

        if nuclide is not None:
            assert series is None, 'fail.'
        if series is not None:
            assert nuclide is None, 'fail.'

        if series is not None:
            assert False, ' not implemented.'

        if attributeName == 'isotopes':
            assert nuclide is not None, 'need a nuclide symbol.'

# .................................................................................
# # of segments

        if attributeName == 'nSegments':
            return 1

# .................................................................................
# segmentId

        if attributeName == 'segmentId':
            return self.geometry['segment id']

# .................................................................................
# fuel volume

        if attributeName == 'fuelVolume':
            return self.__GetFuelSegmentVolume()
# .................................................................................
# segment volume

        if attributeName == 'segmentVolume':

            claddingLength = self.geometry['cladding length [cm]']
            claddingDiam = self.geometry['OD [cm]']
            volume = claddingLength * math.pi * (claddingDiam / 2.0)**2
            return volume

# .................................................................................
# fuel diameter

        if attributeName == 'fuelDiameter':

            fuelDiam = self.geometry['fuel diameter [cm]']
            return fuelDiam

# .................................................................................
# fuel length

        if attributeName == 'fuelLength':

            fuelLength = self.geometry['fuel length [cm]']
            return fuelLength

# .................................................................................
# fuel segment overall quantities
        if nuclide is None and series is None:

            # mass or mass concentration
            if attributeName == 'massCC' or attributeName == 'massDens' or attributeName == 'mass':
                massCC = 0.0
                for spc in self._species:
                    massCC += spc.massCC
                if attributeName == 'massCC' or attributeName == 'massDens':
                    return massCC
                else:
                    volume = self.__GetFuelSegmentVolume()
                    return massCC * volume
# radioactivity
            if attributeName == 'radioactivtyDens' or attributeName == 'radioactivity':
                radDens = 0.0
                for spc in self._species:
                    radDens += spc.molarRadioactivity * spc.molarCC
                if attributeName == 'radioactivityDens':
                    return radDens
                else:
                    volume = self.__GetFuelSegmentVolume()
                    return radDens * volume
# gamma
            if attributeName == 'gammaDens' or attributeName == 'gamma':
                gammaDens = 0.0
                for spc in self._species:
                    gammaDens += spc.molarGammaPwr * spc.molarCC
                if attributeName == 'gammaDens':
                    return gammaDens
                else:
                    volume = self.__GetFuelSegmentVolume()
                    return gammaDens * volume
# heat
            if attributeName == 'heatDens' or attributeName == 'heat':
                heatDens = 0.0
                for spc in self._species:
                    heatDens += spc.molarHeatPwr * spc.molarCC
                if attributeName == 'heatDens':
                    return heatDens
                else:
                    volume = self.__GetFuelSegmentVolume()
                    return heatDens * volume

# .................................................................................
# radioactivity

        if attributeName == 'radioactivityDens' or attributeName == 'radioactivity':
            assert False
            colName = 'Radioactivity Dens. [Ci/cc]'

# .................................................................................
# thermal

        if attributeName == 'thermalDens' or attributeName == 'thermal' or  \
           attributeName == 'heatDens' or attributeName == 'heat':
            assert False
            colName = 'Thermal Dens. [W/cc]'

# .................................................................................
# gamma

        if attributeName == 'gammaDens' or attributeName == 'gamma':
            assert False
            colName = 'Gamma Dens. [W/cc]'

# .................................................................................
##########################################################################
# .................................................................................

#  if attributeName[-4:] == 'Dens' or attributeName[-2:] == 'CC':
#     attributeDens = True
#  else:
#     attributeDens = False

# .................................................................................
# all nuclide content of the fuel added

#  if nuclide is None and series is None:
#
#     density = 0.0
#
#     density = self.propertyDensities[ colName ].sum()
#
#     if attributeDens is False:
#        volume = self.__GetFuelSegmentVolume()
#        prop = density * volume
#        return prop
#     else:
#        return density

# .................................................................................
# get chemical element series

#  if series is not None:
#
#     density = 0.0
#
#     for isotope in isotopes:
#       density += self.propertyDensities.loc[isotope,colName]
#
#     if attributeDens is False:
#        volume = self.__GetFuelSegmentVolume()
#        prop = density * volume
#        return prop
#     else:
#        return density

# .................................................................................
# get specific nuclide (either the isotopes of the nuclide or the specific
# isotope) property

        if nuclide is not None:

            # a particular nuclide given (atomic number and atomic mass number)
            if len(nuclide.split('-')) == 2:

                nuclideMassNumber = int(nuclide.split('-')[1].strip('m'))
                nuclideSymbol = nuclide.split('-')[0]
                nuclideMolarMass = ELEMENTS[nuclideSymbol].isotopes[nuclideMassNumber].mass

                massCC = 0.0

                for spc in self._species:

                    formula = spc.atoms

                    moleFraction = 0.0

                    for item in formula:

                        if len(item.split('*')
                               ) == 1:  # no multiplier (implies 1.0)

                            formulaNuclideSymbol = item.split('-')[0].strip()
                            if formulaNuclideSymbol == nuclideSymbol:
                                assert len(item.split('-')) == 2

                            if item.split('*')[0].strip() == nuclide:
                                moleFraction = 1.0
                            else:
                                moleFraction = 0.0

                        elif len(item.split('*')) == 2:  # with multiplier

                            formulaNuclideSymbol = item.split(
                                '*')[1].split('-')[0].strip()
                            if formulaNuclideSymbol == nuclideSymbol:
                                assert len(item.split('*')[1].split('-')) == 2

                            if item.split('*')[1].strip() == nuclide:
                                moleFraction = float(
                                    item.split('*')[0].strip())
                            else:
                                moleFraction = 0.0

                        else:
                            assert False

                        massCC += spc.molarCC * moleFraction * nuclideMolarMass

                return massCC * self.__GetFuelSegmentVolume()

        # chemical element given (only atomic number given)
            elif len(nuclide.split('-')) == 1:

                massCC = 0.0

                for spc in self._species:

                    formula = spc.atoms

                    for item in formula:

                        moleFraction = 0.0

                        if len(item.split('*')
                               ) == 1:  # no multiplier (implies 1.0)

                            assert len(item.split('-')) == 2
                            formulaNuclideSymbol = item.split('-')[0].strip()
                            formulaNuclideMassNumber = int(
                                item.split('-')[1].strip('m'))
                            formulaNuclideMolarMass = ELEMENTS[formulaNuclideSymbol].isotopes[formulaNuclideMassNumber].mass

                            if formulaNuclideSymbol == nuclide:
                                moleFraction = 1.0
                            else:
                                moleFraction = 0.0

                        elif len(item.split('*')) == 2:  # with multiplier

                            assert len(item.split('*')[1].split('-')) == 2
                            formulaNuclideSymbol = item.split(
                                '*')[1].split('-')[0].strip()
                            formulaNuclideMassNumber = int(
                                item.split('*')[1].split('-')[1].strip('m'))
                            formulaNuclideMolarMass = ELEMENTS[formulaNuclideSymbol].isotopes[formulaNuclideMassNumber].mass

                            if formulaNuclideSymbol == nuclide:
                                moleFraction = float(
                                    item.split('*')[0].strip())
                            else:
                                moleFraction = 0.0

                        else:
                            assert False

                        massCC += spc.molarCC * moleFraction * formulaNuclideMolarMass

                return massCC * self.__GetFuelSegmentVolume()

            else:

                assert False

# ---------------------------------------------------------------------------------
    def __GetFuelSegmentVolume(self):

        fuelLength = self.geometry['fuel length [cm]']
        fuelDiam = self.geometry['fuel diameter [cm]']

        volume = fuelLength * math.pi * (fuelDiam / 2.0)**2

        return volume

# *********************************************************************************

# *******************************************************************************
# Printing of data members
    def __str__(self):
        s = 'FuelSegment(): %s\n %s\n'
        return s % (self._geometry, self._species)

    def __repr__(self):
        s = 'FuelSegment(): %s\n %s\n'
        return s % (self._geometry, self._species)
# *******************************************************************************
