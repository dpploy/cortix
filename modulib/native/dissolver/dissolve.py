#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Nitrino module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import math, random
from .getfuelmass   import GetFuelMass
from .getfuelvolume import GetFuelVolume
from .updatestatevariables import UpdateStateVariables
from .getvolatilespecies   import GetVolatileSpecies
#*********************************************************************************

#---------------------------------------------------------------------------------
def Dissolve( self, facilityTime, timeStep ):

  #..........
  # new start
  #..........
  if facilityTime == self.dissolutionStartedTime: # this is the beginning of a duty cycle

    s = 'Dissolve(): starting new duty cycle at ' + str(facilityTime) + ' [min]'
    self.log.info(s)
    (mass,unit) = GetFuelMass(self)
    s = 'Dissolve(): loaded mass ' + str(round(mass,3)) + ' [' + unit + ']'
    self.log.info(s)
    (volume,unit) = GetFuelVolume(self)
    s = 'Dissolve(): loaded volume ' + str(round(volume,3)) + ' [' + unit + ']'
    self.log.info(s)
    nSegments = len(self.fuelSegments[0])
    s = 'Dissolve(): new fuel load # segments = ' + str(nSegments)
    self.log.info(s)

    self.volatileSpecies0 = GetVolatileSpecies(self)

    # set initial concentrations in the liquid phase to zero
    self.historyHNO3MolarLiquid[ facilityTime ] = self.startingHNO3Molarity
    self.historyH2OMassLiquid[ facilityTime ] = 1000.0 * self.dissolverVolume - self.startingHNO3Molarity * self.molarMassHNO3 * self.dissolverVolume
    self.historyUNMassConcLiquid[ facilityTime ] = 0.0
    self.historyPuNMassConcLiquid[ facilityTime ] = 0.0
    self.historyFPNMassConcLiquid[ facilityTime ] = 0.0
    self.historyI2MassLiquid[ facilityTime ] = 0.0
    self.historyHTOMassLiquid[ facilityTime ] = 0.0

    self.historyNOMassVapor[ facilityTime ] = 0.0
    self.historyNO2MassVapor[ facilityTime ] = 0.0

    s = 'Dissolve(): begin dissolving...' 
    self.log.info(s)

    #................................................
    UpdateStateVariables( self, facilityTime, timeStep )
    #................................................

  #.....................
  # continue dissolving
  #.....................
  elif facilityTime > self.dissolutionStartedTime and GetFuelMass(self) is not None:

    s = 'Dissolve(): continue dissolving...' 
    self.log.info(s)

    #................................................
    UpdateStateVariables( self, facilityTime, timeStep )
    #................................................

    (mass,unit) = GetFuelMass(self)
    s = 'Dissolve(): solid mass ' + str(round(mass,3)) + ' [' + unit + ']'
    self.log.info(s)
  
    if  facilityTime + timeStep >= self.dissolutionStartedTime + self.dutyPeriod: # prepare for a new load in the next time step

      s = 'Dissolve(): signal new duty cycle for ' + str(facilityTime+timeStep)+' [min]'
      self.log.info(s)

      self.ready2LoadFuel = True

      # send everything to accumulationTank...to be done...
      # for now clear the data
      self.volatileSpecies0 = None
      self.fuelSegments    = None 

  #.............................
  # do nothing in this time step
  #.............................
  else: 

    s = 'Dissolve(): idle and ready ' + str(facilityTime)+' [min]'
    self.log.info(s)

    # set initial concentrations in the liquid phase to zero
    self.historyI2MassLiquid[ facilityTime ] = 0.0
    self.historyHTOMassLiquid[ facilityTime ] = 0.0
    self.historyHNO3MolarLiquid[ facilityTime ] = self.startingHNO3Molarity 
    self.historyH2OMassLiquid[facilityTime] = 1000.0 * self.dissolverVolume - self.startingHNO3Molarity * self.molarMassHNO3 * self.dissolverVolume
    self.historyUNMassConcLiquid[ facilityTime ] = 0.0
    self.historyPuNMassConcLiquid[ facilityTime ] = 0.0
    self.historyFPNMassConcLiquid[ facilityTime ] = 0.0

    self.historyI2MassLiquid[ facilityTime + timeStep ]  = 0.0
    self.historyHTOMassLiquid[ facilityTime + timeStep ]  = 0.0

    self.historyNOMassVapor[ facilityTime ] = 0.0
    self.historyNO2MassVapor[ facilityTime ] = 0.0

    self.historyXeMassVapor[ facilityTime + timeStep ]   = 0.0
    self.historyKrMassVapor[ facilityTime + timeStep ]   = 0.0
    self.historyI2MassVapor[ facilityTime + timeStep ]   = 0.0
    self.historyHTOMassVapor[ facilityTime + timeStep ]   = 0.0
    self.historyRuO4MassVapor[ facilityTime + timeStep ] = 0.0
    self.historyCO2MassVapor[ facilityTime + timeStep ]  = 0.0

    #................................................
    UpdateStateVariables( self, facilityTime, timeStep )
    #................................................

  return

#*********************************************************************************
