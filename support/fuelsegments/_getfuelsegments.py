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

# Return the fuel segments of a given group (if the groupKey is given), otherwise
# returns an ordered list of pairs of all segments in all groups and their keys.
# That is, [ (timeStamp,fuelSegment), (timeStamp,fuelSegment), ... ]

# *ALWAYS* return the list of segments held by the group when a groupKey is given.

# If the groupKey does not exist return an empty list()

#---------------------------------------------------------------------------------
def _GetFuelSegments(self, groupKey=None):

  if groupKey is None:  # return an ordered list of all fuelSegments

    tmp = list()
    timeStamp = list()
    for (key, fuelSegments) in self.groups.items():
      if fuelSegments is None: continue
      tmp += fuelSegments
      timeStamp += [key for i in fuelSegments] # all fuel segments in the group have 
                                               # the same time stamp

    # sort fuelSegments in order of their keys
    data = zip(timeStamp, tmp)  # this is a list of pairs
    sorted_data = sorted(data, key=lambda entry: entry[0], reverse=False)
#    tmp = [ y for (x,y) in sorted_data ]  # oldest first
    return sorted_data

  else:

    if groupKey not in self.groups.keys(): return list()

    return  self.groups[groupKey] 
       
#*********************************************************************************
