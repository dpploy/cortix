"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Phase container

VFdALib support classes 

Sat Sep  5 13:44:19 EDT 2015
"""
#*******************************************************************************
import os, sys
import pandas

from ..specie.interface import Specie
from ..quantity.interface import Quantity
#*******************************************************************************

#*******************************************************************************
# constructor

def _Phase( self, timeStamp, species=None, quantities=None, value=0.0 ):

  assert type(timeStamp) == type(float())

  if species is not None: 
     assert type(species) == type(list())
     if len(species) > 0:
        assert type(species[-1]) == type(Specie())

  if quantities is not None: 
     assert type(quantities) == type(list())
     if len(quantities) > 0:
        assert type(quantities[-1]) == type(Quantity())

  assert type(value) == type(float())

# List of species and quantities objects; columns of data frame are named by objects
  self._species    = species       # list
  self._quantities = quantities    # list

  names = list()

  if species is not None:
     for specie in self._species:
         names.append(specie.name)
         specie.massCC = value     # massCC in specie is overriden here

  if quantities is not None:
     for quant in self._quantities:
         names.append(quant.name)
         quant.value = value       # value in quant is overriden here

# Table data phase 
  self._phase = pandas.DataFrame( index=[timeStamp], columns = names )
  self._phase.fillna( float(value), inplace = True )
  
 
  return

#*******************************************************************************
