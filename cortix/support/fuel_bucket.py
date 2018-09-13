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
This FuelBucket class is a container for usage with other plant-level process modules.
It is meant to represent a fuel bucket of a metal fuel reactor.
----------
ATTENTION:
----------
This container uses Phase() for phases (cladding and fuel). Therefore user is
responsible to make the "history" of the phases consistent. See Phase() info.

Author: Valmor de Almeida dealmeidav@ornl.gov; vfda
"""
#*************************************************************************
import os
import sys
import math
import pandas
from copy import deepcopy
#*************************************************************************

class FuelBucket():

    def __init__(self,
                 specs=pandas.DataFrame()
                ):

        assert isinstance(specs, pandas.DataFrame), 'oops not pandas table.'

        self.__specs = specs

        self.__solid_phase = None

        self.__fuel_phase = None
        self.__cladding_phase = None

        return
 # ---------------------- end def __init__():------------------------------

    #------
    # Start: Pre-irradiation information

    def get_name(self):
        return self.__specs.loc['Name', 1]
    name = property(get_name, None, None, None)

    def get_slug_type(self):
        return self.__specs.loc['Slug type', 1]
    slug_type = property(get_slug_type, None, None, None)

    def get_n_slugs(self):
        return self.__get_n_slugs()
    n_slugs = property(get_n_slugs, None, None, None)

    def get_fuel_enrichment(self):
        return self.__get_fuel_enrichment()
    fuel_enrichment = property(get_fuel_enrichment, None, None, None)

    def get_fresh_u_mass(self):
        return self.__get_fresh_u_mass()
    fresh_u_mass = property(get_fresh_u_mass, None, None, None)

    def get_fresh_u238_mass(self):
        return self.__get_fresh_u238_mass()
    fresh_u238_mass = property(get_fresh_u238_mass, None, None, None)

    def get_fresh_u235_mass(self):
        return self.__GetFreshU235UMass()
    fresh_u235_mass = property(get_fresh_u235_mass, None, None, None)

    def get_cladding_mass(self):
        return self.__get_cladding_mass()
    cladding_mass = property(get_cladding_mass, None, None, None)

    # End: Pre-irradiation information
    #------

    def get_slug_length(self):
        return self.__get_slug_length()

    def set_slug_length(self, x):
        self.__set_slug_length(x)
    slug_length = property(get_slug_length, set_slug_length, None, None)

    def get_outer_slug_od(self):
        return self.__get_outer_slug_od()
    outer_slug_od = property(get_outer_slug_od, None, None, None)

    def get_outer_slug_id(self):
        return self.__get_outer_slug_id()
    outer_slug_id = property(get_outer_slug_id, None, None, None)

    def get_inner_slug_od(self):
        return self.__get_inner_slug_od()
    inner_slug_od = property(get_inner_slug_od, None, None, None)

    def get_inner_slug_id(self):
        return self.__get_inner_slug_id()
    inner_slug_id = property(get_inner_slug_id, None, None, None)

    def get_cladding_wall_thickness(self):
        return self.__get_cladding_wall_thickness()
    cladding_wall_thickness = property(
        get_cladding_wall_thickness, None, None, None)

    def get_cladding_end_thickness(self):
        return self.__get_cladding_end_thickness()
    cladding_end_thickness = property(get_cladding_end_thickness, None, None, None)

    def get_slug_fuel_volume(self): return self.__get_slug_fuel_volume()
    slug_fuel_volume = property(get_slug_fuel_volume, None, None, None)

    def get_fuel_volume(self):
        return self.__get_fuel_volume()
    fuel_volume = property(get_fuel_volume, None, None, None)

    def get_slug_cladding_volume(self):
        return self.__get_slug_cladding_volume()
    slug_cladding_volume = property(get_slug_cladding_volume, None, None, None)

    def get_cladding_volume(self):
        return self.__get_cladding_volume()
    cladding_volume = property(get_cladding_volume, None, None, None)

    def get_fuel_mass(self):
        return self.__fuel_phase.GetValue('mass') # mass of the solid phase
    fuel_mass = property(get_fuel_mass, None, None, None)

    def get_fuel_mass_unit(self):
        return self.__fuel_phase.GetQuantity('mass').unit # mass of the solid phase
    fuel_mass_unit = property(get_fuel_mass_unit, None, None, None)

    def get_radioactivity(self):   # radioactivity of the fuel bucket (fix me)
        return self.__fuel_phase.GetValue('radioactivity')
    radioactivity = property(get_radioactivity, None, None, None)

    def get_gamma_pwr(self):
        return self.__fuel_phase.GetValue('gamma')   # gamma pwr of the fuel bucket
    gamma_pwr = property(get_gamma_pwr, None, None, None)

    def get_heat_pwr(self):
        return self.__fuel_phase.GetValue('heat')   # heat pwr of the fuel bucket
    heat_pwr = property(get_heat_pwr, None, None, None)

    def get_fuel_radioactivity(self):         # radioactivity of the solid phase
        return self.__fuel_phase.GetValue('radioactivity')
    fuel_radioactivity = property(get_fuel_radioactivity, None, None, None)

    def get_fuel_phase(self):
        return self.__fuel_phase

    def set_fuel_phase(self, phase):
        self.__fuel_phase = deepcopy(phase)
    fuel_phase = property(get_fuel_phase, set_fuel_phase, None, None)

    def get_cladding_phase(self):
        return self.__cladding_phase

    def set_cladding_phase(self, phase):
        self.__cladding_phase = deepcopy(phase)
    cladding_phase = property(get_cladding_phase, set_cladding_phase, None, None)

# *********************************************************************************
# Private helper functions (internal use: __)

    def __get_n_slugs(self):
        return int(self.__specs.loc['Number of slugs', 1])

    def __get_fuel_enrichment(self):
        return float(self.__specs.loc['Enrichment [U-235 wt%]', 1])

    def __get_outer_slug_fresh_u_mass(self):
        return float(
            self.__specs.loc['U mass outer slug [kg]', 1]) * 1000.0  # [g]

    def __get_inner_slug_fresh_u_mass(self):
        return float(
            self.__specs.loc['U mass inner slug [kg]', 1]) * 1000.0  # [g]

    def __get_outer_slug_cladding_mass(self):
        return float(
            self.__specs.loc['Cladding mass outer slug [kg]', 1]) * 1000.0  # [g]

    def __get_inner_slug_cladding_mass(self):
        return float(
            self.__specs.loc['Cladding mass inner slug [kg]', 1]) * 1000.0  # [g]

    def __get_fresh_u_mass(self):
        n_slugs = self.__get_n_slugs()
        uMassOuterSlug = self.__get_outer_slug_fresh_u_mass()
        uMassInnerSlug = self.__get_inner_slug_fresh_u_mass()
        return n_slugs * (uMassOuterSlug + uMassInnerSlug)

    def __get_fresh_u238_mass(self):
        totalUMass = self.__get_fresh_u_mass()
        fuelEnrichment = self.__get_fuel_enrichment()
        return totalUMass * (1.0 - fuelEnrichment / 100.0)

    def __get_fresh_u235_mass(self):
        totalUMass = self.__get_fresh_u_mass()
        fuelEnrichment = self.__get_fuel_enrichment()
        return totalUMass * fuelEnrichment / 100.0

    def __get_cladding_mass(self):
        n_slugs = self.__get_n_slugs()
        cladMassOuterSlug = self.__get_outer_slug_cladding_mass()
        cladMassInnerSlug = self.__get_inner_slug_cladding_mass()
        return n_slugs * (cladMassOuterSlug + cladMassInnerSlug)

    def __get_slug_length(self):
        return float(self.__specs.loc['Slug length [in]', 1]) * 2.54  # cm

    def __set_slug_length(self, x):
        self.__specs.loc['Slug length [in]', 1] = x / 2.54  # in
        return

    def __get_outer_slug_od(self):
        return float(self.__specs.loc['Outer slug O.D. [in]', 1]) * 2.54  # cm

    def __get_outer_slug_id(self):
        return float(self.__specs.loc['Outer slug I.D. [in]', 1]) * 2.54  # cm

    def __get_inner_slug_od(self):
        return float(self.__specs.loc['Inner slug O.D. [in]', 1]) * 2.54  # cm

    def __get_inner_slug_id(self):
        return float(self.__specs.loc['Inner slug I.D. [in]', 1]) * 2.54  # cm

    def __get_cladding_wall_thickness(self):
        return float(
            self.__specs.loc['Cladding wall thickness [mm]', 1]) / 10.0  # cm

    def __get_cladding_end_thickness(self):
        return float(
            self.__specs.loc['Cladding end cap thickness [mm]', 1]) / 10.0  # cm

    def __get_slug_fuel_volume(self):
        slugLength = self.__get_slug_length()
        cladWallThickness = self.__get_cladding_wall_thickness()
        cladEndThickness = self.__get_cladding_end_thickness()
        fuelLength = slugLength - 2.0 * cladEndThickness
        fuelOuterSlugOuterRadius = self.__get_outer_slug_od() / 2.0 - cladWallThickness
        fuelOuterSlugInnerRadius = self.__get_outer_slug_id() / 2.0 + cladWallThickness
        outerVolume = fuelLength * math.pi * \
            (fuelOuterSlugOuterRadius**2 - fuelOuterSlugInnerRadius**2)
        fuelInnerSlugOuterRadius = self.__get_inner_slug_od() / 2.0 - cladWallThickness
        fuelInnerSlugInnerRadius = self.__get_inner_slug_id() / 2.0 + cladWallThickness
        innerVolume = fuelLength * math.pi * \
            (fuelInnerSlugOuterRadius**2 - fuelInnerSlugInnerRadius**2)
        return outerVolume + innerVolume

    def __get_slug_volume(self):
        slugLength = self.__get_slug_length()
        outerSlugOuterRadius = self.__get_outer_slug_od() / 2.0
        outerSlugInnerRadius = self.__get_outer_slug_id() / 2.0
        outerVolume = slugLength * math.pi * \
            (outerSlugOuterRadius**2 - outerSlugInnerRadius**2)
        innerSlugOuterRadius = self.__get_inner_slug_od() / 2.0
        innerSlugInnerRadius = self.__get_inner_slug_id() / 2.0
        innerVolume = slugLength * math.pi * \
            (innerSlugOuterRadius**2 - innerSlugInnerRadius**2)
        return outerVolume + innerVolume

    def __get_slug_cladding_volume(self):
        return self.__get_slug_volume() - self.__get_slug_fuel_volume()

    def __get_fuel_volume(self):
        slugFuelVolume = self.__get_slug_fuel_volume()
        nFuelSlugs = self.__get_n_slugs()
        return slugFuelVolume * nFuelSlugs

    def __get_cladding_volume(self):
        slugCladdingVolume = self.__get_slug_cladding_volume()
        nFuelSlugs = self.__get_n_slugs()
        return slugCladdingVolume * nFuelSlugs

#*************************************************************************
# Printing of data members
    def __str__(self):
        s = '\nFuelBucket():\n\t*******\n\t specs:\n\t*******\n\t %s\n'
        t = '\t************\n\t fuel_phase:\n\t**********\n\t %s\n'
        u = '\t***************\n\t cladding_phase:\n\t*****************\n\t %s\n'
        stu = s + t + u
        return stu % (self.__specs, self.__fuel_phase, self.__cladding_phase)

    def __repr__(self):
        s = '\nFuelBucket():\n\t*******\n\t specs:\n\t*******\n\t %s\n'
        t = '\t************\n\t fuel_phase:\n\t**********\n\t %s\n'
        u = '\t****************\n\t cladding_phase:\n\t****************\n\t %s\n'
        stu = s + t + u
        return stu % (self.__specs, self.__fuel_phase, self.__cladding_phase)

# ====================== end class FuelBucket: ===================================
