"""
Valmor de Almeida dealmeidav@ornl.gov; vfda

This Secie class is to be used with other classes in plant-level process modules.

Sun Sep 20 17:00:09 EDT 2015
"""

#*******************************************************************************
import os, sys

from ..periodictable import ELEMENTS
#*******************************************************************************

#*******************************************************************************
def _UpdateMolarMass( self ):

 self._nAtoms        = 0
 self._nNuclideTypes = 0

 nuclides = dict()

 if len(self._atoms) > 0:
   nAtoms = 0
   summ = 0.0
   for entry in self._atoms:
     assert type(entry) == type(str()), 'oops'
     # format example:  3.2*O-18, or 3*O or O or O-16
     tmp = entry.split('*')
     multiple  = 1.0
     # single nuclide    
     if len(tmp) == 1: 
        nuclide = tmp[0]
     # multiple nuclide
     elif len(tmp) == 2: 
        multiple = float(tmp[0])
        nuclide = tmp[1]
     else:
        assert False

     nuclides[ nuclide ] = multiple
     nAtoms += multiple

     try: 
       tmp = nuclide.split('-')
       if len(tmp) == 1:
          element = ELEMENTS[tmp[0]]
          molarMass = element.exactmass # from isotopic composition
       elif len(tmp) == 2:
          element = ELEMENTS[tmp[0]].isotopes[int(tmp[1].strip('m'))]
          molarMass = element.mass
#          print( element, molarMass )
       else:
          assert False
     except KeyError:
       summ += multiple * 0.0
     else:
       summ += multiple * molarMass    

   self._molarMass = summ
#   print( summ )
   self._nAtoms    = nAtoms
   self._nNuclideTypes = len(nuclides)

 return

#*******************************************************************************
