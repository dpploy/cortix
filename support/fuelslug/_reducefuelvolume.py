#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Fuel slug support class

A FuelSlug object describes the full composition and geometry of a fuel
slug.

Thu Jan 26 00:51:30 EST 2017
"""
#*********************************************************************************
import os, sys, io, time, datetime
import math, random

from ._getattribute import _GetAttribute  
#*********************************************************************************

# Shrink the volume based on the equivalent fuel hollow sphere 

#---------------------------------------------------------------------------------
def _ReduceFuelVolume(self, dissolvedVolume ):

  assert dissolvedVolume >=0.0, 'dissolved volume= %r; failed.' % (dissolvedVolume)

  if dissolvedVolume == 0.0: return

  if self._fuelHollowSphereRo == self._fuelHollowSphereRi: return

  assert self._claddingHollowSphereRo == 0.0
  assert self._claddingHollowSphereRi == 0.0

  dV = dissolvedVolume
  pi = math.pi

  # get this first
  massDens = _GetAttribute( self, 'fuelMassDens' )

#.................................................................................
# reduce the volume of the fuel hollow sphere

  ro = self._fuelHollowSphereRo 
  ri = self._fuelHollowSphereRi

  volume = 4.0/3.0*pi * ( ro**3 - ri**3 )

  if dV < volume:

    ro = ( ri**3 + 3.0/4.0/pi*(volume - dV) )**(1/3)
    self._fuelHollowSphereRo = ro

  else:

    self._fuelHollowSphereRo = 0.0
    self._fuelHollowSphereRi = 0.0

    self._specs['Inner slug ID [cm]'] = 0.0
    self._specs['Inner slug OD [cm]'] = 0.0
    self._specs['Outer slug ID [cm]'] = 0.0
    self._specs['Outer slug OD [cm]'] = 0.0

    self._specs['Slug length [cm]'] = 0.0

    self._specs['Cladding wall thickness [cm]']    = 0.0
    self._specs['Cladding end cap thickness [cm]'] = 0.0

#.................................................................................
# Update the history of the fuel phase

  volume   = _GetAttribute( self, 'equivalentFuelVolume' )
  self._fuelPhase.SetValue('volume',volume) 

  self._fuelPhase.SetValue('mass',massDens*volume)


#*********************************************************************************
