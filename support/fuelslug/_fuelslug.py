"""
Valmor de Almeida dealmeidav@ornl.gov; vfda

Fuel slug 

VFdALib support classes 

Sat May  9 21:40:48 EDT 2015 created; vfda
"""

#*******************************************************************************
import os, sys
import math, random
import pandas
from copy import deepcopy

from ..phase.interface  import Phase

from ._getattribute import _GetAttribute  
#*******************************************************************************

#*******************************************************************************
# constructor

def _FuelSlug( self, specs, fuelPhase, claddingPhase ):

  assert type(specs)         == type(pandas.Series()), 'fatal.'
  assert type(fuelPhase)     == type(Phase()), 'fatal.'
  assert type(claddingPhase) == type(Phase()), 'fatal.'

  self.attributeNames = \
  ['nSlugs','slugType','slugVolume','slugArea','fuelVolume','claddingVolume','claddingArea','equivalentCladdingVolume','equivalentCladdingArea','fuelLength','slugLength','fuelMass','fuelMassDens','fuelMassCC','claddingMass','claddingMassDens','claddingMassCC','nuclides','isotopes','radioactivity','radioactivityDens','gamma','gammaDens','heat','heatDens','molarHeatPwr','molarGammaPwr']

  # own internal copy
  self._specs         = deepcopy( specs )
  self._fuelPhase     = deepcopy( fuelPhase )
  self._claddingPhase = deepcopy( claddingPhase )

  # setup the equivalent cladding hollow sphere
  pi = math.pi

  area   = _GetAttribute( self, 'claddingArea' )
  volume = _GetAttribute( self, 'claddingVolume' )

  ro = math.sqrt( area/4/pi )
  ri = ( ro**3 - volume*3/4/pi )**(1/3)

  self._claddingHollowSphereRo = ro
  self._claddingHollowSphereRi = ri

#*******************************************************************************
