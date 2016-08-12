"""
Valmor de Almeida dealmeidav@ornl.gov; vfda

This Secie class is to be used with other classes in plant-level process modules.

Tue Aug  9 00:35:53 EDT 2016
"""

#*******************************************************************************
import os, sys

#*******************************************************************************

#*******************************************************************************
def _FormulaCleanup( self ):

 if len(self._atoms) > 0:

   # save the multiplier value as a string type of scientific notation
   for entry in self._atoms:

     assert type(entry) == type(str()), 'oops'

     # format example:  3.2*O-18, or 3*O or O or O-16
     tmp = entry.split('*')

     multiplier = 0.0

     if len(tmp) == 1:
        continue
     elif len(tmp) == 2: 
        multiplier = float(tmp[0])
     else:
        assert False

     assert multiplier != 0.0, 'multiplier = %r'%(multiplier)

     multiplier = '{0:9.3e}'.format( multiplier )

     self._atoms[ self._atoms.index( entry ) ] = multiplier+'*'+tmp[1]

   # order in decreasing order of multiplier magnitude
   multipliers_lst = list()

   for entry in self._atoms:

     tmp = entry.split('*')

     multiplier = 0.0

     if len(tmp) == 1:
        continue
     elif len(tmp) == 2: 
        multiplier = float(tmp[0])
     else:
        assert False

     multipliers_lst.append( float( multiplier ) )

   sortedAtoms_lst = [ a for (i,a) in sorted( zip(multipliers_lst,self._atoms), 
                                              key=lambda pair: pair[0],
                                              reverse=True ) ]

   self._atoms = sortedAtoms_lst

 return

#*******************************************************************************
