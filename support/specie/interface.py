#!/usr/bin/env python
"""
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

This Specie class is to be used with other classes in plant-level process modules.
NB: Species is always a plural but here, the class is named as singular to
    reflect one specie. If many species are used in an external context, the plural
    can be used.

For unit testing do at the linux command prompt:
    python specie.py

NB: the definition of chemical specie here is extended to ficticious compounds.
    This is done as follows. Say MAO2 is a ficticious compound denoting a 
    minor actinides dioxide. The list of atoms is given as follows:

    ['0.49*Np-237', '0.42*Am-241', '0.08*Am-243', '0.01*Cm-244', '2.0*O-16']

    note the MA forming nuclides add to 1 = 0.49 + 0.42 + 0.08 + 0.01. Hence
    therefore the number of atoms in this compound is 3. 1 MA "atom" and 2 O.
    The nuclide is indicated by the element symbol followed by a dash and the 
    atomic mass number.

    Other forms can be used for common true species

    ['Np-237', '2.0*O-16'] or ['Np-237', 'O-16', 'O-16'] or [ '2*H', 'O' ] or
    [ 'H', 'O', 'H' ]  etc...
 
    This code will calculate the molar mass of any species with a given valid
    atom list using a provided periodic table of chenical elements. The user 
    can also reset the value of the molar mass with a setter method.

Sat May  9 21:40:48 EDT 2015 created; vfda
"""

#*******************************************************************************
import os, sys

from ._specie import _Specie  # constructor
from ._updatenatoms import _UpdateNAtoms  # constructor
#*******************************************************************************

#*******************************************************************************
class Specie():

 def __init__( self, 
               name    = 'null',
               formula = 'null',
               phase   = 'null',
               atoms   = list(),
               molarCC = 0.0,      # M (mole/L)
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

 def GetNAtoms(self): # number of ficticious atoms in the species (see NB above)
     return self._nAtoms       
 nAtoms = property(GetNAtoms,None,None,None)

 def GetNNuclides(self): # number of all nuclides involved in the species definition
     return self._nNuclides    
 nNuclides = property(GetNNuclides,None,None,None)

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
     s = ' %5s %5s %5s '+' molar mass: %6s '+' molar cc: %6s '+' mass cc: %6s '+' flag: %s '+'# atoms: %s'+' atoms: %s'+' molar radioactivity: %s'+' molar heat pwr: %s'+' molar gamma pwr: %s\n'
     return s % (self.name, self.formula, self.phase, self.molarMass, self.molarCC, self.massCC, self.flag, self.nAtoms, self.atoms, self.molarRadioactivity, self.molarHeatPwr, self.molarGammaPwr)

 def __repr__( self ):
     s = ' %5s %5s %5s '+' molar mass: %6s '+' molar cc: %6s '+' mass cc: %6s '+' flag: %s '+'# atoms: %s'+' atoms: %s'+' molar radioactivity: %s'+' molar heat pwr: %s'+' molar gamma pwr: %s\n'
     return s % (self.name, self.formula, self.phase, self.molarMass, self.molarCC, self.massCC, self.flag, self.nAtoms, self.atoms, self.molarRadioactivity, self.molarHeatPwr, self.molarGammaPwr)
#*******************************************************************************
