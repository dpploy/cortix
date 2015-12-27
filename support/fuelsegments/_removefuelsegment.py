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

#---------------------------------------------------------------------------------
def _RemoveFuelSegment(self, groupKey, fuelSegment_remove):

  assert groupKey in self.groups.keys(), 'fail.'

  fuelSegments = self.groups[ groupKey ]
  nSegments    = len(fuelSegments)

  for fuelSegment in fuelSegments:
    if fuelSegment.GetAttribute('segmentId') == fuelSegment_remove.GetAttribute('segmentId'): 
       fuelSegments.remove( fuelSegment )

  assert len(self.groups[groupKey]) == nSegments-1, 'fatal.'

#*********************************************************************************
