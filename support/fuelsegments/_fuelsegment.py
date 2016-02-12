"""
Valmor de Almeida dealmeidav@ornl.gov; vfda

Fuel segment 

VFdALib support classes 

Sat May  9 21:40:48 EDT 2015 created; vfda
"""

#*******************************************************************************
import os, sys
import pandas

from ..specie.interface import Specie 
#*******************************************************************************

#*******************************************************************************
# constructor

def _FuelSegment( self, geometry, species ):

  assert type(geometry) == type(pandas.Series()), 'fatal.'
  assert type(species)  == type(list()), 'fatal.'
  if type(species) == type(list()) and len(species) > 0:
     assert type(species[0]) == type(Specie())

  self.attributeNames = \
  ['nSegments','fuelVolume','fuelDiameter','fuelLength','mass','massDens','massCC','nuclides','isotopes','radioactivity','radioactivityDens','gamma','gammaDens','heat','heatDens','molarHeatPwr','molarGammaPwr']

  self._geometry = geometry
  self._species  = species

#*******************************************************************************
