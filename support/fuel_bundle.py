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
"""
# *******************************************************************************
import os
import sys
import math
import pandas
from copy import deepcopy
# *******************************************************************************

class FuelBundle():

    def __init__(self,
                 specs=pandas.DataFrame()
                 ):

        assert isinstance(specs, pandas.DataFrame), 'oops not pandas table.'

        self.__specs = specs

        self.__solid_phase = None
        self.__gas_phase = None

        return
# ---------------------- end def __init__():------------------------------

    # ------
    # Start: Pre-irradiation information

    def get_name(self):
        return self.__specs.loc['Name', 1]
    name = property(get_name, None, None, None)

    def get_fuel_enrichment(self):
        return self.__get_fuel_enrichment()
    fuel_enrichment = property(get_fuel_enrichment, None, None, None)

    def get_fresh_u_mass(self):
        return self.__get_fresh_u_mass()
    fresh_u_mass = property(get_fresh_u_mass, None, None, None)

    def get_fresh_u238_mass(self):
        total_mass = self.__get_fresh_u_mass()
        fuel_enrichment = self.__get_fuel_enrichment()
        return total_mass * (1.0 - fuel_enrichment / 100.0)
    fresh_u238_mass = property(get_fresh_u238_mass, None, None, None)

    def get_fresh_U235_mass(self):
        total_u_Mass = self.__get_fresh_u_mass()
        fuel_enrichment = self.__get_fuel_enrichment()
        return total_u_mass * fuel_enrichment / 100.0
    fresh_u235_mass = property(get_fresh_U235_mass, None, None, None)

    def get_n_fuel_rods(self):
        return self.__get_n_fuel_rods()
    n_fuel_rods = property(get_n_fuel_rods, None, None, None)

    # End: Pre-irradiation information
    # ------

    def get_fuel_pin_length(self):
        return self.__get_fuel_pin_length()

    def set_fuel_pin_length(self, x):
        self.__specs.loc['Fuel rods fuel length [in]', 1] = x / 2.54  # in
        return
    fuel_pin_length = property(get_fuel_pin_length, set_fuel_pin_length, None, None)

    def get_fuel_rod_od(self):
        return self.__get_fuel_rod_od()
    fuel_rod_od = property(get_fuel_rod_od, None, None, None)

    def get_fuel_pin_radius(self):
        return self.__get_fuel_pin_radius()
    fuel_pin_radius = property(get_fuel_pin_radius, None, None, None)

    def get_fuel_pin_volume(self):
        return self.__get_fuel_pin_volume()
    fuel_pin_volume = property(get_fuel_pin_volume, None, None, None)

    def get_fuel_volume(self):
        return self.__get_fuel_volume()
    fuel_volume = property(get_fuel_volume, None, None, None)

    # mass of the solid phase (gas phase in plenum not added)
    def get_fuel_mass(self):
        return self.__solid_phase.GetValue('mass')
    fuel_mass = property(get_fuel_mass, None, None, None)

    def get_fuel_mass_unit(self):
        return self.__solid_phase.GetQuantity('mass').unit
    fuel_mass_unit = property(get_fuel_mass_unit, None, None, None)

    def get_gas_mass(self):
        return self.__gas_phase.GetValue('mass')
    gas_mass = property(get_gas_mass, None, None, None)

    def get_radioactivity(self):
        return self.__solid_phase.GetValue('radioactivity') + \
            self.__gas_phase.GetValue('radioactivity')
    radioactivity = property(get_radioactivity, None, None, None)

    def get_gamma_pwr(self):
        return self.__solid_phase.GetValue('gamma') + \
            self.__gas_phase.GetValue('gamma')
    gamma_pwr = property(get_gamma_pwr, None, None, None)

    def get_heat_pwr(self):
        return self.__solid_phase.GetValue('heat') + \
            self.__gas_phase.GetValue('heat')
    heat_pwr = property(get_heat_pwr, None, None, None)

    def get_fuel_radioactivity(self):       # radioactivity of the solid phase
        return self.__solid_phase.GetValue('radioactivity')
    fuel_radioactivity = property(get_fuel_radioactivity, None, None, None)

    def get_gas_radioactivity(self):  # radioactivity of the gas phase
        return self.__gas_phase.GetValue('radioactivity')
    gas_radioactivity = property(get_gas_radioactivity, None, None, None)

    def get_solid_phase(self):
        return self.__solid_phase

    def set_solid_phase(self, phase):
        self.__solid_phase = deepcopy(phase)
    solid_phase = property(get_solid_phase, set_solid_phase, None, None)

    def get_gas_phase(self):
        return self.__gas_phase

    def set_gas_phase(self, phase):
        self.__gas_phase = deepcopy(phase)
    gas_phase = property(get_gas_phase, set_gas_phase, None, None)

# *********************************************************************************
# Private helper functions (internal use: __)

    def __get_fuel_enrichment(self):
        return float(self.__specs.loc['Enrichment [U-235 wt%]', 1])

    def __get_fresh_u_mass(self):
        return float(
            self.__specs.loc['U mass per assy [kg]', 1]) * 1000.0  # [g]

    def __get_n_fuel_rods(self):
        return int(self.__specs.loc['Fuel rods number', 1])

    def __get_fuel_pin_length(self):
        return float(
            self.__specs.loc['Fuel rods fuel length [in]', 1]) * 2.54  # cm

    def __get_fuel_rod_od(self):
        return float(self.__specs.loc['Fuel rods O.D. [in]', 1]) * 2.54  # cm

    def __get_fuel_rod_wall_thickness(self):
        return float(
            self.__specs.loc['Fuel rods wall thickness [in]', 1]) * 2.54  # cm

    def __get_fuel_pin_radius(self):
        fuel_rod_od = self.__get_fuel_rod_od()
        fuel_rod_wall_thickness = self.__get_fuel_rod_wall_thickness()
        fuel_pin_radius = (fuel_rod_od - 2.0 * fuel_rod_wall_thickness) / 2.0
        return fuel_pin_radius

    def __get_fuel_pin_volume(self):
        fuel_pin_length = self.__get_fuel_pin_length()
        fuel_pin_radius = self.__get_fuel_pin_radius()
        return fuel_pin_length * math.pi * fuel_pin_radius ** 2

    def __get_fuel_volume(self):
        fuel_pin_volume = self.__get_fuel_pin_volume()
        n_fuel_rods = self.__get_n_fuel_rods()
        return fuel_pin_volume * n_fuel_rods

# ********************************************************************************
# Printing of data members
    def __str__(self):
        s = 'FuelBundle():\n %s\n %s\n %s\n'
        return s % (self.__specs, self.__solid_phase, self.__gas_phase)

    def __repr__(self):
        s = 'FuelBundle():\n %s\n %s\n %s\n'
        return s % (self.__specs, self.__solid_phase, self.__gas_phase)

# ====================== end class FuelBundle: ===================================
