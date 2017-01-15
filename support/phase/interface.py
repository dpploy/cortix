#!/usr/bin/env python
"""
Author: Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Phase history container. 

ATTENTION:
The species (list of Specie) and quantities (list of Quantity) data members 
have arbitrary values either at an arbitrary point in the history or at no point in 
the history. 

To obtain history values, associated to the phase, at a particular point in time, 
use the GetValue() method to access the history data frame (pandas) via columns and 
rows. The corresponding values in species and quantities are overriden and not to
be used through the phase interface.

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
               timeStamp  = None,
               species    = None,   
               quantities = None,   
               value      = float(0.0) # note: remove this later and let 0.0 be default
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
     return list(self._phase.columns)  # return all names in order

 def GetTimeStamps(self): 
     return list(self._phase.index)  # return all time stamps 

 def GetSpecie(self, name):
     for specie in self._species:
         if specie.name == name:
            return specie
     return None 

 def GetSpecies(self):
     return self._species
 species = property(GetSpecies,None,None,None)

 def GetQuantities(self):
     return self._quantities
 quantities = property(GetQuantities,None,None,None)

 def SetSpecieId(self, name, val):
     for specie in self._species:
         if specie.name == name:
            specie.flag = val
            return 

 def GetQuantity(self, name):
     for quant in self._quantities:
         if quant.name == name:
            return quant
     return None 

 def AddSpecie(self, newSpecie):
     assert type(newSpecie) == type(Specie())
     assert newSpecie.name not in list(self._phase.columns), 'quantity: %r exists. Current names: %r'%(newQuant,self._phase.columns)
     speciesFormulae = [ specie.formulaName for specie in self._species ]
     assert newSpecie.formulaName not in speciesFormulae
     self._species.append( newSpecie )
     newName = newSpecie.name
     col = pandas.DataFrame( index=list(self._phase.index), columns=[newName] )
     col.fillna(0.0)
     tmp = self._phase
     df = tmp.join( col, how='outer' )
     df = df.fillna(0.0)
     self._phase = df

 def AddQuantity(self, newQuant):
     assert type(newQuant) == type(Quantity())
     assert newQuant.name not in list(self._phase.columns), 'quantity: %r exists. Current names: %r'%(newQuant,self._phase.columns)
     quantFormalNames = [ quant.formalName for quant in self._quantities ]
     assert newQuant.formalName not in quantFormalNames
     self._quantities.append( newQuant )
     newName = newQuant.name
     col = pandas.DataFrame( index=list(self._phase.index), columns=[newName] )
     col.fillna(0.0)
     tmp = self._phase
     df = tmp.join( col, how='outer' )
     df = df.fillna(0.0)
     self._phase = df

 def AddRow(self, timeStamp, rowValues):

     assert timeStamp not in self._phase.index

     assert len(rowValues) == len(self._phase.columns)
     tmp = dict()
     for (i,v) in zip( self._phase.columns, rowValues ): 
         tmp[i] = float(v)
     row = pandas.DataFrame( tmp, index=[timeStamp], columns=list(self._phase.columns) )
     frames = [self._phase, row]
     self._phase = pandas.concat( frames )
     return

 def GetRow(self, timeStamp=None):
     if timeStamp is None:
        timeStamp = self._phase.index[-1]
     else:
        assert timeStamp in self._phase.index, 'no timeStamp = %r'%(timeStamp)
     return list(self._phase.loc[timeStamp,:])

 def GetColumn(self, actor):
     assert actor in self._phase.columns
     return list(self._phase.loc[:,actor])

 def ScaleRow(self, timeStamp, value):
     assert timeStamp in self._phase.index
     self._phase.loc[timeStamp,:] *= float(value)
     return

 def ClearHistory(self, value=0.0):
     self._phase.loc[:,:] = float(value)
     return

 def GetValue(self, actor, timeStamp=None):
     if timeStamp is None:
        timeStamp = self._phase.index[-1]
     else:
        assert timeStamp in self._phase.index
     assert actor in self._phase.columns
     return self._phase.loc[timeStamp,actor]

#old def SetValue(self, timeStamp, actor, value):
#new
 def SetValue(self, actor, value, timeStamp=None):
     if timeStamp is None:
        timeStamp = self._phase.index[-1]
     else:
        assert timeStamp in self._phase.index, 'missing timeStamp = %r'%(timeStamp)
     assert actor in self._phase.columns
     self._phase.loc[timeStamp,actor] = float(value)
     return

 def WriteHTML( self, fileName ):
     assert type(fileName) == type(str())
     tmp = pandas.DataFrame(self._phase)
     columnNames = tmp.columns
     speciesNames = [ specie.name for specie in self._species ]
     quantityNames = [ quantity.name for quantity in self._quantities ]
     for col in columnNames:
         if col in speciesNames: 
            idx = speciesNames.index(col)
            specie = self._species[idx]
            tmp.rename( columns={col:specie.formulaName}, inplace=True )
         elif col in quantityNames: 
            idx = quantityNames.index(col)
            quant = self._quantities[idx]
            tmp.rename( columns={col:col+'['+quant.unit+']'}, inplace=True )
         else: assert False,'oops fatal.'
     tmp.to_html( fileName )

#*******************************************************************************
# Printing of data members
# def __str__( self ):
     s = '\n\t **Phase()**: \n\t *quantities*: %s\n\t *species*: %s\n\t *history end*: %s'
     return s % (self._quantities, self._species, self._phase.loc[self._phase.index[-1]:])
#
 def __repr__( self ):
     s = '\n\t **Phase()**: \n\t *quantities*: %s\n\t *species*: %s\n\t *history end*: %s'
     return s % (self._quantities, self._species, self._phase.loc[self._phase.index[-1]:])
#*******************************************************************************
