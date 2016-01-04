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

# If an attibute is not found, Return 0 even if a groupKey is not found
# Don't change this behavior; it will break user's code.

#---------------------------------------------------------------------------------
def _GetGroupAttribute(self, groupKey=None, attributeName=None, symbol=None, series=None ):

  assert attributeName is not None, 'fatal.'
 
  attribute = None 

# Either cumulative or average density property for all fuel segments for *all* groups
# BE VERY CAREFUL HERE: groups with no segments will reduce the average density value
  if groupKey is None:  

     attribute = 0

     for (key, fuelSegments) in self.groups.items():
       assert type(fuelSegments) == type(list()), 'fail.'
       if len(fuelSegments) == 0: continue  # this will reduce the average value
       groupAttribute = 0
       for fuelSegment in fuelSegments:
          groupAttribute += fuelSegment.GetAttribute( attributeName, symbol, series )

       if attributeName[-4:] == 'Dens' or attributeName[-2:] == 'CC': 
          groupAttribute /= len(fuelSegments)
       attribute += groupAttribute 

     if attribute != 0 and \
        (attributeName[-4:] == 'Dens' or attributeName[-2:] == 'CC'):
        attribute /= len(self.groups)

#     if attributeName[-4:] == 'Dens' or attributeName[-2:] == 'CC': 
#        print('HELLO density '+attributeName+' ', attribute)

# Get average property in all fuel segments within a groupKey
  else:                

     if groupKey not in self.groups.keys(): return 0

     fuelSegments = self.groups[ groupKey ]

     if len(fuelSegments) is 0: return 0

     attribute = 0

     for fuelSegment in fuelSegments:
       attribute += fuelSegment.GetAttribute( attributeName, symbol, series )

     if attribute != 0 and \
        (attributeName[-4:] == 'Dens' or attributeName[-2:] == 'CC'):
        attribute /= len(fuelSegments)
   
  return attribute

#*********************************************************************************
