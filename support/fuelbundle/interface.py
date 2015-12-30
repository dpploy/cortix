#!/usr/bin/env python
"""
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

This FuelBundle class is a container for usage with other plant-level process modules.

For unit testing do at the linux command prompt:
    python interface.py

Sun Dec 27 15:06:55 EST 2015
"""

#*******************************************************************************
import os, sys
import math
import pandas

from ._fuelbundle import _FuelBundle  # constructor
#*******************************************************************************

#*******************************************************************************
class FuelBundle():

#*******************************************************************************
 def __init__( self, 
               specs = pandas.DataFrame()
             ):

     # constructor
     _FuelBundle( self, 
                  specs
                )

     return

#*******************************************************************************

#*******************************************************************************
# Setters and Getters methods
#-------------------------------------------------------------------------------
# These are passing arguments by value effectively. Because the python objects
# passed into/out of the function are immutable.

 #------
 # Start: Pre-irradiation information
 def GetName(self):
     return self.__GetName()
 name = property(GetName,None,None,None)

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

 def GetSolidPhase(self): 
     return self._solidPhase
 def SetSolidPhase(self,phase): 
     self._solidPhase = phase
 solidPhase = property(GetSolidPhase,SetSolidPhase,None,None)

 def GetGasPhase(self): 
     return self._gasPhase
 def SetGasPhase(self,phase): 
     self._gasPhase = phase
 gasPhase = property(GetGasPhase,SetGasPhase,None,None)
 

#*******************************************************************************
# Internal class helpers 

 def __GetName(self):
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

#*******************************************************************************
# Printing of data members
# def __str__( self ):
#     s = 'name: %5s; formalName: %5s; unit: %5s; '+' value: %6s\n'
#     return s % (self.name, self.formalName, self.unit, self.value)
#
# def __repr__( self ):
#     s = 'name: %5s; formalName: %5s; unit: %5s;'+' value: %6s\n'
#     return s % (self.name, self.formalName, self.unit, self.value)
#*******************************************************************************
# Usage: -> python interface.py
if __name__ == "__main__":
   print('Unit testing for FuelBundle')