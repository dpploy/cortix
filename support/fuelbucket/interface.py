#!/usr/bin/env python
"""
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

This FuelBucket class is a container for usage with other plant-level process modules.
It is meant to represent a fuel bucket of a metal fuel LWR reactor.

For unit testing do at the linux command prompt:
    python interface.py

Mon Dec 12 00:32:35 EST 2016
"""

#*******************************************************************************
import os, sys
import math
import pandas

from ._fuelbucket import _FuelBucket  # constructor
#*******************************************************************************

#*******************************************************************************
class FuelBucket():

#*******************************************************************************
 def __init__( self, 
               specs = pandas.DataFrame()
             ):

     # constructor
     _FuelBucket( self, 
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

 def GetNFuelSlugs(self): 
     return self.__GetNFuelSlugs()
 nFuelSlugs = property(GetNFuelSlugs,None,None,None)
 # End: Pre-irradiation information
 #------

 def GetFuelSlugLength(self): 
     return self.__GetFuelSlugLength()
 def SetFuelSlugLength(self,x): 
     self.__SetFuelSlugLength(x)
 fuelSlugLength = property(GetFuelSlugLength,SetFuelSlugLength,None,None)

 def GetFuelRodOD(self): 
     return self.__GetFuelRodOD()
 fuelRodOD = property(GetFuelRodOD,None,None,None)

 def GetFuelSlugRadius(self): 
     return self.__GetFuelSlugRadius()
 fuelSlugRadius = property(GetFuelSlugRadius,None,None,None)

 def GetFuelSlugVolume(self): 
     return self.__GetFuelSlugVolume()
 fuelSlugVolume = property(GetFuelSlugVolume,None,None,None)

 def GetFuelVolume(self): 
     return self.__GetFuelVolume()
 fuelVolume = property(GetFuelVolume,None,None,None)

 def GetFuelMass(self): 
     return self.__GetFuelMass()
 fuelMass = property(GetFuelMass,None,None,None)

 def GetFuelMassUnit(self): 
     return self.__GetFuelMassUnit()
 fuelMassUnit = property(GetFuelMassUnit,None,None,None)

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

 def __GetNFuelSlugs(self):
     return int(self._specs.loc['Fuel slugs number',1])

 def __GetFuelSlugLength(self):
     return float(self._specs.loc['Fuel slugs fuel length [in]',1]) * 2.54 # cm

 def __SetFuelSlugLength(self,x):
     self._specs.loc['Fuel slugs fuel length [in]',1] = x / 2.54 # in
     return

 def __GetFuelRodOD(self):
     return float(self._specs.loc['Fuel slugs O.D. [in]',1]) * 2.54 # cm

 def __GetFuelRodWallThickness(self):
     return float(self._specs.loc['Fuel slugs wall thickness [in]',1]) * 2.54 # cm

 def __GetFuelSlugRadius(self):
     fuelRodOD = self.__GetFuelRodOD()
     fuelRodWallThickness = self.__GetFuelRodWallThickness()
     fuelSlugRadius = ( fuelRodOD - 2.0 * fuelRodWallThickness ) / 2.0
     return fuelSlugRadius

 def __GetFuelSlugVolume(self):
     fuelSlugLength = self.__GetFuelSlugLength()
     fuelSlugRadius = self.__GetFuelSlugRadius()
     return fuelSlugLength * math.pi * fuelSlugRadius ** 2

 def __GetFuelVolume(self):
     fuelSlugVolume = self.__GetFuelSlugVolume()
     nFuelSlugs = self.__GetNFuelSlugs()
     return fuelSlugVolume * nFuelSlugs

 def __GetFuelMass(self): # mass of the solid phase (gas phase in plenum not added)
     return self._solidPhase.GetQuantity('mass').value
 def __GetFuelMassUnit(self): # mass of the solid phase (gas phase in plenum not added)
     return self._solidPhase.GetQuantity('mass').unit

 def __GetFuelRadioactivity(self): # radioactivity of the solid phase
     return self._solidPhase.GetQuantity('radioactivity').value
 def __GetGasRadioactivity(self): # radioactivity of the gas phase
     return self._gasPhase.GetQuantity('radioactivity').value

 def __GetRadioactivity(self): # radioactivity of the fuel bucket
     return self._solidPhase.GetQuantity('radioactivity').value + \
            self._gasPhase.GetQuantity('radioactivity').value 

 def __GetGammaPwr(self): # gamma pwr of the fuel bucket
     return self._solidPhase.GetQuantity('gamma').value + \
            self._gasPhase.GetQuantity('gamma').value 

 def __GetHeatPwr(self): # heat pwr of the fuel bucket
     return self._solidPhase.GetQuantity('heat').value + \
            self._gasPhase.GetQuantity('heat').value 

#*******************************************************************************
# Printing of data members
 def __str__( self ):
     s = 'FuelBucket(): %s\n %s\n %s\n'
     return s % (self._specs, self._solidPhase, self._gasPhase)

 def __repr__( self ):
     s = 'FuelBucket(): %s\n %s\n %s\n'
     return s % (self._specs, self._solidPhase, self._gasPhase)
#*******************************************************************************
# Usage: -> python interface.py
if __name__ == "__main__":
   print('Unit testing for FuelBucket')
