"""
Valmor de Almeida dealmeidav@ornl.gov; vfda

Fuel segment 

VFdALib support classes 

Sat May  9 21:40:48 EDT 2015 created; vfda
"""

#*******************************************************************************
import os, sys
import pandas
#*******************************************************************************

#*******************************************************************************
# constructor

def _FuelSegment( self, geometry, propertyDensities ):

  assert type(geometry) == type(pandas.Series()), 'fatal.'
  assert type(propertyDensities) == type(pandas.DataFrame()), 'fatal.'

  self.attributeNames = \
   ['isotopes','nSegments','segmentId','fuelVolume',
    'massCC','mass','radioactivityDens',
    'radioactivity','thermalDens','thermal','heatDens','heat','gammaDens','gamma',
    'segmentVolume']

  self.chemicalElementSeries = \
  ['alkali metals', 'alkali earth metals', 'lanthanides', 'actinides', 
   'transition metals','noble gases','metalloids','fission products','nonmetals',
   'oxide fission products','halogens', 'minor actinides']

  self.geometry          = geometry;    
  self.propertyDensities = propertyDensities; 

#*******************************************************************************
