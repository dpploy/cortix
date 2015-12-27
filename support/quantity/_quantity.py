"""
Valmor de Almeida dealmeidav@ornl.gov; vfda

This Quantity class is to be used with other classes in plant-level process modules.

Sat Sep  5 13:59:00 EDT 2015
"""

#*******************************************************************************
import os, sys

#*******************************************************************************

#*******************************************************************************
# constructor

def _Quantity( self, 
               name       = 'null-quantity',
               formalName = 'null-quantity',
               value      = float(0.0),
               unit       = 'null-value'
             ):

     self._name       = name
     self._formalName = formalName
     self._value      = value 
     self._unit       = unit 

#*******************************************************************************
