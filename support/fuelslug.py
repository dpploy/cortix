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

Fuel slug

----------
ATTENTION:
----------
This container requires two Phase() containers which are by definition histories.
The history is not checked. Therefore any inconsistency will be propagated forward.
A fuel slug has two solid phases: cladding and fuel. The user will decide how to
best use the underlying history data in the Phase() container of each phase.

VFdALib support classes

Thu Dec 15 16:18:39 EST 2016
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
from copy import deepcopy

from cortix.support.periodictable import ELEMENTS
from cortix.support.periodictable import SERIES
from cortix.support.phase import Phase
# *******************************************************************************

# *******************************************************************************


class FuelSlug():

    def __init__(self,
                 specs=pandas.Series(),
                 fuelPhase=Phase(),
                 claddingPhase=Phase()
                 ):

        assert isinstance(specs, pandas.Series), 'fatal.'
        assert isinstance(fuelPhase, Phase), 'fatal.'
        assert isinstance(claddingPhase, Phase), 'fatal.'

        self.attributeNames = \
            ['nSlugs',
             'slugType',
             'slugVolume',
             'slugArea',
             'fuelVolume',
             'claddingVolume',
             'fuelArea',
             'claddingArea',
             'equivalentCladdingVolume',
             'equivalentCladdingArea',
             'equivalentFuelVolume',
             'equivalentFuelArea',
             'fuelLength',
             'slugLength',
             'fuelMass',
             'fuelMassDens',
             'fuelMassCC',
             'claddingMass',
             'claddingMassDens',
             'claddingMassCC',
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

        # own internal copy
        self._specs = deepcopy(specs)
        self._fuelPhase = deepcopy(fuelPhase)
        self._claddingPhase = deepcopy(claddingPhase)

        # setup the equivalent cladding hollow sphere
        pi = math.pi

        area = self.__GetAttribute('claddingArea')
        volume = self.__GetAttribute('claddingVolume')

        ro = math.sqrt(area / 4 / pi)
        ri = (ro**3 - volume * 3 / 4 / pi)**(1 / 3)

        self._claddingHollowSphereRo = ro
        self._claddingHollowSphereRi = ri

        area = self.__GetAttribute('fuelArea')
        volume = self.__GetAttribute('fuelVolume')

        ro = math.sqrt(area / 4 / pi)
        ri = (ro**3 - volume * 3 / 4 / pi)**(1 / 3)

        self._fuelHollowSphereRo = ro
        self._fuelHollowSphereRi = ri

        return


# *******************************************************************************

# *******************************************************************************

# *******************************************************************************
# Setters and Getters methods
# -------------------------------------------------------------------------------
# These are passing arguments by value effectively. Because the python objects
# passed into/out of the function are immutable.

    def GetSpecs(self):
        return self._specs
    specs = property(GetSpecs, None, None, None)

    def GetFuelPhase(self):
        return self._fuelPhase
    fuelPhase = property(GetFuelPhase, None, None, None)

    def GetCladdingPhase(self):
        return self._claddingPhase
    claddingPhase = property(GetCladdingPhase, None, None, None)

    def GetAttribute(self, name, phase=None, symbol=None, series=None):
        return self.__GetAttribute(name, symbol, series)

    def ReduceCladdingVolume(self, dissolvedVolume):
        self.__ReduceCladdingVolume(dissolvedVolume)

    def ReduceFuelVolume(self, dissolvedVolume):
        self.__ReduceFuelVolume(dissolvedVolume)


# Get stored fuel slug property either overall or on a nuclide basis
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
# # of slugs

        if attributeName == 'nSlugs':
            return 1

# .................................................................................
# slugId

        if attributeName == 'slugType':
            return self._specs['Slug type']

# .................................................................................
# slug volume

        if attributeName == 'slugVolume':
            return __GetSlugVolume(self)

# .................................................................................
# fuel volume

        if attributeName == 'fuelVolume':
            return __GetFuelVolume(self)

# .................................................................................
# equivalent fuel volume

        if attributeName == 'equivalentFuelVolume':
            return __GetEquivalentFuelVolume(self)

# .................................................................................
# cladding volume

        if attributeName == 'claddingVolume':
            return __GetCladdingVolume(self)

# .................................................................................
# equivalent cladding volume

        if attributeName == 'equivalentCladdingVolume':
            return __GetEquivalentCladdingVolume(self)

# .................................................................................
# fuel area

        if attributeName == 'fuelArea':
            return __GetFuelArea(self)

# .................................................................................
# equivalent fuel area

        if attributeName == 'equivalentFuelArea':
            return __GetEquivalentFuelArea(self)

# .................................................................................
# cladding area

        if attributeName == 'claddingArea':
            return __GetCladdingArea(self)
        if attributeName == 'slugArea':
            return __GetCladdingArea(self)

# .................................................................................
# equivalent cladding area

        if attributeName == 'equivalentCladdingArea':
            return __GetEquivalentCladdingArea(self)

# .................................................................................
# fuel length

        if attributeName == 'fuelLength':
            return __GetFuelLength(self)

# .................................................................................
# fuel slug overall quantities
        if nuclide is None and series is None:

            # mass or mass concentration
            if attributeName == 'fuelMassCC' or attributeName == 'fuelMassDens' or attributeName == 'fuelMass':
                mass = self._fuelPhase.GetValue('mass')
                if attributeName == 'fuelMass':
                    return mass
                else:
                    #          volume = __GetFuelVolume( self )
                    volume = __GetEquivalentFuelVolume(self)
                    if volume == 0.0:
                        assert abs(
                            volume - self._fuelPhase.GetValue('volume')) < 1e-8
                        return mass
                    else:
                        assert abs(
                            volume - self._fuelPhase.GetValue('volume')) / volume * 100.0 < 0.1
                        return mass / volume
# mass or mass concentration
            if attributeName == 'claddingMassCC' or attributeName == 'claddingMassDens' or attributeName == 'claddingMass':
                mass = self._claddingPhase.GetValue('mass')
                if attributeName == 'claddingMass':
                    return mass
                else:
                    #          volume = __GetCladdingVolume( self )
                    volume = __GetEquivalentCladdingVolume(self)
                    if volume == 0.0:
                        assert abs(
                            volume - self._claddingPhase.GetValue('volume')) < 1e-8
                        return mass
                    else:
                        assert abs(
                            volume - self._claddingPhase.GetValue('volume')) / volume * 100.0 < 0.1
                        return mass / volume
# radioactivity
            if attributeName == 'radioactivtyDens' or attributeName == 'radioactivity':
                radioactivity = self._fuelPhase.GetValue('radioactivity')
                if attributeName == 'radioactivity':
                    return radioactivity
                else:
                    volume = __GetFuelVolume(self)
                    if volume == 0.0:
                        assert abs(
                            volume - self._fuelPhase.GetValue('volume')) < 1e-8
                        return radioactivity
                    else:
                        assert abs(
                            volume - self._fuelPhase.GetValue('volume')) / volume * 100.0 < 0.1
                        return radioactivity / volume
# gamma
            if attributeName == 'gammaDens' or attributeName == 'gamma':
                gammaDens = 0.0
                for spc in self._fuelPhase.species:
                    gammaDens += spc.molarGammaPwr * spc.molarCC
                if attributeName == 'gammaDens':
                    return gammaDens
                else:
                    volume = __GetFuelVolume(self)
                    return gammaDens * volume
# heat
            if attributeName == 'heatDens' or attributeName == 'heat':
                heatDens = 0.0
                for spc in self._fuelPhase.species:
                    heatDens += spc.molarHeatPwr * spc.molarCC
                if attributeName == 'heatDens':
                    return heatDens
                else:
                    volume = __GetFuelVolume(self)
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
#        volume = __GetFuelSlugVolume( self )
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
#        volume = __GetFuelSlugVolume( self )
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

                for spc in self._fuelPhase.species:

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

                return massCC * __GetFuelVolume(self)

        # chemical element given (only atomic number given)
            elif len(nuclide.split('-')) == 1:

                massCC = 0.0

                for spc in self._fuelPhase.species:

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

                return massCC * __GetFuelVolume(self)

            else:

                assert False

# ---------------------------------------------------------------------------------
    def __GetSlugLength(self):

        return self._specs['Slug length [cm]']

# ---------------------------------------------------------------------------------
    def __GetFuelLength(self):

        slugLength = __GetSlugLength(self)

        cladEndCapThickness = self._specs['Cladding end cap thickness [cm]']
        fuelLength = slugLength - 2.0 * cladEndCapThickness

        return fuelLength

# ---------------------------------------------------------------------------------
    def __GetSlugVolume(self):

        slugLength = __GetSlugLength(self)

        outerSlugOuterRadius = self._specs['Outer slug OD [cm]'] / 2.0
        outerSlugInnerRadius = self._specs['Outer slug ID [cm]'] / 2.0
        outerSlugVolume = slugLength * math.pi * \
            (outerSlugOuterRadius**2 - outerSlugInnerRadius**2)
        innerSlugOuterRadius = self._specs['Inner slug OD [cm]'] / 2.0
        innerSlugInnerRadius = self._specs['Inner slug ID [cm]'] / 2.0
        innerSlugVolume = slugLength * math.pi * \
            (innerSlugOuterRadius**2 - innerSlugInnerRadius**2)

        return outerSlugVolume + innerSlugVolume

# ---------------------------------------------------------------------------------
    def __GetFuelVolume(self):

        fuelLength = __GetFuelLength(self)

        cladWallThickness = self._specs['Cladding wall thickness [cm]']
        outerFuelOuterRadius = self._specs['Outer slug OD [cm]'] / \
            2.0 - cladWallThickness
        outerFuelInnerRadius = self._specs['Outer slug ID [cm]'] / \
            2.0 + cladWallThickness

        outerFuelVolume = fuelLength * math.pi * \
            (outerFuelOuterRadius**2 - outerFuelInnerRadius**2)

        innerFuelOuterRadius = self._specs['Inner slug OD [cm]'] / \
            2.0 - cladWallThickness
        innerFuelInnerRadius = self._specs['Inner slug ID [cm]'] / \
            2.0 + cladWallThickness

        innerFuelVolume = fuelLength * math.pi * \
            (innerFuelOuterRadius**2 - innerFuelInnerRadius**2)

        volume = outerFuelVolume + innerFuelVolume

        return volume

# ---------------------------------------------------------------------------------
    def __GetCladdingVolume(self):

        slugVolume = __GetSlugVolume(self)
        fuelVolume = __GetFuelVolume(self)

        return slugVolume - fuelVolume

# ---------------------------------------------------------------------------------
    def __GetFuelArea(self):

        pi = math.pi

        cladWallThickness = self._specs['Cladding wall thickness [cm]']
        slugLength = self._specs['Slug length [cm]']

        outerSlugFuelArea = 0.0

        # side walls
        outerSlugOuterRadius = self._specs['Outer slug OD [cm]'] / 2.0
        outerSlugFuelArea += 2.0 * pi * \
            (outerSlugOuterRadius - cladWallThickness) * slugLength
        outerSlugInnerRadius = self._specs['Outer slug ID [cm]'] / 2.0
        outerSlugFuelArea += 2.0 * pi * \
            (outerSlugInnerRadius + cladWallThickness) * slugLength
        # add bottom and top areas
        outerSlugFuelArea += 2.0 * pi * \
            ((outerSlugOuterRadius - cladWallThickness)**2 -
             (outerSlugInnerRadius + cladWallThickness)**2)

        innerSlugFuelArea = 0.0

        # side walls
        innerSlugOuterRadius = self._specs['Inner slug OD [cm]'] / 2.0
        innerSlugFuelArea += 2.0 * pi * \
            (innerSlugOuterRadius - cladWallThickness) * slugLength
        innerSlugInnerRadius = self._specs['Inner slug ID [cm]'] / 2.0
        innerSlugFuelArea += 2.0 * pi * \
            (innerSlugInnerRadius + cladWallThickness) * slugLength
        # add bottom and top areas
        innerSlugFuelArea += 2.0 * pi * \
            ((innerSlugOuterRadius - cladWallThickness)**2 -
             (innerSlugInnerRadius + cladWallThickness)**2)

        return outerSlugFuelArea + innerSlugFuelArea

# ---------------------------------------------------------------------------------
    def __GetCladdingArea(self):

        slugLength = self._specs['Slug length [cm]']

        outerSlugArea = 0.0

        # side walls
        outerSlugOuterRadius = self._specs['Outer slug OD [cm]'] / 2.0
        outerSlugArea += 2.0 * math.pi * outerSlugOuterRadius * slugLength
        outerSlugInnerRadius = self._specs['Outer slug ID [cm]'] / 2.0
        outerSlugArea += 2.0 * math.pi * outerSlugInnerRadius * slugLength
        # add bottom and top areas
        outerSlugArea += 2.0 * math.pi * \
            (outerSlugOuterRadius**2 - outerSlugInnerRadius**2)

        innerSlugArea = 0.0

        # side walls
        innerSlugOuterRadius = self._specs['Inner slug OD [cm]'] / 2.0
        innerSlugArea += 2.0 * math.pi * innerSlugOuterRadius * slugLength
        innerSlugInnerRadius = self._specs['Inner slug ID [cm]'] / 2.0
        innerSlugArea += 2.0 * math.pi * innerSlugInnerRadius * slugLength
        # add bottom and top areas
        innerSlugArea += 2.0 * math.pi * \
            (innerSlugOuterRadius**2 - innerSlugInnerRadius**2)

        return outerSlugArea + innerSlugArea

# ---------------------------------------------------------------------------------
    def __GetEquivalentCladdingArea(self):

        ro = self._claddingHollowSphereRo

        area = 4.0 * math.pi * ro

        return area

# ---------------------------------------------------------------------------------
    def __GetEquivalentCladdingVolume(self):

        ro = self._claddingHollowSphereRo
        ri = self._claddingHollowSphereRi

        volume = 4.0 / 3.0 * math.pi * (ro**3 - ri**3)

        return volume

# ---------------------------------------------------------------------------------
    def __GetEquivalentFuelVolume(self):

        ro = self._fuelHollowSphereRo
        ri = self._fuelHollowSphereRi

        volume = 4.0 / 3.0 * math.pi * (ro**3 - ri**3)

        return volume

# ---------------------------------------------------------------------------------
    def __GetEquivalentFuelArea(self):

        ro = self._fuelHollowSphereRo

        area = 4.0 * math.pi * ro

        return area


# *********************************************************************************
# Shrink the volume based on the equivalent cladding hollow sphere

# ---------------------------------------------------------------------------------

    def __ReduceCladdingVolume(self, dissolvedVolume):

        assert dissolvedVolume >= 0.0, 'dissolved volume= %r; failed.' % (
            dissolvedVolume)

        if dissolvedVolume == 0.0:
            return

        if self._claddingHollowSphereRo == self._claddingHollowSphereRi:
            return

        dV = dissolvedVolume
        pi = math.pi

        # get this first
        massDens = _GetAttribute(self, 'claddingMassDens')

# .................................................................................
# reduce the volume of the cladding hollow sphere

        ro = self._claddingHollowSphereRo
        ri = self._claddingHollowSphereRi

        volume = 4.0 / 3.0 * pi * (ro**3 - ri**3)

        if dV < volume:

            ro = (ri**3 + 3.0 / 4.0 / pi * (volume - dV))**(1 / 3)
            self._claddingHollowSphereRo = ro

        else:

            self._claddingHollowSphereRo = 0.0
            self._claddingHollowSphereRi = 0.0

            cladWallThickness = self._specs['Cladding wall thickness [cm]']
            cladEndCapThickness = self._specs['Cladding end cap thickness [cm]']

            self._specs['Inner slug ID [cm]'] += cladWallThickness
            self._specs['Inner slug OD [cm]'] -= cladWallThickness
            self._specs['Outer slug ID [cm]'] += cladWallThickness
            self._specs['Outer slug OD [cm]'] -= cladWallThickness

            self._specs['Slug length [cm]'] -= 2.0 * cladEndCapThickness

            self._specs['Cladding wall thickness [cm]'] = 0.0
            self._specs['Cladding end cap thickness [cm]'] = 0.0

# .................................................................................
# Update the history of the cladding phase

        volume = _GetAttribute(self, 'equivalentCladdingVolume')
        self._claddingPhase.SetValue('volume', volume)

        self._claddingPhase.SetValue('mass', massDens * volume)


# ---------------------------------------------------------------------------------

    def __ReduceFuelVolume(self, dissolvedVolume):

        assert dissolvedVolume >= 0.0, 'dissolved volume= %r; failed.' % (
            dissolvedVolume)

        if dissolvedVolume == 0.0:
            return

        if self._fuelHollowSphereRo == self._fuelHollowSphereRi:
            return

        assert self._claddingHollowSphereRo == 0.0
        assert self._claddingHollowSphereRi == 0.0

        dV = dissolvedVolume
        pi = math.pi

        # get this first
        massDens = _GetAttribute(self, 'fuelMassDens')

# .................................................................................
# reduce the volume of the fuel hollow sphere

        ro = self._fuelHollowSphereRo
        ri = self._fuelHollowSphereRi

        volume = 4.0 / 3.0 * pi * (ro**3 - ri**3)

        if dV < volume:

            ro = (ri**3 + 3.0 / 4.0 / pi * (volume - dV))**(1 / 3)
            self._fuelHollowSphereRo = ro

        else:

            self._fuelHollowSphereRo = 0.0
            self._fuelHollowSphereRi = 0.0

            self._specs['Inner slug ID [cm]'] = 0.0
            self._specs['Inner slug OD [cm]'] = 0.0
            self._specs['Outer slug ID [cm]'] = 0.0
            self._specs['Outer slug OD [cm]'] = 0.0

            self._specs['Slug length [cm]'] = 0.0

            self._specs['Cladding wall thickness [cm]'] = 0.0
            self._specs['Cladding end cap thickness [cm]'] = 0.0

# .................................................................................
# Update the history of the fuel phase

        volume = _GetAttribute(self, 'equivalentFuelVolume')
        self._fuelPhase.SetValue('volume', volume)

        self._fuelPhase.SetValue('mass', massDens * volume)


# *********************************************************************************


# *******************************************************************************
# Printing of data members

    def __str__(self):
        s = 'FuelSlug(): \n\t specs \n\t %s \n\t fuelPhase \n\t %s \n\t claddingPhase \n\t %s'
        return s % (self._specs, self._fuelPhase, self._claddingPhase)

    def __repr__(self):
        s = 'FuelSlug(): \n\t specs \n\t %s \n\t fuelPhase \n\t %s \n\t claddingPhase \n\t %s'
        return s % (self._specs, self._fuelPhase, self._claddingPhase)
# *******************************************************************************
