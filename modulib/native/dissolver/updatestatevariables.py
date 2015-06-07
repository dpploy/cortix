#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Nitrino module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import math, random
from .getvolatilespecies import GetVolatileSpecies
from .leachfuel          import LeachFuel
#*********************************************************************************

#---------------------------------------------------------------------------------
def UpdateStateVariables( self, facilityTime, timeStep ):
  
  """
  if self.volatileSpecies is not None:

    # place holder for evolving species in dissolution; 
    # modeling as a log-normal distribution with positive skewness (right-skewness)

    # here is the mass packet entering the system at facilityTime

    for key in self.volatileSpecies:

      (mass, massUnit) = self.volatileSpecies[ key ] 

      t0 = self.dissolutionStartedTime 
      tf = t0 + self.dutyPeriod
      sigma = 0.7  # right-skewness
      mean = math.log(10) + sigma**2

      t = facilityTime - t0

      if t == 0: 
        logNormalPDF = 0.0
      else:
        logNormalPDF = 1.0/t/sigma/math.sqrt(2.0*math.pi) * \
                       math.exp( - (math.log(t) - mean)**2 / 2/ sigma**2 )

      if key == 'Xe':
        variability = 1.0 - random.random() * 0.15
        self.historyXeMassVapor[ facilityTime + timeStep ] = mass * logNormalPDF * variability

      if key == 'Kr':
        variability = 1.0 - random.random() * 0.15
        self.historyKrMassVapor[ facilityTime + timeStep ] = mass * logNormalPDF * variability

      if key == 'I2':
        massSplit = 0.85
        mass *= massSplit
#        variability = 1.0 - random.random() * 0.10
        variability = 1.0 
        self.historyI2MassVapor[ facilityTime + timeStep ] = mass * logNormalPDF * variability
#        print(' self.historyI2MassVapor = ', self.historyI2MassVapor)
#        print(' self.historyI2MassLiquid = ', self.historyI2MassLiquid)
        self.historyI2MassLiquid[ facilityTime + timeStep ] = \
             self.historyI2MassLiquid[ facilityTime ] + \
             self.historyI2MassVapor[ facilityTime + timeStep ] * (1.0-massSplit) * timeStep

      if key == 'HTO':
        massSplit = 0.50
        mass *= massSplit
        variability = 1.0 
        self.historyHTOMassVapor[ facilityTime + timeStep ] = mass * logNormalPDF * variability
        self.historyHTOMassLiquid[ facilityTime + timeStep ] = \
             self.historyHTOMassLiquid[ facilityTime ] + \
             self.historyHTOMassVapor[ facilityTime + timeStep ] * (1.0-massSplit) * timeStep

      if key == 'RuO4':
        variability = 1.0 - random.random() * 0.15
        self.historyRuO4MassVapor[ facilityTime + timeStep ] = mass * logNormalPDF * variability

      if key == 'CO2':
        variability = 1.0 - random.random() * 0.15
        self.historyCO2MassVapor[ facilityTime + timeStep ] = mass * logNormalPDF * variability

  else:

    self.historyXeMassVapor[ facilityTime + timeStep ]   = 0.0
    self.historyKrMassVapor[ facilityTime + timeStep ]   = 0.0
    self.historyI2MassVapor[ facilityTime + timeStep ]   = 0.0
    self.historyHTOMassVapor[ facilityTime + timeStep ]   = 0.0
    self.historyI2MassLiquid[ facilityTime + timeStep ]  = 0.0
    self.historyHTOMassLiquid[ facilityTime + timeStep ]  = 0.0
    self.historyRuO4MassVapor[ facilityTime + timeStep ] = 0.0
    self.historyCO2MassVapor[ facilityTime + timeStep ]  = 0.0

  """

  if self.fuelSegments is not None:


    LeachFuel( self, facilityTime, timeStep )

    species = GetVolatileSpecies(self)

    for key in species:

      (mass, massUnit) = species[ key ] 

      if key == 'Xe':
        self.historyXeMassVapor[ facilityTime + timeStep ] = \
             self.volatileSpecies0[key][0] - mass

      if key == 'Kr':
        self.historyKrMassVapor[ facilityTime + timeStep ] = \
             self.volatileSpecies0[key][0] - mass 

      if key == 'I2':
        massSplit = 0.85
        self.historyI2MassVapor[ facilityTime + timeStep ] =  \
             (self.volatileSpecies0[key][0] - mass) * massSplit
        self.historyI2MassLiquid[ facilityTime + timeStep ] = \
             (self.volatileSpecies0[key][0] - mass) * (1.0-massSplit)
#        print(' **************************** ')
#        print(' self.volatileSpecies0   = ',  self.volatileSpecies0[key][0])
#        print(' self.historyI2MassVapor = ',  self.historyI2MassVapor[facilityTime+timeStep])
#        print(' self.historyI2MassLiquid = ', self.historyI2MassLiquid[facilityTime+timeStep])
#        print(' **************************** ')

      if key == 'HTO':
        massSplit = 0.20
        self.historyHTOMassVapor[ facilityTime + timeStep ] = \
             (self.volatileSpecies0[key][0] - mass) * massSplit
        self.historyHTOMassLiquid[ facilityTime + timeStep ] = \
             (self.volatileSpecies0[key][0] - mass) * (1.0-massSplit)

      if key == 'RuO4':
        self.historyRuO4MassVapor[ facilityTime + timeStep ] = \
             self.volatileSpecies0[key][0] - mass

      if key == 'CO2':
        self.historyCO2MassVapor[ facilityTime + timeStep ] = \
             self.volatileSpecies0[key][0] - mass

  else:

      self.historyXeMassVapor[ facilityTime + timeStep ]   = 0.0
      self.historyKrMassVapor[ facilityTime + timeStep ]   = 0.0
      self.historyI2MassVapor[ facilityTime + timeStep ]   = 0.0
      self.historyHTOMassVapor[ facilityTime + timeStep ]   = 0.0
      self.historyRuO4MassVapor[ facilityTime + timeStep ] = 0.0
      self.historyCO2MassVapor[ facilityTime + timeStep ]  = 0.0

      self.historyI2MassLiquid[ facilityTime + timeStep ]  = 0.0
      self.historyHTOMassLiquid[ facilityTime + timeStep ]  = 0.0

      self.historyHNO3MolarLiquid[ facilityTime + timeStep ]  = self.startingHNO3Molarity 
      self.historyH2OMassLiquid[facilityTime] = 1000.0 * self.dissolverVolume - self.startingHNO3Molarity * self.molarMassHNO3 * self.dissolverVolume
      self.historyUNMassConcLiquid[ facilityTime + timeStep ] = 0.0
      self.historyPuNMassConcLiquid[ facilityTime + timeStep ] = 0.0
      self.historyFPNMassConcLiquid[ facilityTime + timeStep ] = 0.0

      self.historyNOMassVapor[ facilityTime + timeStep ]   = 0.0
      self.historyNO2MassVapor[ facilityTime + timeStep ]   = 0.0

      self.historyRuO4MassVapor[ facilityTime + timeStep ] = 0.0
      self.historyCO2MassVapor[ facilityTime + timeStep ]  = 0.0

#*********************************************************************************
