#!/usr/bin/env python
"""
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

Fuel segment 

VFdALib support classes 

Sat Jun 27 14:46:49 EDT 2015
"""

#*******************************************************************************
import os, sys
from ._fuelsegmentsgroups  import _FuelSegmentsGroups
from ._getgroupattribute   import _GetGroupAttribute
from ._getfuelsegments     import _GetFuelSegments
from ._addgroup            import _AddGroup
from ._removefuelsegment   import _RemoveFuelSegment
#*******************************************************************************

#*******************************************************************************
class FuelSegmentsGroups():

 def __init__( self, 
               key = None, 
               fuelSegments = None 
             ):

     # constructor
     _FuelSegmentsGroups( self, 
                          key, fuelSegments )

#*******************************************************************************

#*******************************************************************************
# Setters and Getters methods
#-------------------------------------------------------------------------------
# These are passing arguments by value effectively. Because the python objects
# passed into/out of the function are immutable.

 def HasGroup(self, key):

     return key in self.groups.keys()        

 def AddGroup(self, key, fuelSegments=None):

     _AddGroup( self, key, fuelSegments )

 def GetAttribute(self, groupKey=None, attributeName=None, 
                        nuclideSymbol=None, nuclideSeries=None):

     return _GetGroupAttribute( self, groupKey, attributeName, nuclideSymbol, nuclideSeries )

 def GetFuelSegments(self, groupKey=None):

     return _GetFuelSegments( self, groupKey )

 def RemoveFuelSegment(self, groupKey, fuelSegment):

     return _RemoveFuelSegment( self, groupKey, fuelSegment )

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
