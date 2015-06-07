#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Nitrino module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import math, random
#*********************************************************************************

#---------------------------------------------------------------------------------
def GetFuelVolume( self ):

  volume = 0.0
  volumeUnit = 'null'

  if self.fuelSegments is None: return None

  segmentsGeoData = self.fuelSegments[0]

  for segmentData in segmentsGeoData:
    for (name,unit,value) in segmentData:
      if name=='length': 
        length = value
        lengthUnit = unit
      if name=='innerDiameter': 
        iD = value
        iDUnit = unit
    volume += length * math.pi * iD * iD / 4.0

  if lengthUnit=='mm' and iDUnit=='mm': 
     volumeUnit = 'cc'
     volume /= 1000.0
  else:
     assert True, 'invalid unit'

  return (volume,volumeUnit)

#*********************************************************************************
