#!/usr/bin/env python
"""
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

Fuel segment 

VFdALib support classes 

Sat Jun 27 14:46:49 EDT 2015
"""

#*******************************************************************************
import os, sys
import pandas
from ._fuelsegment  import _FuelSegment      # constructor
from ._getattribute import _GetAttribute  
#*******************************************************************************

#*******************************************************************************
class FuelSegment():

 def __init__( self, 
               geometry = pandas.Series(),
               species  = list()
             ):

  # constructor
  _FuelSegment( self, 
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

 def GetAttribute(self, name, symbol=None, series=None):
     return _GetAttribute( self, name, symbol, series )

#*******************************************************************************
# Printing of data members
# def __str__( self ):
#     s = ' %5s %5s %5s '+' molar mass: %6s '+' molar cc: %6s '+' mass cc: %6s '+' flag: %s '+'# atoms: %s'+' atoms: %s\n'
#     return s % (self.name, self.formula, self.phase, self.molarMass, self.molarCC, self.massCC, self.flag, self.nAtoms, self.atoms)
#
# def __repr__( self ):
#     s = ' %5s %5s %5s '+' molar mass: %6s '+' molar cc: %6s '+' mass cc: %6s '+' flag: %s '+'# atoms: %s'+' atoms: %s\n'
#     return s % (self.name, self.formula, self.phase, self.molarMass, self.molarCC, self.massCC, self.flag, self.nAtoms, self.atoms)
#*******************************************************************************
