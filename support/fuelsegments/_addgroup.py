#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Fuel segment support class

Thu Jun 25 18:16:06 EDT 2015
"""
#*********************************************************************************
import os, sys, io, time, datetime
import math, random
#*********************************************************************************

# Make fuelSegments *ALWAYS* a list (could be empty)
# If group key exists, add to group otherwise create a group
# If fuelSegments are not given, add an empty list to a group if it exists
# A group will *ALWAYS* have a fuelSegments list.

#---------------------------------------------------------------------------------
def _AddGroup( self, groupKey, fuelSegments=None ):

  if fuelSegments is None: 
     fuelSegments = list()
  else:
     assert type(fuelSegments) == type(list()), 'fail.'

  if groupKey in self.groups.keys(): 
     self.groups[groupKey] += fuelSegments 
  else:                          
     self.groups[groupKey]  = fuelSegments 

#*********************************************************************************
