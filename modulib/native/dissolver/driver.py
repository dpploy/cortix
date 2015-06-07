#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Dissolver module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import math, random
import logging
from .providedata import ProvideData
from .usedata     import UseData
from .dissolve    import Dissolve
#*********************************************************************************

#*********************************************************************************
class Driver():

 def __init__( self, ports=list() ):

  # Sanity test
  assert type(ports) is list, '-> ports type %r is invalid.' % type(ports)
 
  # Logger
  self.log = logging.getLogger('laucher.dissolver')
  self.log.info('initializing an instance of Dissolver')

  # Temporary configuration
  self.solidsMassLoadMax     = 670.0 # gram
  self.dissolverVolume       = 4.0  # liter
  self.dutyPeriod            = 120.0 # minute

  self.molarMassU            = 238.0
  self.molarMassPu           = 239.0
  self.molarMassFP           = 135.34-16*1.18
  self.molarMassH2O          = 18.0    # g/mole
  self.molarMassHNO3         = 63.0    # g/mole
  self.molarMassNO           = 30.01   # g/mole
  self.molarMassNO2          = 46.0055 # g/mole
  self.molarMassUO2          = 270.05
  self.molarMassPuO2         = 271.17
  self.molarMassFPO1dot18    = 135.34
  self.molarMassUO2NO3_2     = self.molarMassUO2 + 62.0*2.0 # g/mole
  self.molarMassPuNO3_4      = self.molarMassPu  + 62.0*4.0 # g/mole
  self.molarMassFPNO3_2dot36 = 328.22

  self.roughnessF = 4.0

  self.rho_uo2       =  8.300  # g/cc
  self.rho_puo2      = 11.460
  self.rho_fpo1dot18 = 12.100

  self.gramDecimals = 7 # tenth of a microgram significant digits
  self.mmDecimals   = 3 # micrometer significant digits
  self.ccDecimals   = 3 # cubic centimeter significant digits
  self.pyplotScale = 'linear' # linear, linear-linear, log, log-log, linear-log, log-linear

  self.startingHNO3Molarity = 10 # Molar

  # Member data 
  self.ports = ports

  self.ready2LoadFuel    = True   # major control variable
  self.dissolutionStartedTime = -1.0   # major control variable

  self.fuelSegments = None # major data: dissolving solids  (time-dependent)

#  self.stateHistory = list(dict())

  self.historyXeMassVapor   = dict()  # persistent variable
  self.historyXeMassVapor[0.0] = 0.0 

  self.historyKrMassVapor   = dict()  # persistent variable
  self.historyKrMassVapor[0.0] = 0.0

  self.historyI2MassVapor   = dict()  # persistent variable
  self.historyHTOMassVapor  = dict()  # persistent variable
  self.historyRuO4MassVapor = dict()  # persistent variable
  self.historyCO2MassVapor  = dict()  # persistent variable

  self.historyI2MassLiquid = dict()  # persistent variable
  self.historyI2MassLiquid[0.0] = 0.0

  self.historyHTOMassLiquid = dict()  # persistent variable
  self.historyHTOMassLiquid[0.0] = 0.0

  self.historyHNO3MolarLiquid = dict()  # persistent variable
  self.historyHNO3MolarLiquid[0.0] = self.startingHNO3Molarity 

  self.historyH2OMassLiquid = dict()  # persistent variable
  self.historyH2OMassLiquid[0.0] = 1000.0 * self.dissolverVolume - self.startingHNO3Molarity * self.molarMassHNO3 * self.dissolverVolume

  self.historyUNMassConcLiquid = dict()  # persistent variable
  self.historyUNMassConcLiquid[0.0] = 0.0

  self.historyPuNMassConcLiquid = dict()  # persistent variable
  self.historyPuNMassConcLiquid[0.0] = 0.0

  self.historyFPNMassConcLiquid = dict()  # persistent variable
  self.historyFPNMassConcLiquid[0.0] = 0.0

  self.historyNOMassVapor   = dict()  # persistent variable
  self.historyNOMassVapor[0.0] = 0.0 

  self.historyNO2MassVapor   = dict()  # persistent variable
  self.historyNO2MassVapor[0.0] = 0.0 

  self.volatileSpecies0 = None 

#---------------------------------------------------------------------------------
 def CallPorts( self, facilityTime=0.0 ):
 
  ProvideData( self, providePortName='signal', atTime=facilityTime )     

  UseData( self, usePortName='solids', atTime=facilityTime )     

  ProvideData( self, providePortName='vapor', atTime=facilityTime )     
  ProvideData( self, providePortName='state', atTime=facilityTime )     

  UseData( self, usePortName='condensate', atTime=facilityTime )     

#---------------------------------------------------------------------------------
# Evolve system from facilityTime to facilityTime+timeStep
 def Execute( self, facilityTime=0.0, timeStep=1.0 ):

  s = 'Execute(): facility time [min] = ' + str(facilityTime)
  self.log.info(s)

  Dissolve( self, facilityTime, timeStep ) # starting at facilityTime advance timeStep

#*********************************************************************************
