"""
Valmor de Almeida dealmeidav@ornl.gov; vfda

This FuelAssembly class is a container for usage with other plant-level process modules.

Sat Sep  5 13:59:00 EDT 2015
"""

#*******************************************************************************
import os, sys
import pandas
#*******************************************************************************

#*******************************************************************************
# constructor

def _FuelBucket( self, 
                 specs = pandas.DataFrame()
               ):

     assert type(specs) == type(pandas.DataFrame()), 'oops not pandas table.'

     self._specs = specs

     self._solidPhase = None

     return

#*******************************************************************************
