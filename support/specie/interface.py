#!/usr/bin/env python
"""
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

This Specie class is to be used with other classes in plant-level process modules.
NB: Species is always a plural but here, the class is named as singular to
    reflect one species. If many species are used in an external context, the plural
    can be used without conflict.

For unit testing do at the linux command prompt:
    python specie.py

NB: The Specie() class encapsulate either the molecular or empirical chemical
    formula of a compound.
    The definition of chemical specie here is extended to ficticious compounds.
    This is done as follows. Say MAO2 is either a molecular or empirical chemical
    formula of a ficticious compound denoting a minor actinides dioxide. The list 
    of atoms is given as follows:

    ['0.49*Np-237', '0.42*Am-241', '0.08*Am-243', '0.01*Cm-244', '2.0*O-16']

    note the MA forming nuclides add to 1 = 0.49 + 0.42 + 0.08 + 0.01. Hence
    therefore the number of atoms in this compound is 3. 1 MA "atom" and 2 O.
    Note that the total number of "atoms" is obtained by summing all multipliers:
    0.49 + 0.42 + 0.08 + 0.01 + 2.0.
    The nuclide is indicated by the element symbol followed by a dash and the 
    atomic mass number. Here the number of nuclide types is 5 (self._nNuclideTypes).

    The numbers preceeding the nuclide symbol before the * will referred to as
    multipliers. The sum of the multipliers will add to the number of "atoms" in
    the formula. WARNING: a multiplier could be in the format 0.00e-00. In this 
    case a hiphen may appear twice, e.g.: 1.549e-09*U-233

    Other forms can be used for common true species

    ['Np-237', '2.0*O-16'] or ['Np-237', 'O-16', 'O-16'] or [ '2*H', 'O' ] or
    [ 'H', 'O', 'H' ]  etc...
 
    This code will calculate the molar mass of any species with a given valid
    atom list using a provided periodic table of chemical elements. The user 
    can also reset the value of the molar mass with a setter method.

Sat May  9 21:40:48 EDT 2015 created; vfda
"""

#*******************************************************************************
import os, sys

from ._specie import _Specie              # constructor
from ._updatemolarmass import _UpdateMolarMass  
#*******************************************************************************

#*******************************************************************************
class Specie():

 def __init__( self, 
               name        = 'null',
               formulaName = 'null',
               phase       = 'null',
               atoms       = list(),
               molarCC     = 0.0,      # default unit: M (mole/L)
               massCC      = 0.0,      # default unit: g/L
               flag        = None   ):

     # constructor
     _Specie( self, 
              name,
              formulaName,
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

 def GetName(self):
     return self._name
 def SetName(self,n):
     self._name = n
 name = property(GetName,SetName,None,None)

 def GetFormulaName(self):
     return self._formulaName
 def SetFormulaName(self,f):
     self._formulaName = f
 formulaName = property(GetFormulaName,SetFormulaName,None,None)

 def GetPhase(self):
     return self._phase
 def SetPhase(self,p):
     self._mass = p
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

 def GetMolarRadioactivityFractions(self):
     return self._molarRadioactivityFractions
 def SetMolarRadioactivityFractions(self,fracs):
     assert type(fracs) == type(list()), 'oops not list.'
     assert len(fracs) == len(self._atoms), 'oops not right length,'
     if len(fracs) != 0:
        assert type(fracs[-1]) == type(float()), 'oops not float.'
     self._molarRadioactivityFractions = fracs
 molarRadioactivityFractions = property(GetMolarRadioactivityFractions,SetMolarRadioactivityFractions,None,None)

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
 
 # Deprecated 
 def GetAtoms(self):
     return self._atoms       
 def SetAtoms(self, atoms):
     assert type(atoms) == type(list()), 'oops not list.'
     if len(atoms) != 0:
        assert type(atoms[-1]) == type(str()), 'oops not string.'
     self._atoms = atoms
     _UpdateMolarMass(self)
 atoms = property(GetAtoms,SetAtoms,None,None)

 # New interface 
 def GetFormula(self):
     return self._atoms       
 def SetFormula(self, atoms):
     assert type(atoms) == type(list()), 'oops not list.'
     if len(atoms) != 0:
        assert type(atoms[-1]) == type(str()), 'oops not string.'
     self._atoms = atoms
     _UpdateMolarMass(self)
 formula = property(GetFormula,SetFormula,None,None)

 def GetNAtoms(self): # number of ficticious atoms in the species (see NB above)
     return self._nAtoms       
 nAtoms = property(GetNAtoms,None,None,None)

 def GetNNuclideTypes(self): # number of nuclide types involved in the species definition
     return self._nNuclideTypes
 nNuclideTypes = property(GetNNuclideTypes,None,None,None)

 def SetFlag(self,f):
     self._flag = f
 def GetFlag(self):
     return self._flag
 flag = property(GetFlag,SetFlag,None,None)

 def GetMolarCC(self):
     return self._molarCC
 def SetMolarCC(self,v):
     self._molarCC = v
     self._massCC  = v * self._molarMass
 molarCC = property(GetMolarCC,SetMolarCC,None,None)

 def GetMolarCCUnit(self):
     return self._molarCCUnit
 def SetMolarCCUnit(self,v):
     self._molarCCUnit = v
 molarCCUnit = property(GetMolarCCUnit,SetMolarCCUnit,None,None)

 def GetMassCC(self):
     return self._massCC
 def SetMassCC(self,v):
     self._massCC = v
     self._molarCC = v / self._molarMass
 massCC = property(GetMassCC,SetMassCC,None,None)

 def GetMassCCUnit(self):
     return self._massCCUnit
 def SetMassCCUnit(self,v):
     self._massCCUnit = v
 massCCUnit = property(GetMassCCUnit,SetMassCCUnit,None,None)

#*******************************************************************************
# Internal helpers 


#*******************************************************************************
# Printing of data members
 def __str__( self ):
     s = 'Specie(): name=%s; formulaName=%s; phase=%s;'+' formula=%s;'+' # atoms=%s;'+' # nuclide types=%s;'+' molar mass=%s[%s];'+' molar cc=%s[%s];'+' mass cc=%s[%s];'+' flag=%s;'+' molar radioactivity=%s[%s];'+' molar heat pwr=%s[%s];'+' molar gamma pwr=%s[%s];'+' molar radioactivity fractions=%s.\n'
     return s % (self.name, self.formulaName, self.phase, self.atoms, self.nAtoms, self.nNuclideTypes, self.molarMass, self.molarMassUnit, self.molarCC, self.molarCCUnit, self.massCC, self.massCCUnit, self.flag, self.molarRadioactivity, self.molarRadioactivityUnit, self.molarHeatPwr, self.molarHeatPwrUnit, self.molarGammaPwr, self.molarGammaPwrUnit, self.molarRadioactivityFractions)

 def __repr__( self ):
     s = 'Specie(): name=%s; formulaName=%s; phase=%s;'+' formula=%s;'+' # atoms=%s;'+' # nuclide types=%s;'+' molar mass=%s[%s];'+' molar cc=%s[%s];'+' mass cc=%s[%s];'+' flag=%s;'+' molar radioactivity=%s[%s];'+' molar heat pwr=%s[%s];'+' molar gamma pwr=%s[%s];'+' molar radioactivity fractions=%s.\n'
     return s % (self.name, self.formulaName, self.phase, self.atoms, self.nAtoms, self.nNuclideTypes, self.molarMass, self.molarMassUnit, self.molarCC, self.molarCCUnit, self.massCC, self.massCCUnit, self.flag, self.molarRadioactivity, self.molarRadioactivityUnit, self.molarHeatPwr, self.molarHeatPwrUnit, self.molarGammaPwr, self.molarGammaPwrUnit, self.molarRadioactivityFractions)
#*******************************************************************************
