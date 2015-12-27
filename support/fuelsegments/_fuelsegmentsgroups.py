"""
Valmor de Almeida dealmeidav@ornl.gov; vfda

Fuel segment 

VFdALib support classes 

Sat May  9 21:40:48 EDT 2015 created; vfda
"""

#*******************************************************************************
import os, sys

from .fuelsegment import FuelSegment
#*******************************************************************************

#*******************************************************************************
# constructor
# FuelSegmentsGroups simply encapsulates a dictionary of a list of 
# FuelSegment objects. The key is typically a time stamp. 
# A FuelSegment object has two data members, a pandas Series for geometry spec
# and a pandas DataFrame for property density.

def _FuelSegmentsGroups( self, key, fuelSegments=None ):

# This is the central member data
  self.groups = dict()

  assert key not in self.groups.keys()

  if fuelSegments is not None:
     assert type(fuelSegments) == type(list())
     assert type(fuelSegments[-1]) == type(FuelSegment())
     self.groups[key] = fuelSegments
  else:
     self.groups[key] = list()

  return

#*******************************************************************************
