"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Stream container

VFdALib support classes 

Sat Aug 15 17:24:18 EDT 2015
"""

#*******************************************************************************
import os, sys
import pandas

from ..specie.interface import Specie
from ..quantity.interface import Quantity
#*******************************************************************************

#*******************************************************************************
# constructor

def _Stream( self, timeStamp, species=None, quantities=None, values=0.0 ):

  assert type(timeStamp) == type(float())

  self.timeStamp = timeStamp

  if species is not None: 
     assert type(species) == type(list())
     if len(species) > 0:
        assert type(species[-1]) == type(Specie())

  if quantities is not None: 
     assert type(quantities) == type(list())
     if len(quantities) > 0:
        assert type(quantities[-1]) == type(Quantity())

#  assert type(value) == type(float())

# List of quantities and species objects
  self.species    = species       # list
  self.quantities = quantities    # list

  names = list() # note order of names; values must be in the same order; caution

  for specie in self.species:
      names.append(specie.name)

  for quant in self.quantities:
      names.append(quant.name)

# ORDERED data; caution!!
# Table data stream 
  self.stream = pandas.DataFrame( index=[timeStamp], columns = names )
  if type(values) == type(float()): 
     self.stream.fillna( values, inplace = True )
  else:
     self.stream.fillna( 0.0, inplace = True )

  if type(values) == type(list()) and len(values) == len(names):
     for (name,val) in zip( names, values):
         self.stream.loc[timeStamp,name] = val
   
  return

#*******************************************************************************
