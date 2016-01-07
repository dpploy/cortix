#!/usr/bin/env python
"""
Author: Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Phase container

VFdALib support classes 

Sat Sep  5 01:26:53 EDT 2015
"""

#*******************************************************************************
import os, sys
from ._phase  import _Phase
import pandas

from ..specie.interface import Specie
from ..quantity.interface import Quantity
#*******************************************************************************

#*******************************************************************************
class Phase():

 def __init__( self, 
               timeStamp,
               species    = None,   
               quantities = None,   
               value      = float(0.0)
             ):

   # constructor
   _Phase( self, timeStamp, species, quantities, value )

   return
#*******************************************************************************

#*******************************************************************************
# Setters and Getters methods
#-------------------------------------------------------------------------------
# These are passing arguments by value effectively. Because the python objects
# passed into/out of the function are immutable.

 def GetActors(self): 
     return list(self.phase.columns)  # return all names in order

 def GetTimeStamps(self): 
     return list(self.phase.index)  # return all time stamps 

 def GetSpecie(self, name):
     for specie in self._species:
         if specie.name == name:
            return specie
     return None 

 def GetSpecies(self):
     return self._species
 species = property(GetSpecies,None,None,None)

 def GetQuantities(self):
     return self.quantities

 def SetSpecieId(self, name, val):
     for specie in self._species:
         if specie.name == name:
            specie.flag = val
            return 

 def GetQuantity(self, name):
     for quant in self.quantities:
         if quant.name == name:
            return quant
     return None 

 def AddSpecie(self, newSpecie):
     assert type(newSpecie) == type(Specie())
     assert newSpecie.name not in list(self.phase.columns), 'quantity: %r exists. Current names: %r'%(newQuant,self.phase.columns)
     speciesFormulae = [ specie.formula for specie in self._species ]
     assert newSpecie.formula not in speciesFormulae
     self._species.append( newSpecie )
     newName = newSpecie.name
     col = pandas.DataFrame( index=list(self.phase.index), columns=[newName] )
     col.fillna(0.0)
     tmp = self.phase
     df = tmp.join( col, how='outer' )
     df = df.fillna(0.0)
     self.phase = df

 def AddQuantity(self, newQuant):
     assert type(newQuant) == type(Quantity())
     assert newQuant.name not in list(self.phase.columns), 'quantity: %r exists. Current names: %r'%(newQuant,self.phase.columns)
     quantFormalNames = [ quant.formalName for quant in self.quantities ]
     assert newQuant.formalName not in quantFormalNames
     self.quantities.append( newQuant )
     newName = newQuant.name
     col = pandas.DataFrame( index=list(self.phase.index), columns=[newName] )
     col.fillna(0.0)
     tmp = self.phase
     df = tmp.join( col, how='outer' )
     df = df.fillna(0.0)
     self.phase = df

 def AddRow(self, timeStamp, rowValues):

     assert timeStamp not in self.phase.index

     assert len(rowValues) == len(self.phase.columns)
     tmp = dict()
     for (i,v) in zip( self.phase.columns, rowValues ): 
         tmp[i] = float(v)
     row = pandas.DataFrame( tmp, index=[timeStamp], columns=list(self.phase.columns) )
     frames = [self.phase, row]
     self.phase = pandas.concat( frames )
     return

 def GetRow(self, timeStamp=None):
     if timeStamp is None:
        timeStamp = self.phase.index[-1]
     else:
        assert timeStamp in self.phase.index, 'no timeStamp = %r'%(timeStamp)
     return list(self.phase.loc[timeStamp,:])

 def GetColumn(self, actor):
     assert actor in self.phase.columns
     return list(self.phase.loc[:,actor])

 def ScaleRow(self, timeStamp, value):
     assert timeStamp in self.phase.index
     self.phase.loc[timeStamp,:] *= float(value)
     return

 def ClearHistory(self, value=0.0):
     self.phase.loc[:,:] = float(value)
     return

 def GetValue(self, actor, timeStamp=None):
     if timeStamp is None:
        timeStamp = self.phase.index[-1]
     else:
        assert timeStamp in self.phase.index
     assert actor in self.phase.columns
     return self.phase.loc[timeStamp,actor]

 def SetValue(self, timeStamp, actor, value):
# vfda: change this later
# def SetValue(self, actor, value=None, timeStamp=None):
     assert timeStamp in self.phase.index, 'missing timeStamp = %r'%(timeStamp)
     assert actor in self.phase.columns
     self.phase.loc[timeStamp,actor] = float(value)
     return

 def WriteHTML( self, fileName ):
     assert type(fileName) == type(str())
     tmp = pandas.DataFrame(self.phase)
     columnNames = tmp.columns
     speciesNames = [ specie.name for specie in self._species ]
     quantityNames = [ quantity.name for quantity in self.quantities ]
     for col in columnNames:
         if col in speciesNames: 
            idx = speciesNames.index(col)
            specie = self._species[idx]
            tmp.rename( columns={col:specie.formula}, inplace=True )
         elif col in quantityNames: 
            idx = quantityNames.index(col)
            quant = self.quantities[idx]
            tmp.rename( columns={col:col+'['+quant.unit+']'}, inplace=True )
         else: assert False,'oops fatal.'
     tmp.to_html( fileName )

#*******************************************************************************
# Printing of data members
# def __str__( self ):
     s = 'Phase(): %s;\n %s;\n'
     return s % (self.quantities, self._species)
#
 def __repr__( self ):
     s = 'Phase(): %s;\n %s;\n'
     return s % (self.quantities, self._species)
#*******************************************************************************
