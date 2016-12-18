#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Fuel slug support class

A FuelSlug object describes the full composition and geometry of a fuel
slug.

Thu Jun 25 18:16:06 EDT 2015
"""
#*********************************************************************************
import os, sys, io, time, datetime
import math, random
from ..periodictable import ELEMENTS
from ..periodictable import SERIES
#*********************************************************************************

# Get stored fuel slug property either overall or on a nuclide basis 

#---------------------------------------------------------------------------------
def _GetAttribute(self, attributeName, nuclide=None, series=None ):

  assert attributeName in self.attributeNames, ' attribute name: %r; options: %r; fail.' % (attributeName,self.attributeNames)

  if nuclide is not None: assert len(nuclide.split('*')) == 1 # sanity check

  if nuclide is not None: assert series  is None, 'fail.'
  if series  is not None: assert nuclide is None, 'fail.'

  if series is not None: assert False,' not implemented.'

  if attributeName == 'isotopes': assert nuclide is not None, 'need a nuclide symbol.'

#.................................................................................
# # of slugs

  if attributeName == 'nSlugs':  return 1

#.................................................................................
# slugId   

  if attributeName == 'slugType': return self._specs['Slug type'] 

#.................................................................................
# slug volume

  if attributeName == 'slugVolume':   return  __GetSlugVolume( self )

#.................................................................................
# fuel volume

  if attributeName == 'fuelVolume':   return  __GetFuelVolume( self )

#.................................................................................
# cladding volume

  if attributeName == 'claddingVolume':   return  __GetCladdingVolume( self )

#.................................................................................
# fuel length        

  if attributeName == 'fuelLength':  return __GetFuelLength( self )

#.................................................................................
# fuel slug overall quantities
  if nuclide is None and series is None:

# mass or mass concentration
     if attributeName == 'fuelMassCC' or attributeName == 'fuelMassDens' or attributeName == 'fuelMass': 
        massCC = 0.0
        for spc in self._fuelPhase.species:
            massCC += spc.massCC
        if attributeName == 'fuelMassCC' or attributeName == 'fuelMassDens': 
          return massCC
        else:
          volume = __GetFuelVolume( self )
          return massCC * volume
# mass or mass concentration
     if attributeName == 'claddingMassCC' or attributeName == 'claddingMassDens' or attributeName == 'claddingMass': 
        massCC = 0.0
        for spc in self._claddingPhase.species:
            massCC += spc.massCC
        if attributeName == 'claddingMassCC' or attributeName == 'claddingMassDens': 
          return massCC
        else:
          volume = __GetCladdingVolume( self )
          return massCC * volume
# radioactivity 
     if attributeName == 'radioactivtyDens' or attributeName == 'radioactivity':
        radDens = 0.0
        for spc in self._fuelPhase.species:
            radDens += spc.molarRadioactivity * spc.molarCC
        if attributeName == 'radioactivityDens': 
          return radDens
        else:
          volume = __GetFuelVolume( self )
          return radDens * volume
# gamma          
     if attributeName == 'gammaDens' or attributeName == 'gamma':
        gammaDens = 0.0
        for spc in self._fuelPhase.species:
            gammaDens += spc.molarGammaPwr * spc.molarCC
        if attributeName == 'gammaDens': 
          return gammaDens
        else:
          volume = __GetFuelVolume( self )
          return gammaDens * volume
# heat           
     if attributeName == 'heatDens' or attributeName == 'heat':
        heatDens = 0.0
        for spc in self._fuelPhase.species:
            heatDens += spc.molarHeatPwr * spc.molarCC
        if attributeName == 'heatDens': 
          return heatDens
        else:
          volume = __GetFuelVolume( self )
          return heatDens * volume

#.................................................................................
# radioactivity               

  if attributeName == 'radioactivityDens' or attributeName == 'radioactivity': 
     assert False
     colName = 'Radioactivity Dens. [Ci/cc]'

#.................................................................................
# thermal                     

  if attributeName == 'thermalDens' or attributeName == 'thermal' or  \
     attributeName == 'heatDens'    or attributeName == 'heat': 
     assert False
     colName = 'Thermal Dens. [W/cc]'

#.................................................................................
# gamma                       

  if attributeName == 'gammaDens' or attributeName == 'gamma': 
     assert False
     colName = 'Gamma Dens. [W/cc]'

#.................................................................................
##################################################################################
#.................................................................................

#  if attributeName[-4:] == 'Dens' or attributeName[-2:] == 'CC': 
#     attributeDens = True
#  else:
#     attributeDens = False 

#.................................................................................
# all nuclide content of the fuel added

#  if nuclide is None and series is None:
#
#     density = 0.0
#
#     density = self.propertyDensities[ colName ].sum()
#
#     if attributeDens is False:  
#        volume = __GetFuelSlugVolume( self )
#        prop = density * volume
#        return prop
#     else:
#        return density

#.................................................................................
# get chemical element series

#  if series is not None:
# 
#     density = 0.0
#
#     for isotope in isotopes:
#       density += self.propertyDensities.loc[isotope,colName]
#
#     if attributeDens is False:  
#        volume = __GetFuelSlugVolume( self )
#        prop = density * volume
#        return prop
#     else:
#        return density
   
#.................................................................................
# get specific nuclide (either the isotopes of the nuclide or the specific isotope) property

  if nuclide is not None:

    # a particular nuclide given (atomic number and atomic mass number)
    if len(nuclide.split('-')) == 2: 

       nuclideMassNumber = int(nuclide.split('-')[1].strip('m'))
       nuclideSymbol     = nuclide.split('-')[0]
       nuclideMolarMass  = ELEMENTS[nuclideSymbol].isotopes[nuclideMassNumber].mass

       massCC = 0.0

       for spc in self._fuelPhase.species:

         formula = spc.atoms

         moleFraction = 0.0

         for item in formula:

           if len(item.split('*')) == 1: # no multiplier (implies 1.0)

             formulaNuclideSymbol = item.split('-')[0].strip()
             if formulaNuclideSymbol == nuclideSymbol: assert len(item.split('-')) == 2

             if item.split('*')[0].strip() == nuclide: 
                moleFraction = 1.0
             else:
                moleFraction = 0.0

           elif len(item.split('*')) == 2: # with multiplier

             formulaNuclideSymbol = item.split('*')[1].split('-')[0].strip()
             if formulaNuclideSymbol == nuclideSymbol: assert len(item.split('*')[1].split('-')) == 2

             if item.split('*')[1].strip() == nuclide: 
                moleFraction = float(item.split('*')[0].strip()) 
             else:
                moleFraction = 0.0

           else:
             assert False

           massCC += spc.molarCC * moleFraction * nuclideMolarMass

       return  massCC * __GetFuelVolume( self )

  # chemical element given (only atomic number given)
    elif len(nuclide.split('-')) == 1: 

       massCC = 0.0

       for spc in self._fuelPhase.species:

         formula = spc.atoms

         for item in formula:

           moleFraction = 0.0

           if len(item.split('*')) == 1: # no multiplier (implies 1.0)

             assert len(item.split('-')) == 2
             formulaNuclideSymbol = item.split('-')[0].strip()
             formulaNuclideMassNumber = int(item.split('-')[1].strip('m'))
             formulaNuclideMolarMass = ELEMENTS[formulaNuclideSymbol].isotopes[formulaNuclideMassNumber].mass

             if formulaNuclideSymbol == nuclide: 
                moleFraction = 1.0
             else:
                moleFraction = 0.0

           elif len(item.split('*')) == 2: # with multiplier

             assert len(item.split('*')[1].split('-')) == 2
             formulaNuclideSymbol = item.split('*')[1].split('-')[0].strip()
             formulaNuclideMassNumber = int(item.split('*')[1].split('-')[1].strip('m'))
             formulaNuclideMolarMass = ELEMENTS[formulaNuclideSymbol].isotopes[formulaNuclideMassNumber].mass

             if formulaNuclideSymbol == nuclide: 
                moleFraction = float(item.split('*')[0].strip()) 
             else:
                moleFraction = 0.0

           else:
             assert False

           massCC += spc.molarCC * moleFraction * formulaNuclideMolarMass

       return  massCC * __GetFuelVolume( self )

    else:

      assert False

#---------------------------------------------------------------------------------
def __GetSlugLength(self):

  return self._specs['Slug length [cm]'] 

#---------------------------------------------------------------------------------
def __GetFuelLength(self):

  slugLength = __GetSlugLength(self)

  cladEndCapThickness = self._specs['Cladding end cap thickness [cm]']
  fuelLength = slugLength - 2.0*cladEndCapThickness

  return fuelLength

#---------------------------------------------------------------------------------
def __GetSlugVolume(self):
 
  slugLength  = __GetSlugLength(self)

  outerSlugOuterRadius = self._specs['Outer slug OD [cm]'] / 2.0
  outerSlugInnerRadius = self._specs['Outer slug ID [cm]'] / 2.0
  outerSlugVolume = slugLength * math.pi * \
                    ( outerSlugOuterRadius**2 - outerSlugInnerRadius**2 )
  innerSlugOuterRadius = self._specs['Inner slug OD [cm]'] / 2.0
  innerSlugInnerRadius = self._specs['Inner slug ID [cm]'] / 2.0
  innerSlugVolume = slugLength * math.pi * \
                    ( innerSlugOuterRadius**2 - innerSlugInnerRadius**2 )

  return outerSlugVolume + innerSlugVolume

#---------------------------------------------------------------------------------
def __GetFuelVolume(self):
 
  fuelLength = __GetFuelLength(self)

  cladWallThickness = self._specs['Cladding wall thickness [cm]']
  outerFuelOuterRadius = self._specs['Outer slug OD [cm]']/2.0 - cladWallThickness
  outerFuelInnerRadius = self._specs['Outer slug ID [cm]']/2.0 + cladWallThickness

  outerFuelVolume = fuelLength * math.pi*( outerFuelOuterRadius**2 - outerFuelInnerRadius**2)

  innerFuelOuterRadius = self._specs['Inner slug OD [cm]']/2.0 - cladWallThickness
  innerFuelInnerRadius = self._specs['Inner slug ID [cm]']/2.0 + cladWallThickness

  innerFuelVolume = fuelLength * math.pi*( innerFuelOuterRadius**2 - innerFuelInnerRadius**2)

  volume = outerFuelVolume + innerFuelVolume

  return volume

#---------------------------------------------------------------------------------
def __GetCladdingVolume(self):

   slugVolume = __GetSlugVolume(self)
   fuelVolume = __GetFuelVolume(self)

   return slugVolume - fuelVolume

#*********************************************************************************
