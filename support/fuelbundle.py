# -*- coding: utf-8 -*-
"""
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

This FuelBundle class is a container for usage with other plant-level process modules.
It is meant to represent a fuel bundle of an oxide fuel LWR reactor.
There are three main data structures:
  1) fuel bundle specs
  2) solid phase
  3) gas phase
The container user will have to provide all the data and from then on, this class
will help acess the data.
The printing methods reveal the contained data.

For unit testing do at the linux command prompt:
    python interface.py

Sun Dec 27 15:06:55 EST 2015
"""

#*******************************************************************************
import os, sys
import math
import pandas
from copy import deepcopy
#*******************************************************************************

#*******************************************************************************
class FuelBundle():

#*******************************************************************************
 def __init__( self, 
               specs = pandas.DataFrame()
             ):

     assert type(specs) == type(pandas.DataFrame()), 'oops not pandas table.'

     self._specs = specs

     self._solidPhase = None
     self._gasPhase   = None

     return

#*******************************************************************************
# Setters and Getters methods
#-------------------------------------------------------------------------------
# These are passing arguments by value effectively. Because the python objects
# passed into/out of the function are immutable.

 #------
 # Start: Pre-irradiation information
 def get_name(self):
     return self.__get_name()
 name = property(get_name,None,None,None)

 def GetFuelEnrichment(self):
     return self.__GetFuelEnrichment()
 fuelEnrichment = property(GetFuelEnrichment,None,None,None)

 def GetFreshUMass(self): 
     return self.__GetFreshUMass() 
 freshUMass = property(GetFreshUMass,None,None,None)

 def GetFreshU238Mass(self): 
     return self.__GetFreshU238UMass()
 freshU238Mass = property(GetFreshU238Mass,None,None,None)

 def GetFreshU235Mass(self): 
     return self.__GetFreshU235UMass()
 freshU235Mass = property(GetFreshU235Mass,None,None,None)

 def GetNFuelRods(self): 
     return self.__GetNFuelRods()
 nFuelRods = property(GetNFuelRods,None,None,None)
 # End: Pre-irradiation information
 #------

 def GetFuelPinLength(self): 
     return self.__GetFuelPinLength()
 def SetFuelPinLength(self,x): 
     self.__SetFuelPinLength(x)
 fuelPinLength = property(GetFuelPinLength,SetFuelPinLength,None,None)

 def GetFuelRodOD(self): 
     return self.__GetFuelRodOD()
 fuelRodOD = property(GetFuelRodOD,None,None,None)

 def GetFuelPinRadius(self): 
     return self.__GetFuelPinRadius()
 fuelPinRadius = property(GetFuelPinRadius,None,None,None)

 def GetFuelPinVolume(self): 
     return self.__GetFuelPinVolume()
 fuelPinVolume = property(GetFuelPinVolume,None,None,None)

 def GetFuelVolume(self): 
     return self.__GetFuelVolume()
 fuelVolume = property(GetFuelVolume,None,None,None)

 def GetFuelMass(self): 
     return self.__GetFuelMass()
 fuelMass = property(GetFuelMass,None,None,None)

 def GetFuelMassUnit(self): 
     return self.__GetFuelMassUnit()
 fuelMassUnit = property(GetFuelMassUnit,None,None,None)

 def GetGasMass(self): 
     return self.__GetGasMass()
 gasMass = property(GetGasMass,None,None,None)

 def GetRadioactivity(self): 
     return self.__GetRadioactivity()
 radioactivity = property(GetRadioactivity,None,None,None)

 def GetGammaPwr(self): 
     return self.__GetGammaPwr()
 gammaPwr = property(GetGammaPwr,None,None,None)

 def GetHeatPwr(self): 
     return self.__GetHeatPwr()
 heatPwr = property(GetHeatPwr,None,None,None)

 def GetFuelRadioactivity(self): 
     return self.__GetFuelRadioactivity()
 fuelRadioactivity = property(GetFuelRadioactivity,None,None,None)

 def GetSolidPhase(self): 
     return self._solidPhase
 def SetSolidPhase(self,phase): 
     self._solidPhase = deepcopy( phase )
 solidPhase = property(GetSolidPhase,SetSolidPhase,None,None)

 def GetGasPhase(self): 
     return self._gasPhase
 def SetGasPhase(self,phase): 
     self._gasPhase = deepcopy( phase )
 gasPhase = property(GetGasPhase,SetGasPhase,None,None)
 

#*******************************************************************************
# Internal class helpers 

 def __get_name(self):
     return self._specs.loc['Name',1]

 def __GetFuelEnrichment(self):
     return float(self._specs.loc['Enrichment [U-235 wt%]',1])

 def __GetFreshUMass(self):
     return float(self._specs.loc['U mass per assy [kg]',1])*1000.0  # [g]

 def __GetFreshU238Mass(self):
     totalUMass = self.__GetFreshUMass()
     fuelEnrichment = self.__GetFuelEnrichment()
     return totalUMass * (1.0-fuelEnrichment/100.0)

 def __GetFreshU235Mass(self):
     totalUMass = self.__GetFreshUMass()
     fuelEnrichment = self.__GetFuelEnrichment()
     return totalUMass * fuelEnrichment/100.0

 def __GetNFuelRods(self):
     return int(self._specs.loc['Fuel rods number',1])

 def __GetFuelPinLength(self):
     return float(self._specs.loc['Fuel rods fuel length [in]',1]) * 2.54 # cm

 def __SetFuelPinLength(self,x):
     self._specs.loc['Fuel rods fuel length [in]',1] = x / 2.54 # in
     return

 def __GetFuelRodOD(self):
     return float(self._specs.loc['Fuel rods O.D. [in]',1]) * 2.54 # cm

 def __GetFuelRodWallThickness(self):
     return float(self._specs.loc['Fuel rods wall thickness [in]',1]) * 2.54 # cm

 def __GetFuelPinRadius(self):
     fuelRodOD = self.__GetFuelRodOD()
     fuelRodWallThickness = self.__GetFuelRodWallThickness()
     fuelPinRadius = ( fuelRodOD - 2.0 * fuelRodWallThickness ) / 2.0
     return fuelPinRadius

 def __GetFuelPinVolume(self):
     fuelPinLength = self.__GetFuelPinLength()
     fuelPinRadius = self.__GetFuelPinRadius()
     return fuelPinLength * math.pi * fuelPinRadius ** 2

 def __GetFuelVolume(self):
     fuelPinVolume = self.__GetFuelPinVolume()
     nFuelRods = self.__GetNFuelRods()
     return fuelPinVolume * nFuelRods

 def __GetFuelMass(self): # mass of the solid phase (gas phase in plenum not added)
     return self._solidPhase.GetValue('mass')
 def __GetFuelMassUnit(self): # mass of the solid phase (gas phase in plenum not added)
     return self._solidPhase.GetQuantity('mass').unit

 def __GetFuelRadioactivity(self): # radioactivity of the solid phase
     return self._solidPhase.GetValue('radioactivity')
 def __GetGasRadioactivity(self): # radioactivity of the gas phase
     return self._gasPhase.GetValue('radioactivity')

 def __GetRadioactivity(self): # radioactivity of the fuel bundle
     return self._solidPhase.GetValue('radioactivity') + \
            self._gasPhase.GetValue('radioactivity')

 def __GetGammaPwr(self): # gamma pwr of the fuel bundle
     return self._solidPhase.GetValue('gamma') + \
            self._gasPhase.GetValue('gamma') 

 def __GetHeatPwr(self): # heat pwr of the fuel bundle
     return self._solidPhase.GetValue('heat') + \
            self._gasPhase.GetValue('heat') 

 def __GetGasMass(self): # gas plenum mass
     return self._gasPhase.GetValue('mass')

#*******************************************************************************
# Printing of data members
 def __str__( self ):
     s = 'FuelBundle(): %s\n %s\n %s\n'
     return s % (self._specs, self._solidPhase, self._gasPhase)

 def __repr__( self ):
     s = 'FuelBundle(): %s\n %s\n %s\n'
     return s % (self._specs, self._solidPhase, self._gasPhase)
#*******************************************************************************
# Usage: -> python interface.py
if __name__ == "__main__":
   print('Unit testing for FuelBundle')
