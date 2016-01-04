"""
Valmor de Almeida dealmeidav@ornl.gov; vfda

This Secie class is to be used with other classes in plant-level process modules.

Sun Sep 20 17:00:09 EDT 2015
"""

#*******************************************************************************
import os, sys

from ..periodictable import ELEMENTS
#*******************************************************************************

# FIX ME: THIS IS duplicated

#*******************************************************************************
# constructor

def _UpdateNAtoms( self ):

     assert False

     self._nAtoms = 0
     if len(self._atoms) > 0:
       nAtoms = 0
       summ = 0.0
       for entry in self._atoms:
         assert type(entry) == type(str()), 'oops'
         # format example:  3.2*O-18, or 3*O or O or O-16
         tmp = entry.split('*')
         multiple  = 1.0
         # no multiple atoms
         if len(tmp) == 1: 
            symbol = tmp[0]
         # multiple atoms
         elif len(tmp) == 2: 
            multiple = float(tmp[0])
            symbol = tmp[1]
         else:
            assert False

         nAtoms += multiple

         try: 
           tmp = symbol.split('-')
           if len(tmp) == 1:
              element = ELEMENTS[tmp[0]]
           elif len(tmp) == 2:
              element = ELEMENTS[tmp[0]].isotopes[int(tmp[1].strip('m'))]
           else:
              assert False
         except KeyError:
           summ += multiple * 0.0
         else:
           summ += multiple * element.mass

       self._molarMass = summ
       self._nAtoms    = nAtoms

     if self._molarMass == 0.0:
       self._molarCC = 0.0
       self._massCC  = 0.0


#*******************************************************************************
