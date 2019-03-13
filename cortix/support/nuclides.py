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
"""
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

Nuclides container.
The purpose of the this container is to store and query a table of nuclides.
Typically the table is filled in with data from an ORIGEN calculation or
some other fission/transmutation code.

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
# *******************************************************************************

# *******************************************************************************


class Nuclides():

    def __init__(self,
                 propertyDensities=pandas.DataFrame()
                 ):

        assert isinstance(
            propertyDensities, type(
                pandas.DataFrame())), 'fatal.'

        self.attributeNames = \
            ['nuclides',
             'isotopes',
             'massDens',
             'massCC',
             'radioactivityDens',
             'thermalDens',
             'heatDens',
             'gammaDens']

        self.chemicalElementSeries = \
            ['alkali metals', 'alkali earth metals', 'lanthanides', 'actinides',
             'transition metals', 'noble gases', 'metalloids', 'fission products', 'nonmetals',
             'oxide fission products', 'halogens', 'minor actinides', 'volatile fission products', 'poor metals']

        self.propertyDensities = propertyDensities

        return

# *******************************************************************************
# Setters and Getters methods
# -------------------------------------------------------------------------------
# These are passing arguments by value effectively. Because the python objects
# passed into/out of the function are immutable.

    def GetAttribute(self, name, symbol=None, series=None):
        return self.__GetAttribute(name, symbol, series)


# *********************************************************************************

# Get property either overall or on a nuclide basis

# ---------------------------------------------------------------------------------

    def __GetAttribute(self, attributeName, symbol=None, series=None):

        assert attributeName in self.attributeNames, ' attribute name: %r; options: %r; fail.' % (
            attributeName, self.attributeNames)

        if symbol is not None:
            assert series is None, 'fail.'
        if series is not None:
            assert symbol is None, 'fail.'

        if attributeName == 'isotopes':
            assert symbol is not None, 'need an element symbol.'

# .................................................................................
# isotopes python list

        if attributeName == 'isotopes':

            nuclidesNames = self.propertyDensities.index
            isotopes = [x for x in nuclidesNames if x.split(
                '-')[0].strip() == symbol]
            return isotopes

# .................................................................................
# nuclides python list

        if attributeName == 'nuclides':

            if series is not None:
                # CREATE A HELPER FUNCTION FOR THIS; NOTE THIS IS USED BELOW
                # TOO!!!
                nuclidesNames = self.propertyDensities.index

                seriesNameMap = {
                    'alkali metals': 'Alkali metals',
                    'alkali earth metals': 'Alkaline earth metals',
                    'lanthanides': 'Lanthanides',
                    'actinides': 'Actinides',
                    'transition metals': 'Transition metals',
                    'noble gases': 'Noble gases',
                    'metalloids': 'Metalloids',
                    'fission products': 'fission products',
                    'nonmetals': 'Nonmetals',
                    'oxide fission products': 'oxide fission products',
                    'halogens': 'Halogens',
                    'minor actinides': 'minor actnides',
                    'volatile fission products': 'volatile fission products',
                    'poor metals': 'Poor metals'}
                #
                if series == 'fission products':
                    nuclides = [x for x in nuclidesNames if SERIES[ELEMENTS[x.split(
                        '-')[0].strip()].series] != seriesNameMap['actinides']]
                #
                elif series == 'oxide fission products':
                    collec = [seriesNameMap['actinides'],
                              seriesNameMap['halogens'],
                              seriesNameMap['noble gases']
                              ]
                    nuclides = [x for x in nuclidesNames if SERIES[ELEMENTS[x.split(
                        '-')[0].strip()].series] not in collec]
                    collec = ['C', 'N', 'O', 'H']
                    nuclides = [x for x in nuclides if x.split(
                        '-')[0].strip() not in collec]
                #
                elif series == 'volatile fission products':
                    collec = [seriesNameMap['actinides'],
                              seriesNameMap['alkali metals'],
                              seriesNameMap['alkali earth metals'],
                              seriesNameMap['lanthanides'],
                              seriesNameMap['metalloids'],
                              seriesNameMap['transition metals'],
                              seriesNameMap['poor metals']
                              ]
                    nuclides = [x for x in nuclidesNames if SERIES[ELEMENTS[x.split(
                        '-')[0].strip()].series] not in collec]
                    collec = ['C', 'O']
                    nuclides = [x for x in nuclides if x.split(
                        '-')[0].strip() not in collec]
                #
                elif series == 'minor actinides':
                    nuclides = [x for x in nuclidesNames if SERIES[ELEMENTS[x.split(
                        '-')[0].strip()].series] == seriesNameMap['actinides']]
                    collec = ['U', 'Pu']
                    nuclides = [x for x in nuclides if x.split(
                        '-')[0].strip() not in collec]
                #
                else:
                    nuclides = [x for x in nuclidesNames if SERIES[ELEMENTS[x.split(
                        '-')[0].strip()].series] == seriesNameMap[series]]

                return nuclides

            if series is None:

                nuclidesNames = self.propertyDensities.index
                return list(nuclidesNames)

# .................................................................................
# mass or mass concentration

        if attributeName == 'massCC':
            colName = 'Mass CC [g/cc]'

# .................................................................................
# radioactivity

        if attributeName == 'radioactivityDens':
            colName = 'Radioactivity Dens. [Ci/cc]'

# .................................................................................
# thermal

        if attributeName == 'thermalDens' or attributeName == 'heatDens':
            colName = 'Thermal Dens. [W/cc]'

# .................................................................................
# gamma

        if attributeName == 'gammaDens':
            colName = 'Gamma Dens. [W/cc]'

# .................................................................................
##########################################################################
# .................................................................................

# .................................................................................
# all nuclide content added

        if symbol is None and series is None:

            density = 0.0
            density = self.propertyDensities[colName].sum()
            return float(density)  # avoid numpy.float64 type

# .................................................................................
# get chemical element series

        if series is not None:

            density = 0.0

            assert series in self.chemicalElementSeries, 'series: %r; fail.' % (
                series)

            seriesNameMap = {
                'alkali metals': 'Alkali metals',
                'alkali earth metals': 'Alkaline earth metals',
                'lanthanides': 'Lanthanides',
                'actinides': 'Actinides',
                'transition metals': 'Transition metals',
                'noble gases': 'Noble gases',
                'metalloids': 'Metalloids',
                'fission products': 'fission products',
                'nonmetals': 'Nonmetals',
                'oxide fission products': 'oxide fission products',
                'halogens': 'Halogens',
                'minor actinides': 'minor actnides',
                'volatile fission products': 'volatile fission products',
                'poor metals': 'Poor metals'}

            if series in self.chemicalElementSeries:

                nuclidesNames = self.propertyDensities.index
                #
                if series == 'fission products':
                    nuclides = [x for x in nuclidesNames if SERIES[ELEMENTS[x.split(
                        '-')[0].strip()].series] != seriesNameMap['actinides']]
                #
                elif series == 'oxide fission products':
                    collec = [seriesNameMap['actinides'],
                              seriesNameMap['halogens'],
                              seriesNameMap['noble gases']
                              ]
                    nuclides = [x for x in nuclidesNames if SERIES[ELEMENTS[x.split(
                        '-')[0].strip()].series] not in collec]
                    collec = ['C', 'N', 'O', 'H']
                    nuclides = [x for x in nuclides if x.split(
                        '-')[0].strip() not in collec]
                #
                elif series == 'volatile fission products':
                    collec = [seriesNameMap['actinides'],
                              seriesNameMap['alkali metals'],
                              seriesNameMap['alkali earth metals'],
                              seriesNameMap['lanthanides'],
                              seriesNameMap['metalloids'],
                              seriesNameMap['transition metals'],
                              seriesNameMap['poor metals']
                              ]
                    nuclides = [x for x in nuclidesNames if SERIES[ELEMENTS[x.split(
                        '-')[0].strip()].series] not in collec]
                    collec = ['C', 'O']
                    nuclides = [x for x in nuclides if x.split(
                        '-')[0].strip() not in collec]
                #
                elif series == 'minor actinides':
                    nuclides = [x for x in nuclidesNames if SERIES[ELEMENTS[x.split(
                        '-')[0].strip()].series] == seriesNameMap['actinides']]
                    collec = ['U', 'Pu']
                    nuclides = [x for x in nuclides if x.split(
                        '-')[0].strip() not in collec]
                #
                else:
                    nuclides = [x for x in nuclidesNames if SERIES[ELEMENTS[x.split(
                        '-')[0].strip()].series] == seriesNameMap[series]]

#       print('fission products ',nuclides)

                for nuclide in nuclides:
                    density += self.propertyDensities.loc[nuclide, colName]

            return float(density)  # avoid numpy.float64 type

# .................................................................................
# get specific nuclide (either the isotopes of the nuclide or the specific
# isotope) property

        if symbol is not None:

            density = 0.0

        # single isotope
            if len(symbol.split('-')) == 2:
                density = self.propertyDensities.loc[symbol, colName]

        # many isotopes
            else:
                nuclidesNames = self.propertyDensities.index
#    print(self.propertyDensities)
                isotopes = [
                    x for x in nuclidesNames if x.split('-')[0].strip() == symbol]
#    print(isotopes)
                for isotope in isotopes:
                    density += self.propertyDensities.loc[isotope, colName]

            return float(density)  # avoid numpy.float64.type

# *********************************************************************************

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
