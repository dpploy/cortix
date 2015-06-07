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
# "Derive" species from elemental composition from fuel load
def GetVolatileSpecies( self ):

  species = dict()

  if self.fuelSegments is None: return None
 
  massI2   = 0.0
  massKr   = 0.0
  massXe   = 0.0
  massHTO  = 0.0
  massRuO4 = 0.0
  massCO2  = 0.0

  segmentsCompData = self.fuelSegments[1]

  for segmentData in segmentsCompData:

    for (name,unit,value) in segmentData:
      if name=='I': 
         massI2    += value/2.0
         massI2Unit = unit
      if name=='Kr': 
         massKr    += value
         massKrUnit = unit
      if name=='Xe': 
         massXe    += value
         massXeUnit = unit
      if name=='Ru': 
         massRuO4   += value + value/101.07*4.0*16.0
         massRuO4Unit = unit
      if name=='C': 
         massCO2    += value + value/14.0*2.0*16.0
         massCO2Unit = unit
      if name=='3H': 
         massHTO   += value + value/3.0*1.0*(16.0+1.0)
         massHTOUnit = unit
    # end of: for (name,unit,value) in segmentData:

  # end of: for segmentData in segmentsCompData:

  species['I2']   = ( massI2, massI2Unit )
  species['Kr']   = ( massKr, massKrUnit )
  species['Xe']   = ( massXe, massXeUnit )
  species['RuO4'] = ( massRuO4, massRuO4Unit )
  species['CO2']  = ( massCO2, massCO2Unit )
  species['HTO']  = ( massHTO, massHTOUnit )

  return species

#*********************************************************************************
