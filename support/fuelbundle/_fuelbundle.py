"""
Valmor de Almeida dealmeidav@ornl.gov; vfda

This FuelBundle class is a container for usage with other plant-level process modules.

Sat Sep  5 13:59:00 EDT 2015
"""

#*******************************************************************************
import os, sys
import pandas
#*******************************************************************************

#*******************************************************************************
# constructor

def _FuelBundle( self, 
                 specs = pandas.DataFrame()
               ):

     assert type(specs) == type(pandas.DataFrame()), 'oops not pandas table.'

     self.specs = specs

     return

#*******************************************************************************
