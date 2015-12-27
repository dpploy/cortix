#!/usr/bin/env python
"""
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

This Specie class is to be used with other classes in plant-level process modules.

For unit testing do at the linux command prompt:
    python specie.py

Sat May  9 21:40:48 EDT 2015 created; vfda
"""

#*******************************************************************************
import os, sys

from ._specie import _Specie  # constructor
from ._updatenatoms import _UpdateNAtoms  # constructor
#*******************************************************************************

#*******************************************************************************
class Specie():

# Class data
 atomicMass = {
       'null': 0.0, 
       'e'   : 0.548e-3,    # electron
       'H'   : 1.00794, 
       'D'   : 2.01410178, 
       'C'   : 12.0107, 
       'C-12': 12.0107, 
       'C-13': 13, 
       'O'   : 15.9994,
       'N'   : 14.0067,
       'Si'  : 28.0855,
       'P'   : 30.973762, 
       'S'   : 32.065,
       'Cl'  : 35.453,
       'Ga'  : 69.723,
       'Se'  : 79.0,
       'Br'  : 81.0,
       'Kr'  : 83.0,
       'Rb'  : 85.0,
       'Sr'  : 87.62,
       'Y'   : 89.0,
       'Zr'  : 91.224,
       'Nb'  : 95.0,
       'Mo'  : 95.0,
       'Tc'  : 99.0,
       'Ru'  : 100.0,
       'Rh'  : 103.0,
       'Pd'  : 108.0,
       'Ag'  : 109.0,
       'Cd'  : 110.0,
       'Sn'  : 116.0,
       'Sb'  : 121.0,
       'Te'  : 125.0,
       'I'   : 127.0,
       'Xe'  : 128.0,
       'Cs'  : 132.9054,
       'Ba'  : 134.0,
       'La'  : 139.0,
       'Ce'  : 140.0,
       'Pr'  : 141.0,
       'Nd'  : 142.0,
       'Pm'  : 147.0,
       'Sm'  : 147.0,
       'Eu'  : 153.0,
       'Gd'  : 154.0,
       'Tb'  : 159.0,
       'U'   : 238.0,
       'Pu'  : 238.0,
       'Pu-238'  : 238.0,
       'Pu-239'  : 239.0,
       'Pu-240'  : 240.0,
       'Pu-241'  : 241.0,
       'Pu-242'  : 242.0,
       'Pu-244'  : 244.0,
       'Np'  : 237.0,
       'Am'  : 243.0,
       'Cm'  : 244.0,
       'FP'  : 115.365465356,  # Ficticious combined fission products
       'MA'  : 118.999         # Ficticious combined minor actinides    
               }     

 nuclideDecayData = { # 'nuclide' : (halfLife,timeUnit,decayEnergy_keV,decayMode)
       'Pu-238' : (87.7, 'y', 5593.20, 'alpha')
                    }
#*******************************************************************************
 def __init__( self, 
               name    = 'null',
               formula = 'null',
               phase   = 'null',
               atoms   = list(),
               molarCC = 0.0,      # M
               massCC  = 0.0,      # g/L
               flag    = None   ):

     # constructor
     _Specie( self, 
              name,
              formula,
              phase,
              atoms,
              molarCC,
              massCC,
              flag    )

     return

#*******************************************************************************

#*******************************************************************************
# Setters and Getters methods
#-------------------------------------------------------------------------------
# These are passing arguments by value effectively. Because the python objects
# passed into/out of the function are immutable.

 def SetName(self,n):
     self._name = n
 def GetName(self):
     return self._name
 name = property(GetName,SetName,None,None)

 def SetFormula(self,f):
     self._formula = f
 def GetFormula(self):
     return self._formula
 formula = property(GetFormula,SetFormula,None,None)

 def SetPhase(self,p):
     self._mass = p
 def GetPhase(self):
     return self._phase
 phase = property(GetPhase,SetPhase,None,None)

 def GetMolarMass(self):
     return self._molarMass
 def SetMolarMass(self,v):
     self._molarMass = v
 molarMass = property(GetMolarMass,SetMolarMass,None,None)

 def GetMolarMassUnit(self):
     return self._molarMassUnit
 def SetMolarMassUnit(self,v):
     self._molarMassUnit = v
 molarMassUnit = property(GetMolarMassUnit,SetMolarMassUnit,None,None)

 def GetMolarRadioactivity(self):
     return self._molarRadioactivity
 def SetMolarRadioactivity(self,v):
     self._molarRadioactivity = v
 molarRadioactivity = property(GetMolarRadioactivity,SetMolarRadioactivity,None,None)

 def GetMolarRadioactivityUnit(self):
     return self._molarRadioactivityUnit
 def SetMolarRadioactivityUnit(self,v):
     self._molarRadioactivityUnit = v
 molarRadioactivityUnit = property(GetMolarRadioactivityUnit,SetMolarRadioactivityUnit,None,None)

 def GetMolarHeatPwr(self):
     return self._molarHeatPwr
 def SetMolarHeatPwr(self,v):
     self._molarHeatPwr = v
 molarHeatPwr = property(GetMolarHeatPwr,SetMolarHeatPwr,None,None)

 def GetMolarHeatPwrUnit(self):
     return self._molarHeatPwrUnit
 def SetMolarHeatPwrUnit(self,v):
     self._molarHeatPwrUnit = v
 molarHeatPwrUnit = property(GetMolarHeatPwrUnit,SetMolarHeatPwrUnit,None,None)

 def GetMolarGammaPwr(self):
     return self._molarGammaPwr
 def SetMolarGammaPwr(self,v):
     self._molarGammaPwr = v
 molarGammaPwr = property(GetMolarGammaPwr,SetMolarGammaPwr,None,None)

 def GetMolarGammaPwrUnit(self):
     return self._molarGammaPwrUnit
 def SetMolarGammaPwrUnit(self,v):
     self._molarGammaPwrUnit = v
 molarGammaPwrUnit = property(GetMolarGammaPwrUnit,SetMolarGammaPwrUnit,None,None)
 
 def GetAtoms(self):
     return self._atoms       
 def SetAtoms(self, atoms):
     assert type(atoms) == type(list()), 'oops not list.'
     if len(atoms) != 0:
        assert type(atoms[-1]) == type(str()), 'oops not string.'
     self._atoms = atoms
     _UpdateNAtoms(self)
 atoms = property(GetAtoms,SetAtoms,None,None)

 def GetNAtoms(self):
     return self._nAtoms       
 nAtoms = property(GetNAtoms,None,None,None)

 def SetFlag(self,f):
     self._flag = f
 def GetFlag(self):
     return self._flag
 flag = property(GetFlag,SetFlag,None,None)

 def SetMolarCC(self,v):
     self._molarCC = v
     self._massCC  = v * self._molarMass
 def GetMolarCC(self):
     return self._molarCC
 molarCC = property(GetMolarCC,SetMolarCC,None,None)

 def SetMolarCCUnit(self,v):
     self._molarCCUnit = v
 def GetMolarCCUnit(self):
     return self._molarCCUnit
 molarCCUnit = property(GetMolarCCUnit,SetMolarCCUnit,None,None)

 def SetMassCC(self,v):
     self._massCC = v
     self._molarCC = v / self._molarMass
 def GetMassCC(self):
     return self._massCC
 massCC = property(GetMassCC,SetMassCC,None,None)

 def SetMassCCUnit(self,v):
     self._massCCUnit = v
 def GetMassCCUnit(self):
     return self._massCCUnit
 massCCUnit = property(GetMassCCUnit,SetMassCCUnit,None,None)

#*******************************************************************************
# Internal helpers 

 def _GetAtomicMass(self):
     return Specie.atomicMass
 def _GetNuclideDecayData(self):
     return Specie.nuclideDecayData

#*******************************************************************************
# Printing of data members
 def __str__( self ):
     s = ' %5s %5s %5s '+' molar mass: %6s '+' molar cc: %6s '+' mass cc: %6s '+' flag: %s '+'# atoms: %s'+' atoms: %s\n'
     return s % (self.name, self.formula, self.phase, self.molarMass, self.molarCC, self.massCC, self.flag, self.nAtoms, self.atoms)

 def __repr__( self ):
     s = ' %5s %5s %5s '+' molar mass: %6s '+' molar cc: %6s '+' mass cc: %6s '+' flag: %s '+'# atoms: %s'+' atoms: %s\n'
     return s % (self.name, self.formula, self.phase, self.molarMass, self.molarCC, self.massCC, self.flag, self.nAtoms, self.atoms)
#*******************************************************************************
