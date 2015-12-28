"""
Valmor de Almeida dealmeidav@ornl.gov; vfda

Nuclides constructor

Sat May  9 21:40:48 EDT 2015 created; vfda
"""

#*******************************************************************************
import os, sys
import pandas
#*******************************************************************************

#*******************************************************************************
# constructor

def _Nuclides( self, propertyDensities ):

  assert type(propertyDensities) == type(pandas.DataFrame()), 'fatal.'

  self.attributeNames = \
   ['nuclides', 'isotopes', 'massDens', 'massCC','radioactivityDens', 'thermalDens','heatDens','gammaDens']

  self.chemicalElementSeries = \
  ['alkali metals', 'alkali earth metals', 'lanthanides', 'actinides', 
   'transition metals','noble gases','metalloids','fission products','nonmetals',
   'oxide fission products','halogens', 'minor actinides']

  self.propertyDensities = propertyDensities; 

#*******************************************************************************
