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
Fuel segment
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda
Sat Jun 27 14:46:49 EDT 2015
'''
#*********************************************************************************
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
#*********************************************************************************

class FuelSegment():

    # TODO: Species should not be here. Need to replace by Phase instead.
    #      Chopper will be affected

#*********************************************************************************
# Construction
#*********************************************************************************

    def __init__(self,
                 geometry = pandas.Series(),
                 species = list()
                 ):

        assert isinstance(geometry, pandas.Series), 'fatal.'
        assert isinstance(species, list), 'fatal.'
        if isinstance(species, list) and len(species) > 0:
            assert isinstance(species[0], Specie)

        self.attribute_names = \
            ['n-segments',
             'fuel-volume',
             'segment-volume',
             'fuel-diameter',
             'fuel-length',
             'mass',
             'mass-dens',
             'mass-cc',
             'nuclides',
             'isotopes',
             'radioactivity',
             'radioactivity-dens',
             'gamma',
             'gamma-dens',
             'heat',
             'heat-dens',
             'molar-heat-pwr',
             'molar-gamma-pwr']

        self.__geometry = geometry
        self.__species  = species

#*********************************************************************************
# Public Member Functions
#*********************************************************************************

    def get_geometry(self):

        '''
        Returns the geometry of the fuel bundle (cylindrical, hexoganol,
        rectangular, etc).

        Returns
        -------
        geometry: pandas.series
        '''

        return self.__geometry
    geometry = property(get_geometry, None, None, None)

    def get_species(self):
        '''
        Returns the list containing all the specie objects that make up the
        fuel bundle.
<<<<<<< HEAD:cortix/support/fuel_segment.py

        Parameters
        ----------
        Empty:
=======
>>>>>>> master:cortix/support/nuclear/fuel_segment.py

        Returns
        -------
        species: list of objects
        '''

        return self.__species
    species = property(get_species, None, None, None)

    def get_specie(self, name):
        '''
        Returns a specie named [name] from the list of species making up the
        fuel bundle. If no name is specified, this function will return None.

        Parameters
        ----------
        name: str

        Returns
        -------
        specie: obj
        '''

        for specie in self.__species:
            if specie.name == name:
                return specie
        return None
    specie = property(get_specie, None, None, None)

# Get stored fuel segment property either overall or on a nuclide basis
    def get_attribute(self, name, nuclide=None, series=None):

        '''
        Used to get stored fuel segment properties, either overall (as an
        average), or on a nuclide basis. "name" in this case refers to the
        attribute in question. At this point in time, series is not implemented
        and passing it to this function will result in an error. Possible
        attributes that may be retrieved with this function, as well as the
        name to pass to this function to retrieve them are: number of segments
        in the bundle (n-segments, always equal to 1), the id of the segment
        that makes up the bundle (segment-id), the volume of the fuel in the
        bundle  (fuel-volume), the total volume of the segment
        (segment-volume), the diameter (fuel-diameter) and length
        (fuel-length) of the segment, the mass or mass density of the segment
        (mass or mass-cc, respectively), or the total or per-volume
        radioactivity, gamma radiation density or heat density of the fuel
        segment (radioactivity and radioactivityDens, gamma and gamma-dens,
        and heat and heat-dens, respectively).

        Finally, density or total mass of a specific nuclide can be determined
        by passing a specific nuclide to the function, with a name value of
        mass or mass-cc.

        Parameters
        ----------
        name: str
        nuclide: str

        Returns
        -------
        many types
        '''

        attribute_name = name

        assert attribute_name in self.attribute_names, \
               'attribute_name: %r; options: %r; fail.' % \
               (attribute_name, self.attribute_names)

        if nuclide is not None:
            assert isinstance(nuclide,str), 'type(nuclide) = %r' % type(nuclide)
            # no multipliers for now (see below: codes is almost ready for it)
            assert len(nuclide.split('*')) == 1, 'nuclide = %r' % nuclide # sanity check

        if nuclide is not None:
            assert series is None, 'fail.'
        if series is not None:
            assert nuclide is None, 'fail.'

        if series is not None:
            assert False, ' not implemented.'

        if attribute_name == 'isotopes':
            assert nuclide is not None, 'need a nuclide symbol.'

# .................................................................................
# # of segments

        if attribute_name == 'n-segments':
            return 1

# .................................................................................
# segment id

        if attribute_name == 'segment-id':
            return self.__geometry['segment id']

# .................................................................................
# fuel volume

        if attribute_name == 'fuel-volume':
            return self.__get_fuel_segment_volume()
# .................................................................................
# segment volume

        if attribute_name == 'segment-volume':

            cladding_length = self.__geometry['cladding length [cm]']
            cladding_diam = self.__geometry['OD [cm]']
            volume = cladding_length * math.pi * (cladding_diam / 2.0)**2
            return volume

# .................................................................................
# fuel diameter

        if attribute_name == 'fuel-diameter':

            fuel_diam = self.__geometry['fuel diameter [cm]']
            return fuel_diam

# .................................................................................
# fuel length

        if attribute_name == 'fuel-length':

            fuel_length = self.__geometry['fuel length [cm]']
            return fuel_length

# .................................................................................
# fuel segment overall quantities
        if nuclide is None and series is None:

            # mass or mass concentration
            if attribute_name == 'mass-cc' or attribute_name == 'mass-dens' or attribute_name == 'mass':
                mass_cc = 0.0
                for spc in self.__species:
                    mass_cc += spc.massCC
                if attribute_name == 'mass-cc' or attribute_name == 'mass-dens':
                    return mass_cc
                else:
                    volume = self.__get_fuel_segment_volume()
                    return mass_cc * volume
# radioactivity
            if attribute_name == 'radioactivtyDens' or attribute_name == 'radioactivity':
                radDens = 0.0
                for spc in self.__species:
                    radDens += spc.molarRadioactivity * spc.molarCC
                if attribute_name == 'radioactivity-dens':
                    return radDens
                else:
                    volume = self.__get_fuel_segment_volume()
                    return radDens * volume
# gamma
            if attribute_name == 'gamma-dens' or attribute_name == 'gamma':
                gamma_dens = 0.0
                for spc in self.__species:
                    gamma_dens += spc.molarGammaPwr * spc.molarCC
                if attribute_name == 'gamma-dens':
                    return gamma_dens
                else:
                    volume = self.__get_fuel_segment_volume()
                    return gamma_dens * volume
# heat
            if attribute_name == 'heat-dens' or attribute_name == 'heat':
                heat_dens = 0.0
                for spc in self.__species:
                    heat_dens += spc.molarHeatPwr * spc.molarCC
                if attribute_name == 'heat-dens':
                    return heat_dens
                else:
                    volume = self.__get_fuel_segment_volume()
                    return heat_dens * volume

# .................................................................................
# radioactivity

        if attribute_name == 'radioactivity-dens' or attribute_name == 'radioactivity':
            assert False
            colName = 'Radioactivity Dens. [Ci/cc]'

# .................................................................................
# thermal

        if attribute_name == 'thermalDens' or attribute_name == 'thermal' or  \
           attribute_name == 'heat-dens' or attribute_name == 'heat':
            assert False
            colName = 'Thermal Dens. [W/cc]'

# .................................................................................
# gamma

        if attribute_name == 'gamma-dens' or attribute_name == 'gamma':
            assert False
            colName = 'Gamma Dens. [W/cc]'

# .................................................................................
##########################################################################
# .................................................................................

#  if attribute_name[-4:] == 'Dens' or attribute_name[-2:] == 'CC':
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
#        volume = self.__get_fuel_segment_volume()
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
#        volume = self.__get_fuel_segment_volume()
#        prop = density * volume
#        return prop
#     else:
#        return density

# .................................................................................
# get specific nuclide (either the isotopes of the nuclide or the specific
# isotope) property: note the most complex case handled is, say: 2*Cs-133.

        if nuclide is not None:

            # a particular nuclide given (atomic number and atomic mass number)
            if len(nuclide.split('-')) == 2:

                nuclideMassNumber = int(nuclide.split('-')[1].strip('m'))
                nuclideSymbol = nuclide.split('-')[0]
                nuclideMolarMass = ELEMENTS[nuclideSymbol].isotopes[nuclideMassNumber].mass

                mass_cc = 0.0

                for spc in self.__species:

                    formula = spc.atoms

                    mole_fraction = 0.0

                    for item in formula:

                        if len(item.split('*')
                               ) == 1:  # no multiplier (implies 1.0)

                            formula_nuclide_symbol = item.split('-')[0].strip()
                            if formula_nuclide_symbol == nuclideSymbol:
                                assert len(item.split('-')) == 2

                            if item.split('*')[0].strip() == nuclide:
                                mole_fraction = 1.0
                            else:
                                mole_fraction = 0.0

                        elif len(item.split('*')) == 2:  # with multiplier

                            formula_nuclide_symbol = item.split(
                                '*')[1].split('-')[0].strip()
                            if formula_nuclide_symbol == nuclideSymbol:
                                assert len(item.split('*')[1].split('-')) == 2

                            if item.split('*')[1].strip() == nuclide:
                                mole_fraction = float(
                                    item.split('*')[0].strip())
                            else:
                                mole_fraction = 0.0

                        else:
                            assert False

                        mass_cc += spc.molarCC * mole_fraction * nuclideMolarMass

                return mass_cc * self.__get_fuel_segment_volume()

        # chemical element given (only atomic number given)
            elif len(nuclide.split('-')) == 1:

                mass_cc = 0.0

                for spc in self.__species:

                    formula = spc.atoms

                    for item in formula:

                        mole_fraction = 0.0

                        if len(item.split('*')
                               ) == 1:  # no multiplier (implies 1.0)

                            assert len(item.split('-')) == 2
                            formula_nuclide_symbol = item.split('-')[0].strip()
                            formula_nuclide_mass_number = int(
                                item.split('-')[1].strip('m'))
                            formula_nuclide_molar_mass = ELEMENTS[formula_nuclide_symbol].isotopes[formula_nuclide_mass_number].mass

                            if formula_nuclide_symbol == nuclide:
                                mole_fraction = 1.0
                            else:
                                mole_fraction = 0.0

                        elif len(item.split('*')) == 2:  # with multiplier

                            assert len(item.split('*')[1].split('-')) == 2
                            formula_nuclides_symbol = item.split(
                                '*')[1].split('-')[0].strip()
                            formula_nuclide_mass_number = int(
                                item.split('*')[1].split('-')[1].strip('m'))
                            formula_nuclide_molar_mass = \
                                    ELEMENTS[formula_nuclides_symbol].isotopes[formula_nuclide_mass_number].mass

                            if formula_nuclides_symbol == nuclide:
                                mole_fraction = float(
                                    item.split('*')[0].strip())
                            else:
                                mole_fraction = 0.0

                        else:
                            assert False

                        mass_cc += spc.molarCC * mole_fraction * formula_nuclide_molar_mass

                return mass_cc * self.__get_fuel_segment_volume()

            else:

                assert False

#**********************************************************************************
# Private Helper Functions (internal use: __)
#*********************************************************************************

    def __get_fuel_segment_volume(self):

        '''
        Returns the total volume of fuel in the fuel segment.

        Returns
        -------
        volume: float
        '''

        fuel_length = self.__geometry['fuel length [cm]']
        fuel_diam = self.__geometry['fuel diameter [cm]']

        volume = fuel_length * math.pi * (fuel_diam / 2.0)**2

        return volume

    def __str__(self):
        '''
        Used to print the geometry of the fuel segment and the species that it
        consists of.

        Returns
        -------
        s: str
        '''

        s = 'FuelSegment(): %s\n %s\n'
        return s % (self.__geometry, self.__species)

    def __repr__(self):
        '''
        Used to print the geometry of the fuel segment and the species that it
        consists of.

        Returns
        -------
        s: str
        '''

        s = 'FuelSegment(): %s\n %s\n'
        return s % (self.__geometry, self.__species)

#============================ end class FuelSegment ==============================
