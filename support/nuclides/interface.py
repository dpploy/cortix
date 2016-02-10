#!/usr/bin/env python
"""
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

Nuclides container
The purpose of the this container is to store and query a table of nuclides.
Typically the table is filled in with data from an ORIGEN calculation.

VFdALib support classes 

Sat Jun 27 14:46:49 EDT 2015
"""

#*******************************************************************************
import os, sys
import pandas

from ._nuclides  import _Nuclides      # constructor
from ._getattribute import _GetAttribute  
#*******************************************************************************

#*******************************************************************************
class Nuclides():

 def __init__( self, 
               propertyDensities = pandas.DataFrame()
             ):

  # constructor
  _Nuclides( self, 
             propertyDensities )

#*******************************************************************************

#*******************************************************************************
# Setters and Getters methods
#-------------------------------------------------------------------------------
# These are passing arguments by value effectively. Because the python objects
# passed into/out of the function are immutable.

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
