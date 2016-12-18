"""
Valmor de Almeida dealmeidav@ornl.gov; vfda

This Secie class is to be used with other classes in plant-level process modules.

Sat May  9 21:40:48 EDT 2015 created; vfda
"""
#*******************************************************************************
import os, sys

from ._updatemolarmass import _UpdateMolarMass
from ..periodictable   import ELEMENTS
#*******************************************************************************

#*******************************************************************************
# constructor

def _Specie( self, 
             name        = 'null',
             formulaName = 'null',
             phase       = 'null',
             atoms       = list(),
             molarCC     = 0.0,      # default unit: M 
             massCC      = 0.0,      # default unit: g/L
             flag        = None   ):

 assert type(name) == type(str()), 'oops not string.'
 self._name = name;    

 assert type(formulaName) == type(str()), 'oops not string.'
 self._formulaName = formulaName; 

 assert type(phase) == type(str()), 'oops not string.'
 self._phase = phase;   

 assert type(atoms) == type(list()), 'oops not list.'
 self._atoms = atoms;   

 self._flag = flag  # flag can be any type

 self._molarMass = 0.0
 self._molarHeatPwr = 0.0
 self._molarGammaPwr = 0.0
 self._molarRadioactivity = 0.0

 self._molarMassUnit = 'g/mole'

 self._molarHeatPwrUnit = 'W/mole'
 self._molarGammaPwrUnit = 'W/mole'
 self._molarRadioactivityUnit = 'Ci/mole'

 self._molarRadioactivityFractions = list()

 self._molarCCUnit = 'mole/L'
 self._massCCUnit  = 'g/L'

 
 _UpdateMolarMass( self )


 if self._molarMass == 0.0:
   self._molarCC = 0.0
   self._massCC  = 0.0
   return

 assert type(molarCC) == type(float()), 'oops not a float.'
 assert molarCC >= 0.0, 'oops negative value.'
 self._molarCC = molarCC
 self._massCC  = molarCC * self._molarMass

 assert type(massCC) == type(float()), 'oops not a float.'
 assert massCC >= 0.0, 'oops negative value.'
 if self._massCC == 0.0: 
    self._massCC  = massCC 
    self._molarCC = massCC / self._molarMass

 return

#*******************************************************************************
