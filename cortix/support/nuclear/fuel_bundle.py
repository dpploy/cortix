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
This FuelBundle class is a container for usage with other plant-level process modules.
It is meant to represent a fuel bundle of an oxide fuel LWR reactor.
There are three main data structures:

  1) fuel bundle specs
  2) solid phase
  3) gas phase

The container user will have to provide all the data and from then on, this class
will help acess the data.
The printing methods reveal the contained data.

Author: Valmor de Almeida dealmeidav@ornl.gov; vfda
Sun Dec 27 15:06:55 EST 2015
'''
#*********************************************************************************
import os
import sys
import math
import pandas
from copy import deepcopy
#*********************************************************************************

class FuelBundle():

#*********************************************************************************
# Constructor
#*********************************************************************************

    def __init__(self,
                 specs=pandas.DataFrame()
                 ):

        assert isinstance(specs, pandas.DataFrame), 'oops not pandas table.'

        self.__specs = specs

        self.__solid_phase = None
        self.__gas_phase = None

        return

    # ------
    # Start: Pre-irradiation information

#*********************************************************************************
# Public Member Functions
#*********************************************************************************

    def get_name(self):
        '''
        Returns the name of the fuel bundle.

        Returns
        -------
        name: str
        '''

        return self.__specs.loc['Name', 1]
    name = property(get_name, None, None, None)

    def get_fuel_enrichment(self):
        '''
        Returns the enrichment of the fuel pins in the bundle, in %.

        Returns
        -------
        fuel_enrichment: float
        '''

        return self.__get_fuel_enrichment()
    fuel_enrichment = property(get_fuel_enrichment, None, None, None)

    def get_fresh_u_mass(self):
        '''
        Returns the amount of uranium in the bundle, in grams.

        Returns
        -------
        fresh_u_mass: float
        '''

        return self.__get_fresh_u_mass()
    fresh_u_mass = property(get_fresh_u_mass, None, None, None)

    def get_fresh_u238_mass(self):
        '''
        Returns the amount of uranium-238 in the bucket, in grams.

        Returns
        -------
        fresh_u238_mass: float
        '''

        total_mass = self.__get_fresh_u_mass()
        fuel_enrichment = self.__get_fuel_enrichment()
        return total_mass * (1.0 - fuel_enrichment / 100.0)
    fresh_u238_mass = property(get_fresh_u238_mass, None, None, None)

    def get_fresh_U235_mass(self):
        '''
        Returns the amount of uranium-235 in the bucket, in grams.

        Returns
        -------
        fresh_u235_mass: float
        '''

        total_u_Mass = self.__get_fresh_u_mass()
        fuel_enrichment = self.__get_fuel_enrichment()
        return total_u_mass * fuel_enrichment / 100.0
    fresh_u235_mass = property(get_fresh_U235_mass, None, None, None)

    def get_n_fuel_rods(self):
        '''
        Returns the number of fuel rods in the bundle.

        Returns
        -------
        n_fuel_rods: int
        '''

        return self.__get_n_fuel_rods()
    n_fuel_rods = property(get_n_fuel_rods, None, None, None)

    # End: Pre-irradiation information
    # ------

    def get_fuel_pin_length(self):
        '''
        Returns the length of each fuel pin in the fuel bundle. A fuel pin is
        a cylindircal section of uranium fuel that is surrounded by cladding.

        Returns
        -------
        fuel_pin_length: float
        '''

        return self.__get_fuel_pin_length()

    def set_fuel_pin_length(self, x):
        '''
        Sets the length of all fuel pins in the bundle to x.

        Returns
        -------
        x: float
        '''

        self.__specs.loc['Fuel rods fuel length [in]', 1] = x / 2.54  # in
        return
    fuel_pin_length = property(get_fuel_pin_length, set_fuel_pin_length, None, None)

    def get_fuel_rod_od(self):
        '''
        Returns the outer diameter of the fuel rod, in cm.
        A fuel rod consists of a fuel pin surrounded by cladding.

        Returns
        -------
        fuel_rod_od: float
        '''

        return self.__get_fuel_rod_od()
    fuel_rod_od = property(get_fuel_rod_od, None, None, None)

    def get_fuel_pin_radius(self):
        '''
        Returns the radius of the fuel pin, in cm.
        '''

        return self.__get_fuel_pin_radius()
    fuel_pin_radius = property(get_fuel_pin_radius, None, None, None)

    def get_fuel_pin_volume(self):
        '''
        Returns the volume of fuel in each fuel pin, in cm^3.

        Returns
        -------
        fuel_pin_volume: float
        '''

        return self.__get_fuel_pin_volume()
    fuel_pin_volume = property(get_fuel_pin_volume, None, None, None)

    def get_fuel_volume(self):

        '''
        Returns the total volume of fuel in the bundle, in cm^3.

        Returns
        -------
        fuel_volume: float
        '''

        return self.__get_fuel_volume()
    fuel_volume = property(get_fuel_volume, None, None, None)

    # mass of the solid phase (gas phase in plenum not added)
    def get_fuel_mass(self):
        '''
        Returns the total numerical value for  mass of fuel in the solid phase
        in the bundle.

        Returns
        -------
        fuel_mass: float
        '''

        return self.__solid_phase.GetValue('mass')
    fuel_mass = property(get_fuel_mass, None, None, None)

    def get_fuel_mass_unit(self):
        '''
        Returns the unit used to measure the mass of fuel in the bundle.

        Returns
        -------
        fuel_mass_unit: str
        '''

        return self.__solid_phase.GetQuantity('mass').unit
    fuel_mass_unit = property(get_fuel_mass_unit, None, None, None)

    def get_gas_mass(self):
        '''
        Returns the total numerical value for mass of the fuel in the gas
        phase.
        '''

        return self.__gas_phase.GetValue('mass')
    gas_mass = property(get_gas_mass, None, None, None)

    def get_radioactivity(self):
        '''
        Returns the total radioactivity of the fuel bundle, in curies.

        Returns
        -------
        raduioactivity: float
        '''

        return self.__solid_phase.GetValue('radioactivity') + \
            self.__gas_phase.GetValue('radioactivity')
    radioactivity = property(get_radioactivity, None, None, None)

    def get_gamma_pwr(self):
        '''
        Returns the total amount of gamma radiation given by the fuel bundle,
        in watts.

        Returns
        -------
        gamma_pwr: float
        '''

        return self.__solid_phase.GetValue('gamma') + \
            self.__gas_phase.GetValue('gamma')
    gamma_pwr = property(get_gamma_pwr, None, None, None)

    def get_heat_pwr(self):
        '''
        Returns the total amount of heat produced by the fuel bundle, in watts.

        Returns
        -------
        heat_pwr: float
        '''

        return self.__solid_phase.GetValue('heat') + \
            self.__gas_phase.GetValue('heat')
    heat_pwr = property(get_heat_pwr, None, None, None)

    def get_fuel_radioactivity(self):
    # radioactivity of the solid phase
        '''
        Returns the total radioactivity of the fuel in the solid phase in the
        fuel bundle.

        Returns
        -------
        fuel_radioactivity: float
        '''

        return self.__solid_phase.GetValue('radioactivity')
    fuel_radioactivity = property(get_fuel_radioactivity, None, None, None)

    def get_gas_radioactivity(self):
        # radioactivity of the gas phase
        '''
        Returns the total radioactivity of the fuel in the gas phase in the
        fuel bundle, in curies.

        Returns
        -------
        gas_radioactivity: float
        '''

        return self.__gas_phase.GetValue('radioactivity')
    gas_radioactivity = property(get_gas_radioactivity, None, None, None)

    def get_solid_phase(self):
        '''
        Returns the solid phase history associated with this fuel bundle.

        Returns
        -------
        solidPhase: dataFrame
        '''

        return self.__solid_phase

    def set_solid_phase(self, phase):
        '''
        Sets the solid phase history of the fuel equal to phase.

        Parameters
        ----------
        phase: dataFrame
        '''

        self.__solid_phase = deepcopy(phase)
    solid_phase = property(get_solid_phase, set_solid_phase, None, None)

    def get_gas_phase(self):
        '''
        Returns the gas phase history of the fuel.

        Returns
        -------
        gas_phase: dataFrame
        '''

        return self.__gas_phase

    def set_gas_phase(self, phase):
        '''
        Sets the gas phase history of the fuel equal to phase.

        Parameters
        ----------
        phase: dataFrame
        '''

        self.__gas_phase = deepcopy(phase)
    gas_phase = property(get_gas_phase, set_gas_phase, None, None)

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

    def __get_fuel_enrichment(self):
        '''
        Returns the enrichment of the fuel.

        Returns
        -------
        self.__specs.loc['Enrichment [U-235 wt%]', 1]: float
        '''

        return float(self.__specs.loc['Enrichment [U-235 wt%]', 1])

    def __get_fresh_u_mass(self):

        '''
        Returns the mass of fuel in the bundle.

        Returns
        -------
        self.__specs.loc['U mass per assy [kg]', 1]) * 1000
        '''

        return float(
            self.__specs.loc['U mass per assy [kg]', 1]) * 1000.0  # [g]

    def __get_n_fuel_rods(self):
        '''
        Returns the number of fuel rods in the bundle.

        Returns
        -------
        self.__specs.loc['Fuel rods number', 1]): int
        '''

        return int(self.__specs.loc['Fuel rods number', 1])

    def __get_fuel_pin_length(self):
        '''
        Returns the length of the fuel pins in the bundle.

        Returns
        -------
        self.__specs.loc["fuel rods fuel length [in]', 1]) * 2.54
        '''

        return float(
            self.__specs.loc['Fuel rods fuel length [in]', 1]) * 2.54  # cm

    def __get_fuel_rod_od(self):
        '''
        Returns the outer diameter of the fuel rods in the bundle.

        Returns
        -------
        self.__specs.loc['Fuel rods O.D. [in]', 1]) * 2.54: float
        '''

        return float(self.__specs.loc['Fuel rods O.D. [in]', 1]) * 2.54  # cm

    def __get_fuel_rod_wall_thickness(self):
        '''
        Returns the thickness of the cladding wall on the outside of the fuel
        rod.

        Returns
        -------
        self.__specs.loc['Fuel rods wall thickness [in]', 1]) * 2.54: float
        '''

        return float(
            self.__specs.loc['Fuel rods wall thickness [in]', 1]) * 2.54  # cm

    def __get_fuel_pin_radius(self):
        '''
        Returns the radius of the fuel pins.

        Returns
        -------
        fuel_pin_radius: float
        '''

        fuel_rod_od = self.__get_fuel_rod_od()
        fuel_rod_wall_thickness = self.__get_fuel_rod_wall_thickness()
        fuel_pin_radius = (fuel_rod_od - 2.0 * fuel_rod_wall_thickness) / 2.0
        return fuel_pin_radius

    def __get_fuel_pin_volume(self):
        '''
        Returns the volume of each fuel pin.

        Returns
        -------
        fuel_pin_length * math.pi * fuel_pin_radius ** 2: float
        '''

        fuel_pin_length = self.__get_fuel_pin_length()
        fuel_pin_radius = self.__get_fuel_pin_radius()
        return fuel_pin_length * math.pi * fuel_pin_radius ** 2

    def __get_fuel_volume(self):

        '''
        Returns the volume of fuel in the bundle, in cm^3.

        Returns
        -------
        fuel_pin_volume * n_fuel_rods: float
        '''

        fuel_pin_volume = self.__get_fuel_pin_volume()
        n_fuel_rods = self.__get_n_fuel_rods()
        return fuel_pin_volume * n_fuel_rods

    def __str__(self):
        s = 'FuelBundle():\n %s\n %s\n %s\n'
        return s % (self.__specs, self.__solid_phase, self.__gas_phase)

    def __repr__(self):
        s = 'FuelBundle():\n %s\n %s\n %s\n'
        return s % (self.__specs, self.__solid_phase, self.__gas_phase)

#======================= end class FuelBundle ====================================
