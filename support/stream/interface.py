#!/usr/bin/env python
"""
Author: Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Stream container

VFdALib support classes 

Sat Aug 15 17:24:02 EDT 2015
"""

#*******************************************************************************
import os, sys
from ._stream  import _Stream
import pandas
#*******************************************************************************

#*******************************************************************************
class Stream():

 def __init__( self, 
               timeStamp,
               species    = None,   
               quantities = None,   
               values = float(0.0)
             ):

     # constructor
     # THIS WILL CREATE AN ORDERED "STREAM"; values must be in order!
     _Stream( self, timeStamp, species, quantities, values )

     return
#*******************************************************************************

#*******************************************************************************
# Setters and Getters methods
#-------------------------------------------------------------------------------
# These are passing arguments by value effectively. Because the python objects
# passed into/out of the function are immutable.

 def GetTimeStamp(self):
     return self.timeStamp    

 def GetActors(self):
     return list(self.stream.columns)

 def GetSpecie(self, name):
     for specie in self.species:
         if specie.name == name:
            return specie
     return None 

 def GetSpecies(self):
     return self.species

 def GetQuantities(self):
     return self.quantities

 def SetSpecieId(self, name, val):
     for specie in self.species:
         if specie.name == name:
            specie.flag = val
            return 

 def GetQuantity(self, name):
     for quant in self.quantities:
         if quant.name == name:
            return quant
     return None 

 def GetRow(self, timeStamp=None):
     if timeStamp is None:
        return list(self.stream.loc[self.timeStamp,:])
     else:
        assert timeStamp in self.stream.index, 'timeStamp = %r'%(timeStamp)
        return list(self.stream.loc[timeStamp,:])

 def GetValue(self, actor, timeStamp=None):
     assert actor in self.stream.columns
     if timeStamp is None:
        return self.stream.loc[self.timeStamp,actor]
     else:
        assert timeStamp in self.stream.index
        return self.stream.loc[timeStamp,actor]

 def SetValue(self, actor, value=None, timeStamp=None):
     assert actor in self.stream.columns
     if timeStamp is None:
        if value is None:
           self.stream.loc[self.timeStamp,actor] = float(0.0)
        else:
           self.stream.loc[self.timeStamp,actor] = float(value)
     else:
        assert timeStamp in self.stream.index, 'timeStamp = %r'%(timeStamp)
        if value is None:
           self.stream.loc[timeStamp,actor] = float(0.0)
        else:
           self.stream.loc[timeStamp,actor] = float(value)

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
