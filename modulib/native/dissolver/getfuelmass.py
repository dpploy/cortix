#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Nitrino module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
#*********************************************************************************

#---------------------------------------------------------------------------------
def GetFuelMass( self ):

  mass = 0.0
  massUnit = 'null'

  if self.fuelSegments is None: return None

  segmentsGeoData = self.fuelSegments[0]
  for segmentData in segmentsGeoData:
    for (name,unit,value) in segmentData:
      if name=='mass': 
        mass += value
        massUnit = unit

  return (mass,massUnit)

#*********************************************************************************
