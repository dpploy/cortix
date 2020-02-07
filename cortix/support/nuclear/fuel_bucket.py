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
This FuelBucket class is a container for usage with other plant-level process modules.
It is meant to represent a fuel bucket of a metal fuel reactor.
----------
ATTENTION:
----------
This container uses Phase() for phases (cladding and fuel). Therefore user is
responsible to make the "history" of the phases consistent. See Phase() info.

Author: Valmor de Almeida dealmeidav@ornl.gov; vfda
'''
#*********************************************************************************
import os
import sys
import math
import pandas
from copy import deepcopy
#*********************************************************************************

class FuelBucket():

#*********************************************************************************
# Construction
#*********************************************************************************

    def __init__(self,
                 specs=pandas.DataFrame()
                ):

        assert isinstance(specs, pandas.DataFrame), 'oops not pandas table.'

        self.__specs = specs

        self.__solid_phase = None

        self.__fuel_phase = None
        self.__cladding_phase = None

        return

#**********************************************************************************
# Public Member Functions
#**********************************************************************************

    # Start: Pre-irradiation information

    def get_name(self):

        '''
        Returns the name of the fuel bucket.

        Returns
        -------
        name: str
        '''

        return self.__specs.loc['Name', 1]
    name = property(get_name, None, None, None)

    def get_slug_type(self):

        '''
        Returns the type of slugs being stored in the bucket (inner slug or
        outer slug).

        Returns
        -------
        slug_type: str
        '''

        return self.__specs.loc['Slug type', 1]
    slug_type = property(get_slug_type, None, None, None)

    def get_n_slugs(self):

        '''
        Returns the number of fuel slugs in the bucket.

        Returns
        -------
        n_slugs: int
        '''

        return self.__get_n_slugs()
    n_slugs = property(get_n_slugs, None, None, None)

    def get_fuel_enrichment(self):

        '''
        Returns the enrichment of the fuel slugs in the bucket, in %.

        Returns
        -------
        fuel_enrichment: float
        '''

        return self.__get_fuel_enrichment()
    fuel_enrichment = property(get_fuel_enrichment, None, None, None)

    def get_fresh_u_mass(self):

        '''
        Returns the total amount of uranium in the bucket, in grams.

        Returns
        -------
        fresh_u_mass: float
        '''

        return self.__get_fresh_u_mass()
    fresh_u_mass = property(get_fresh_u_mass, None, None, None)

    def get_fresh_u238_mass(self):

        '''
        Returns the total amount of uranium-238 in the bucket, in grams.

        Returns
        -------
        fresh_u238_mass: float
        '''

        return self.__get_fresh_u238_mass()
    fresh_u238_mass = property(get_fresh_u238_mass, None, None, None)

    def get_fresh_u235_mass(self):
        '''
        Returns the total amount of uranium-235 in the bucket, in grams.

        Returns
        -------
        fresh_u235_mass: float
        '''

        return self.__GetFreshU235UMass()
    fresh_u235_mass = property(get_fresh_u235_mass, None, None, None)

    def get_cladding_mass(self):

        '''
        Returns the total mass of cladding material in the bucket, in grams.

        Returns
        -------
        cladding_mass: float
        '''

        return self.__get_cladding_mass()
    cladding_mass = property(get_cladding_mass, None, None, None)

    # End: Pre-irradiation information
    #------

    def get_slug_length(self):
        '''
        Returns the length of each slug in the fuel bucket.

        Returns
        -------
        slug_length: float
        '''

        return self.__get_slug_length()

    def set_slug_length(self, x):
        '''
        Sets the length of all slugs in the bucket to x. Used for chopping.

        Parameters
        ----------
        x: float
        '''

        self.__set_slug_length(x)
    slug_length = property(get_slug_length, set_slug_length, None, None)

    def get_outer_slug_od(self):
        '''
        Returns the outer diameter of the outer section of fuel, in cm. A fuel
        slug consists of an outer section of fuel and an inner section of fuel,
        with cladding on the outside of the slug and between the inner and
        outer sections of fuel.

        Returns
        -------
        outer_slug_od: float
        '''

        return self.__get_outer_slug_od()
    outer_slug_od = property(get_outer_slug_od, None, None, None)

    def get_outer_slug_id(self):
        '''
        Returns the inner diameter of the outer section of fuel, in cm.

        Returns
        -------
        outer_slug_id: float
        '''

        return self.__get_outer_slug_id()
    outer_slug_id = property(get_outer_slug_id, None, None, None)

    def get_inner_slug_od(self):
        '''
        Returns the outer  diameter of the inner section of fuel, in cm.

        Returns
        -------
        inner_slug_od: float
        '''

        return self.__get_inner_slug_od()
    inner_slug_od = property(get_inner_slug_od, None, None, None)

    def get_inner_slug_id(self):
        '''
        Returns the inner diameter of the inner section of fuel, in cm.

        Returns
        -------
        inner_slug_id: float
        '''

        return self.__get_inner_slug_id()
    inner_slug_id = property(get_inner_slug_id, None, None, None)

    def get_cladding_wall_thickness(self):
        '''
        Returns the thickness of the cladding wall which is on the outside of
        every fuel slug, and in between both sections of fuel, in cm.

        Returns
        -------
        cladding_wall_thickness: float
        '''

        return self.__get_cladding_wall_thickness()
    cladding_wall_thickness = property(
        get_cladding_wall_thickness, None, None, None)

    def get_cladding_end_thickness(self):
        '''
        Gets the thickness of the hemispherical cladding end caps that are
        placed on the top and bottom of the fuel slug, in cm.

        Returns
        -------
        cladding_end_thickness: float
        '''

        return self.__get_cladding_end_thickness()
    cladding_end_thickness = property(get_cladding_end_thickness, None, None, None)

    def get_slug_fuel_volume(self):
        '''
        Returns the volume of fuel present in a single fuel slug, in cm^3.

        Returns
        -------
        slug_fuel_volume: float
        '''

        return self.__get_slug_fuel_volume()
    slug_fuel_volume = property(get_slug_fuel_volume, None, None, None)

    def get_fuel_volume(self):
        '''
        Returns the total volume of fuel in the entire bucket, in cm^3.

        Returns
        -------
        fuel_volume: float
        '''

        return self.__get_fuel_volume()
    fuel_volume = property(get_fuel_volume, None, None, None)

    def get_slug_cladding_volume(self):
        '''
        Returns the volume of cladding present in a single fuel slug, in cm^3.

        Returns
        -------
        slug_cladding_volume: float
        '''

        return self.__get_slug_cladding_volume()
    slug_cladding_volume = property(get_slug_cladding_volume, None, None, None)

    def get_cladding_volume(self):
        '''
        Returns the total volume of cladding in the bucket, in cm^3.

        Returns
        -------
        cladding_volume: float
        '''

        return self.__get_cladding_volume()
    cladding_volume = property(get_cladding_volume, None, None, None)

    def get_fuel_mass(self):

        '''
        Returns the total mass of fuel in the solid phase in the bucket.

        Returns
        -------
        fuel_mass: float
        '''

        return self.__fuel_phase.GetValue('mass') # mass of the solid phase
    fuel_mass = property(get_fuel_mass, None, None, None)

    def get_fuel_mass_unit(self):
        '''
        Returns the unit that is used to measure the mass of fuel in the
        bucket.

        Returns
        -------
        fuel_mass_unit: str
        '''

        return self.__fuel_phase.GetQuantity('mass').unit # mass of the solid phase
    fuel_mass_unit = property(get_fuel_mass_unit, None, None, None)

    def get_radioactivity(self):   # radioactivity of the fuel bucket (fix me)
        '''
        Returns the radioactivity of the fuel bucket, in units of curies.

        Returns
        -------
        radioactivity: float
        '''

        return self.__fuel_phase.GetValue('radioactivity')
    radioactivity = property(get_radioactivity, None, None, None)

    def get_gamma_pwr(self):
        '''
        Returns the amount of gamma radiation given off by the fuel bucket,
        in units of watts.

        Returns
        -------
        gamma_pwr: float
        '''

        return self.__fuel_phase.GetValue('gamma')   # gamma pwr of the fuel bucket
    gamma_pwr = property(get_gamma_pwr, None, None, None)

    def get_heat_pwr(self):
        '''
        Returns the total amount of heat generated by the bucket, in units of
        watts.

        Returns
        -------
        heat_pwr: float
        '''

        return self.__fuel_phase.GetValue('heat')   # heat pwr of the fuel bucket
    heat_pwr = property(get_heat_pwr, None, None, None)

    def get_fuel_radioactivity(self):
        # radioactivity of the solid phase

        '''
        Returns the total radioactivity of the solid phase fuel, in units of
        curies.

        Returns
        -------
        fuel_radioactivity: float
        '''

        return self.__fuel_phase.GetValue('radioactivity')
    fuel_radioactivity = property(get_fuel_radioactivity, None, None, None)

    def get_fuel_phase(self):

        '''
        Returns the phase history of the fuel.

        Returns
        -------
        fuel_phase: pandas.core.frame.DataFrame
        '''

        return self.__fuel_phase

    def set_fuel_phase(self, phase):
        '''
        Sets the current fuel phase to a specified phase value.

        Parameters
        ----------
        phase: dataFrame
        '''

        self.__fuel_phase = deepcopy(phase)
    fuel_phase = property(get_fuel_phase, set_fuel_phase, None, None)

    def get_cladding_phase(self):
        '''
        Returns the phase history of the cladding.

        Returns
        -------
        cladding_phase: dataFrame
        '''

        return self.__cladding_phase

    def set_cladding_phase(self, phase):
        '''
        Set's the phase history to specific values.

        Parameters
        ----------
        phase: dataFrame
        '''

        self.__cladding_phase = deepcopy(phase)
    cladding_phase = property(get_cladding_phase, set_cladding_phase, None, None)

#**********************************************************************************
# Private helper functions (internal use: __)
#**********************************************************************************

    def __get_n_slugs(self):
        '''
        Returns the number of fuel slugs in the bucket.

        Returns
        -------
        self.__specs.loc['Number of slugs', 1]: int
        '''

        return int(self.__specs.loc['Number of slugs', 1])

    def __get_fuel_enrichment(self):
        '''
        Returns the enrichment of the fuel in the bucket, in %.

        Returns
        -------
        self.__specs.loc['Enrichment [U-235 wt%]', 1]: float
        '''

        return float(self.__specs.loc['Enrichment [U-235 wt%]', 1])

    def __get_outer_slug_fresh_u_mass(self):
        '''
        Returns the the mass of uranium present in the outer part of a fuel
        slug, in grams.

        Returns
        -------
        self.__specs.loc['U mass outer slug [kg]', 1]) * 1000: float
        '''

        return float(self.__specs.loc['U mass outer slug [kg]', 1]) * 1000.0  # [g]

    def __get_inner_slug_fresh_u_mass(self):
        '''
        Returns the mass of uranium present in the inner part of the fuel slug,
        in grams.

        Returns
        -------
        self.__specs.loc['U mass inner slug [kg]', 1]) * 1000: float
        '''

        return float(
            self.__specs.loc['U mass inner slug [kg]', 1]) * 1000.0  # [g]

    def __get_outer_slug_cladding_mass(self):
        '''
        Returns the mass of cladding present in the outer part of the slug, in
        grams.

        Returns
        -------
        self.__specs.loc['Cladding mass outer slug [kg]', 1]) * 1000: float
        '''

        return float(
            self.__specs.loc['Cladding mass outer slug [kg]', 1]) * 1000.0  # [g]

    def __get_inner_slug_cladding_mass(self):
        '''
        Returns the mass of cladding present in the inner part of the slug, in
        grams.
        '''

        return float(
            self.__specs.loc['Cladding mass inner slug [kg]', 1]) * 1000.0  # [g]

    def __get_fresh_u_mass(self):
        '''
        Returns the total amount of uranium present in the fuel bucket, in
        grams.

        Returns
        -------
        n_slugs * (uMassOuterSlug + uMassInnerSlug): float
        '''

        n_slugs = self.__get_n_slugs()
        uMassOuterSlug = self.__get_outer_slug_fresh_u_mass()
        uMassInnerSlug = self.__get_inner_slug_fresh_u_mass()
        return n_slugs * (uMassOuterSlug + uMassInnerSlug)

    def __get_fresh_u238_mass(self):
        '''
        Returns the total mass of uranium-238 present in the fuel bucket, in
        grams.

        Returns
        -------
        totalUMass * (1.0 - fuelEnrichment / 100): float
        '''

        totalUMass = self.__get_fresh_u_mass()
        fuelEnrichment = self.__get_fuel_enrichment()
        return totalUMass * (1.0 - fuelEnrichment / 100.0)

    def __get_fresh_u235_mass(self):
        '''
        Returns the total amount of uranium-235 present in the bucket in grams.

        Returns
        -------
        totalUmass * fuelEnrichment / 100: float
        '''

        totalUMass = self.__get_fresh_u_mass()
        fuelEnrichment = self.__get_fuel_enrichment()
        return totalUMass * fuelEnrichment / 100.0

    def __get_cladding_mass(self):
        '''
        Returns the total amount of cladding present in the bucket, in grams.

        Returns
        -------
        n_slugs * (cladMassOuterSlug + cladMassInnerSlug): float
        '''

        n_slugs = self.__get_n_slugs()
        cladMassOuterSlug = self.__get_outer_slug_cladding_mass()
        cladMassInnerSlug = self.__get_inner_slug_cladding_mass()
        return n_slugs * (cladMassOuterSlug + cladMassInnerSlug)

    def __get_slug_length(self):
        '''
        Returns the length of a fuel slug, in cm. Does NOT include end caps.

        Returns
        -------
        self.__specs.loc['Slug length [in]', 1]) * 2.54: float
        '''

        return float(self.__specs.loc['Slug length [in]', 1]) * 2.54  # cm

    def __set_slug_length(self, x):
        '''
        Sets the length of a fuel slug to a specified value. Used for chopping.

        Parameters
        ----------
        x: float
        '''

        self.__specs.loc['Slug length [in]', 1] = x / 2.54  # in
        return

    def __get_outer_slug_od(self):
        '''
        Returns the outer diameter of the outer fuel section of the slug in cm.

        Returns
        -------
        self.__specs.loc['Outer slug O.D. [in]', 1]) * 2.54: float
        '''

        return float(self.__specs.loc['Outer slug O.D. [in]', 1]) * 2.54  # cm

    def __get_outer_slug_id(self):
        '''
        Returns the inner diameter of the outer fuel section of the slug in cm.

        Returns
        -------
        self.__specs.loc['Outer slug I.D. [in]', 1]) * 2.54: float
        '''

        return float(self.__specs.loc['Outer slug I.D. [in]', 1]) * 2.54  # cm

    def __get_inner_slug_od(self):
        '''
        Returns the outer diameter of the inner fuel section of the slug in cm.

        Returns
        -------
        self.__specs.loc['Inner slug O.D. [in]', 1]) * 2.54: float
        '''

        return float(self.__specs.loc['Inner slug O.D. [in]', 1]) * 2.54  # cm

    def __get_inner_slug_id(self):
        '''
        Returns the inner diameter of the inner fuel section of the slug in cm.

        Returns
        -------
        self.__specs.loc['Inner slug I.D. [in]', 1]) * 2.54: float
        '''

        return float(self.__specs.loc['Inner slug I.D. [in]', 1]) * 2.54  # cm

    def __get_cladding_wall_thickness(self):
        '''
        Returns the thickness of the cladding material used on the outside of
        the fuel slug and between the inner and outer fuel sections.

        Returns
        -------
        self.__specs.loc['Cladding wall thickness [mm]', 1]) /10: float
        '''

        return float(
            self.__specs.loc['Cladding wall thickness [mm]', 1]) / 10.0  # cm

    def __get_cladding_end_thickness(self):
        '''
        Returns the thickness of the hemispherical end caps placed on either
        end of the cylindrical fuel slug, in cm.

        Returns
        -------
        self.__specs.loc['Cladding end cap thickness [mm]', 1]) / 10: float
        '''

        return float(
            self.__specs.loc['Cladding end cap thickness [mm]', 1]) / 10.0  # cm

    def __get_slug_fuel_volume(self):
        '''
        Returns the volume of fuel contained within a single fuel slug, in
        cm^3.

        Returns
        -------
        outerVolume + innerVolume: float
        '''

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
        '''
        Returns the total volume of a single fuel slug, in cm^3. Does not
        include the end caps.
        '''

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
        '''
        Returns the total volume of cladding in a single fuel slug. Does not
        include the end caps. Given in units of cm^3.

        Returns
        -------
        self.__get_slug_volume() - self.__get_slug_fuel_volume(): float
        '''

        return self.__get_slug_volume() - self.__get_slug_fuel_volume()

    def __get_fuel_volume(self):
        '''
        Returns the total volume of fuel in the bucket, in cm^3.

        Returns
        -------
        slugFuelVolume * nFuelSlugs: float
        '''

        slugFuelVolume = self.__get_slug_fuel_volume()
        nFuelSlugs = self.__get_n_slugs()
        return slugFuelVolume * nFuelSlugs

    def __get_cladding_volume(self):
        '''
        Returns the total volume of cladding material in the bucket, in cm^3.
        Does not include end caps.

        Returns
        -------
        slugCladdingVolume * nFuelSlugs
        '''

        slugCladdingVolume = self.__get_slug_cladding_volume()
        nFuelSlugs = self.__get_n_slugs()
        return slugCladdingVolume * nFuelSlugs

    def __str__(self):
        '''
        Converts to string.
        '''

        s = '\nFuelBucket():\n\t*******\n\t specs:\n\t*******\n\t %s\n'
        t = '\t************\n\t fuel_phase:\n\t**********\n\t %s\n'
        u = '\t***************\n\t cladding_phase:\n\t*****************\n\t %s\n'
        stu = s + t + u
        return stu % (self.__specs, self.__fuel_phase, self.__cladding_phase)

    def __repr__(self):

        '''
        Converts to string.
        '''

        s = '\nFuelBucket():\n\t*******\n\t specs:\n\t*******\n\t %s\n'
        t = '\t************\n\t fuel_phase:\n\t**********\n\t %s\n'
        u = '\t****************\n\t cladding_phase:\n\t****************\n\t %s\n'
        stu = s + t + u
        return stu % (self.__specs, self.__fuel_phase, self.__cladding_phase)

#======================= end class FuelBucket  ===================================
