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

 def GetSlugType(self):
     return self.__GetSlugType()
 slugType = property(GetSlugType,None,None,None)

 def GetNSlugs(self): 
     return self.__GetNSlugs()
 nSlugs = property(GetNSlugs,None,None,None)

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

 def GetCladdingMass(self): 
     return self.__GetCladdingMass() 
 claddingMass = property(GetCladdingMass,None,None,None)

 # End: Pre-irradiation information
 #------

 def GetSlugLength(self): 
     return self.__GetSlugLength()
 def SetSlugLength(self,x): 
     self.__SetSlugLength(x)
 slugLength = property(GetSlugLength,SetSlugLength,None,None)

 def GetFuelRodOD(self): 
     return self.__GetFuelRodOD()
 fuelRodOD = property(GetFuelRodOD,None,None,None)

 def GetSlugFuelVolume(self): 
     return self.__GetSlugFuelVolume()
 slugFuelVolume = property(GetSlugFuelVolume,None,None,None)

 def GetFuelVolume(self): 
     return self.__GetFuelVolume()
 fuelVolume = property(GetFuelVolume,None,None,None)

 def GetSlugCladdingVolume(self): 
     return self.__GetSlugCladdingVolume()
 slugCladdingVolume = property(GetSlugCladdingVolume,None,None,None)

 def GetCladdingVolume(self): 
     return self.__GetCladdingVolume()
 claddingVolume = property(GetCladdingVolume,None,None,None)

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

 def GetFuelPhase(self): 
     return self._fuelPhase
 def SetFuelPhase(self,phase): 
     self._fuelPhase = phase
 fuelPhase = property(GetFuelPhase,SetFuelPhase,None,None)

 def GetCladdingPhase(self): 
     return self._claddingPhase
 def SetCladdingPhase(self,phase): 
     self._claddingPhase = phase
 claddingPhase = property(GetCladdingPhase,SetCladdingPhase,None,None)

#*******************************************************************************
# Internal class helpers 

 def __GetName(self):
     return self._specs.loc['Name',1]

 def __GetSlugType(self):
     return self._specs.loc['Slug type',1]

 def __GetNSlugs(self):
     return int(self._specs.loc['Number of slugs',1])

 def __GetFuelEnrichment(self):
     return float(self._specs.loc['Enrichment [U-235 wt%]',1])

 def __GetOuterSlugFreshUMass(self):
     return float(self._specs.loc['U mass outer slug [kg]',1])*1000.0  # [g]
 def __GetInnerSlugFreshUMass(self):
     return float(self._specs.loc['U mass inner slug [kg]',1])*1000.0  # [g]

 def __GetOuterSlugCladdingMass(self):
     return float(self._specs.loc['Cladding mass outer slug [kg]',1])*1000.0  # [g]
 def __GetInnerSlugCladdingMass(self):
     return float(self._specs.loc['Cladding mass inner slug [kg]',1])*1000.0  # [g]

 def __GetFreshUMass(self):
     nSlugs = self.__GetNSlugs()
     uMassOuterSlug = self.__GetOuterSlugFreshUMass()
     uMassInnerSlug = self.__GetInnerSlugFreshUMass()
     return nSlugs*(uMassOuterSlug + uMassInnerSlug)

 def __GetFreshU238Mass(self):
     totalUMass     = self.__GetFreshUMass()
     fuelEnrichment = self.__GetFuelEnrichment()
     return totalUMass * (1.0-fuelEnrichment/100.0)

 def __GetFreshU235Mass(self):
     totalUMass     = self.__GetFreshUMass()
     fuelEnrichment = self.__GetFuelEnrichment()
     return totalUMass * fuelEnrichment/100.0

 def __GetCladdingMass(self):
     nSlugs = self.__GetNSlugs()
     cladMassOuterSlug = self.__GetOuterSlugCladdingMass()
     cladMassInnerSlug = self.__GetInnerSlugCladdingMass()
     return nSlugs*(cladMassOuterSlug + cladMassInnerSlug)

 def __GetSlugLength(self):
     return float(self._specs.loc['Slug length [in]',1]) * 2.54 # cm

 def __SetSlugLength(self,x):
     self._specs.loc['Slug length [in]',1] = x / 2.54 # in
     return

 def __GetOuterSlugOD(self):
     return float(self._specs.loc['Outer slug O.D. [in]',1]) * 2.54 # cm
 def __GetOuterSlugID(self):
     return float(self._specs.loc['Outer slug I.D. [in]',1]) * 2.54 # cm

 def __GetInnerSlugOD(self):
     return float(self._specs.loc['Inner slug O.D. [in]',1]) * 2.54 # cm
 def __GetInnerSlugID(self):
     return float(self._specs.loc['Inner slug I.D. [in]',1]) * 2.54 # cm

 def __GetCladdingWallThickness(self):
     return float(self._specs.loc['Cladding wall thickness [mm]',1]) # mm
 def __GetCladdingEndThickness(self):
     return float(self._specs.loc['Cladding end thickness [mm]',1]) # mm

 def __GetSlugFuelVolume(self):
     slugLength = self.__GetSlugLength()
     cladWallThickness = self.__GetCladdingWallThickness()/10.0
     cladEndThickness = self.__GetCladdingEndThickness()/10.0
     fuelLength = slugLength - 2.0*cladEndThickness
     fuelOuterSlugOuterRadius = self.__GetOuterSlugOD()/2.0 - cladWallThickness
     fuelOuterSlugInnerRadius = self.__GetOuterSlugID()/2.0 + cladWallThickness
     outerVolume = fuelLength * math.pi * (fuelOuterSlugOuterRadius**2 - fuelOuterSlugInnerRadius**2)
     fuelInnerSlugOuterRadius = self.__GetInnerSlugOD()/2.0 - cladWallThickness
     fuelInnerSlugInnerRadius = self.__GetInnerSlugID()/2.0 + cladWallThickness
     innerVolume = fuelLength * math.pi * (fuelInnerSlugOuterRadius**2 - fuelInnerSlugInnerRadius**2)
     return outerVolume + innerVolume

 def __GetSlugVolume(self):
     slugLength = self.__GetSlugLength()
     outerSlugOuterRadius = self.__GetOuterSlugOD()/2.0 
     outerSlugInnerRadius = self.__GetOuterSlugID()/2.0 
     outerVolume = slugLength * math.pi * (outerSlugOuterRadius**2 - outerSlugInnerRadius**2)
     innerSlugOuterRadius = self.__GetInnerSlugOD()/2.0 
     innerSlugInnerRadius = self.__GetInnerSlugID()/2.0 
     innerVolume = slugLength * math.pi * (innerSlugOuterRadius**2 - innerSlugInnerRadius**2)
     return outerVolume + innerVolume

 def __GetSlugCladdingVolume(self):
     return self.__GetSlugVolume() - self.__GetSlugFuelVolume()

 def __GetFuelVolume(self):
     slugFuelVolume = self.__GetSlugFuelVolume()
     nFuelSlugs = self.__GetNSlugs()
     return slugFuelVolume * nFuelSlugs

 def __GetCladdingVolume(self):
     slugCladdingVolume = self.__GetSlugCladdingVolume()
     nFuelSlugs = self.__GetNSlugs()
     return slugCladdingVolume * nFuelSlugs

 def __GetFuelMass(self): # mass of the solid phase 
     return self._fuelPhase.GetQuantity('mass').value
 def __GetFuelMassUnit(self): # mass of the solid phase 
     return self._fuelPhase.GetQuantity('mass').unit

 def __GetFuelRadioactivity(self): # radioactivity of the solid phase
     return self._fuelPhase.GetQuantity('radioactivity').value

 def __GetRadioactivity(self): # radioactivity of the fuel bucket
     return self._fuelPhase.GetQuantity('radioactivity').value 

 def __GetGammaPwr(self): # gamma pwr of the fuel bucket
     return self._fuelPhase.GetQuantity('gamma').value 

 def __GetHeatPwr(self): # heat pwr of the fuel bucket
     return self._fuelPhase.GetQuantity('heat').value 

#*******************************************************************************
# Printing of data members
 def __str__( self ):
     s = 'FuelBucket():\n*******\n specs:\n*******\n %s\n'
     t = '***********\n fuelPhase:\n**********\n %s\n'
     u = '***************\n claddingPhase:\n***************\n %s\n'
     stu = s+t+u
     return stu % (self._specs, self._fuelPhase, self._claddingPhase)

 def __repr__( self ):
     s = 'FuelBucket():\n*******\n specs:\n*******\n %s\n'
     t = '***********\n fuelPhase:\n**********\n %s\n'
     u = '***************\n claddingPhase:\n***************\n %s\n'
     stu = s+t+u
     return stu % (self._specs, self._fuelPhase, self._claddingPhase)
#*******************************************************************************
# Usage: -> python interface.py
if __name__ == "__main__":
   print('Unit testing for FuelBucket')
