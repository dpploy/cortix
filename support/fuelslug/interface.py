#!/usr/bin/env python
"""
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

Fuel slug 

VFdALib support classes 

Thu Dec 15 16:18:39 EST 2016
"""

#*******************************************************************************
import os, sys
import pandas
from ._fuelslug  import _FuelSlug      # constructor
from ._getattribute import _GetAttribute  
#*******************************************************************************

#*******************************************************************************
class FuelSlug():

 def __init__( self, 
               geometry = pandas.Series(),
               species  = list()
             ):

  # constructor
  _FuelSlug( self, 
             geometry, species )

#*******************************************************************************

#*******************************************************************************
# Setters and Getters methods
#-------------------------------------------------------------------------------
# These are passing arguments by value effectively. Because the python objects
# passed into/out of the function are immutable.

 def GetGeometry(self):
     return self._geometry
 geometry = property(GetGeometry,None,None,None)

 def GetSpecies(self):
     return self._species
 species = property(GetSpecies,None,None,None)

 def GetSpecie(self, name):
     for specie in self._species:
       if specie.name == name: return specie
     return None 
 specie = property(GetSpecie,None,None,None)

 def GetAttribute(self, name, symbol=None, series=None):
     return _GetAttribute( self, name, symbol, series )

#*******************************************************************************
# Printing of data members
 def __str__( self ):
     s = 'FuelSlug(): %s\n %s\n'
     return s % (self._geometry, self._species)

 def __repr__( self ):
     s = 'FuelSlug(): %s\n %s\n'
     return s % (self._geometry, self._species)
#*******************************************************************************
