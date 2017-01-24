#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Fuel slug support class

A FuelSlug object describes the full composition and geometry of a fuel
slug.

Sat Jan 21 00:17:23 EST 2017
"""
#*********************************************************************************
import os, sys, io, time, datetime
import math, random

from ._getattribute import _GetAttribute  
#*********************************************************************************

# Shrink the volume based on the equivalent cladding hollow sphere 

#---------------------------------------------------------------------------------
def _ReduceCladdingVolume(self, dissolvedVolume ):

  assert dissolvedVolume >=0.0, 'dissolved volume= %r; failed.' % (dissolvedVolume)

  if dissolvedVolume == 0.0: return

  if self._claddingHollowSphereRo == self._claddingHollowSphereRi: return

  dV = dissolvedVolume
  pi = math.pi

  # get this first
  massDens = _GetAttribute( self, 'claddingMassDens' )

#.................................................................................
# reduce the volume of the cladding hollow sphere

  ro = self._claddingHollowSphereRo 
  ri = self._claddingHollowSphereRi

  volume = 4.0/3.0*pi * ( ro**3 - ri**3 )

  if dV < volume:

    ro = ( ri**3 + 3.0/4.0/pi*(volume - dV) )**(1/3)
    self._claddingHollowSphereRo = ro

  else:

    self._claddingHollowSphereRo = 0.0
    self._claddingHollowSphereRi = 0.0

    cladWallThickness   = self._specs['Cladding wall thickness [cm]']
    cladEndCapThickness = self._specs['Cladding end cap thickness [cm]']

    self._specs['Inner slug ID [cm]'] += cladWallThickness
    self._specs['Inner slug OD [cm]'] -= cladWallThickness
    self._specs['Outer slug ID [cm]'] += cladWallThickness
    self._specs['Outer slug OD [cm]'] -= cladWallThickness

    self._specs['Slug length [cm]'] -= 2.0*cladEndCapThickness

    self._specs['Cladding wall thickness [cm]']    = 0.0
    self._specs['Cladding end cap thickness [cm]'] = 0.0

#.................................................................................
# Update the history of the cladding phase

  volume   = _GetAttribute( self, 'equivalentCladdingVolume' )
  self._claddingPhase.SetValue('volume',volume) 

  self._claddingPhase.SetValue('mass',massDens*volume)


#*********************************************************************************
