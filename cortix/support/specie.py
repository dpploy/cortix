# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/cortix
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/cortix/blob/master/COPYRIGHT.txt
#
# Licensed under the GNU General Public License v. 3, please see LICENSE file.
# https://www.gnu.org/licenses/gpl-3.0.txt
"""
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

This Specie class is to be used with other classes in plant-level process modules.

NB: Species is always used either in singular or plural cases, the class
    named here reflects one species. If many species are used in an external
    context, the species object name can be used without conflict.

For unit testing do at the linux command prompt:
    python specie.py

NB: The Specie() class encapsulates either the molecular or empirical chemical
    formula of a compound.
    The definition of a chemical species here is extended to ficticious compounds.
    This is done as follows. Say MAO2 is either a molecular or empirical chemical
    formula of a ficticious compound denoting minor actinides dioxide. The list
    of atoms is given as follows:

    ['0.49*Np-237', '0.42*Am-241', '0.08*Am-243', '0.01*Cm-244', '2.0*O-16']

    note the MA forming nuclides add to 1 = 0.49 + 0.42 + 0.08 + 0.01. Therefore
    the number of atoms in this compound is 3. 1 MA "atom" and 2 O.
    Note that the total number of "atoms" is obtained by summing all multipliers:
    0.49 + 0.42 + 0.08 + 0.01 + 2.0.
    The nuclide is indicated by the element symbol followed by a dash and the
    atomic mass number. Here the number of nuclide types is 5 (self._nNuclideTypes).

    The numbers preceeding the nuclide symbol before the * will be referred to as
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

# *******************************************************************************
import os
import sys

from cortix.support.periodictable import ELEMENTS
# *******************************************************************************

# *******************************************************************************


class Specie():

    # todo: phase should not be here; concentrations should not be here
    #      only molar quantities should be here
    #      see the Phase container

    def __init__(self,
                 name='null',
                 formulaName='null',
                 phase='null',
                 atoms=list(),
                 molarCC=0.0,      # default unit: M (mole/L)
                 massCC=0.0,      # default unit: g/L
                 flag=None):

        assert isinstance(name, str), 'oops not string.'
        self._name = name

        assert isinstance(formulaName, str), 'oops not string.'
        self._formulaName = formulaName

        assert isinstance(phase, str), 'oops not string.'
        self._phase = phase

        assert isinstance(atoms, list), 'oops not list.'
        self._atoms = atoms

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
        self._massCCUnit = 'g/L'

        self.__UpdateMolarMass()

        if self._molarMass == 0.0:
            self._molarCC = 0.0
            self._massCC = 0.0
            return

        assert isinstance(molarCC, float), 'oops not a float.'
        assert molarCC >= 0.0, 'oops negative value.'
        self._molarCC = molarCC
        self._massCC = molarCC * self._molarMass

        assert isinstance(massCC, float), 'oops not a float.'
        assert massCC >= 0.0, 'oops negative value.'
        if self._massCC == 0.0:
            self._massCC = massCC
            self._molarCC = massCC / self._molarMass

        return


# *******************************************************************************

# *******************************************************************************
# Setters and Getters methods
# -------------------------------------------------------------------------------
# These are passing arguments by value effectively. Because the python objects
# passed into/out of the function are immutable.

    def GetName(self):
        return self._name

    def SetName(self, n):
        self._name = n
    name = property(GetName, SetName, None, None)

    def GetFormulaName(self):
        return self._formulaName

    def SetFormulaName(self, f):
        self._formulaName = f
    formulaName = property(GetFormulaName, SetFormulaName, None, None)

    def GetPhase(self):
        return self._phase

    def SetPhase(self, p):
        self._mass = p
    phase = property(GetPhase, SetPhase, None, None)

    def GetMolarMass(self):
        return self._molarMass

    def SetMolarMass(self, v):
        self._molarMass = v
    molarMass = property(GetMolarMass, SetMolarMass, None, None)

    def GetMolarMassUnit(self):
        return self._molarMassUnit

    def SetMolarMassUnit(self, v):
        self._molarMassUnit = v
    molarMassUnit = property(GetMolarMassUnit, SetMolarMassUnit, None, None)

    def GetMolarRadioactivity(self):
        return self._molarRadioactivity

    def SetMolarRadioactivity(self, v):
        self._molarRadioactivity = v
    molarRadioactivity = property(
        GetMolarRadioactivity,
        SetMolarRadioactivity,
        None,
        None)

    def GetMolarRadioactivityFractions(self):
        return self._molarRadioactivityFractions

    def SetMolarRadioactivityFractions(self, fracs):
        assert isinstance(fracs, list), 'oops not list.'
        if len(fracs) > 0:
            assert len(fracs) == len(self._atoms), 'oops not right length,'
        if len(fracs) != 0:
            assert isinstance(fracs[-1], float), 'oops not float.'
        self._molarRadioactivityFractions = fracs
    molarRadioactivityFractions = property(
        GetMolarRadioactivityFractions,
        SetMolarRadioactivityFractions,
        None,
        None)

    def GetMolarRadioactivityUnit(self):
        return self._molarRadioactivityUnit

    def SetMolarRadioactivityUnit(self, v):
        self._molarRadioactivityUnit = v
    molarRadioactivityUnit = property(
        GetMolarRadioactivityUnit,
        SetMolarRadioactivityUnit,
        None,
        None)

    def GetMolarHeatPwr(self):
        return self._molarHeatPwr

    def SetMolarHeatPwr(self, v):
        self._molarHeatPwr = v
    molarHeatPwr = property(GetMolarHeatPwr, SetMolarHeatPwr, None, None)

    def GetMolarHeatPwrUnit(self):
        return self._molarHeatPwrUnit

    def SetMolarHeatPwrUnit(self, v):
        self._molarHeatPwrUnit = v
    molarHeatPwrUnit = property(
        GetMolarHeatPwrUnit,
        SetMolarHeatPwrUnit,
        None,
        None)

    def GetMolarGammaPwr(self):
        return self._molarGammaPwr

    def SetMolarGammaPwr(self, v):
        self._molarGammaPwr = v
    molarGammaPwr = property(GetMolarGammaPwr, SetMolarGammaPwr, None, None)

    def GetMolarGammaPwrUnit(self):
        return self._molarGammaPwrUnit

    def SetMolarGammaPwrUnit(self, v):
        self._molarGammaPwrUnit = v
    molarGammaPwrUnit = property(
        GetMolarGammaPwrUnit,
        SetMolarGammaPwrUnit,
        None,
        None)

    # Deprecated; see new interface below as GetFormula
    def GetAtoms(self):
        return self._atoms

    def SetAtoms(self, atoms):
        assert isinstance(atoms, list), 'oops not list.'
        if len(atoms) != 0:
            assert isinstance(atoms[-1], str), 'oops not string.'
        self._atoms = atoms
        self.__UpdateMolarMass()
    atoms = property(GetAtoms, SetAtoms, None, None)

    # New interface
    def GetFormula(self):
        return self._atoms

    def SetFormula(self, atoms):
        assert isinstance(atoms, list), 'oops not list.'
        if len(atoms) != 0:
            assert isinstance(atoms[-1], str), 'oops not string.'
        self._atoms = atoms
        self.__UpdateMolarMass()
    formula = property(GetFormula, SetFormula, None, None)

    def GetNAtoms(self):  # number of ficticious atoms in the species (see NB above)
        return self._nAtoms
    nAtoms = property(GetNAtoms, None, None, None)

    # number of nuclide types involved in the species definition
    def GetNNuclideTypes(self):
        return self._nNuclideTypes
    nNuclideTypes = property(GetNNuclideTypes, None, None, None)

    def SetFlag(self, f):
        self._flag = f

    def GetFlag(self):
        return self._flag
    flag = property(GetFlag, SetFlag, None, None)

    def GetMolarCC(self):
        return self._molarCC

    def SetMolarCC(self, v):
        self._molarCC = v
        self._massCC = v * self._molarMass
    molarCC = property(GetMolarCC, SetMolarCC, None, None)

    def GetMolarCCUnit(self):
        return self._molarCCUnit

    def SetMolarCCUnit(self, v):
        self._molarCCUnit = v
    molarCCUnit = property(GetMolarCCUnit, SetMolarCCUnit, None, None)

    def GetMassCC(self):
        return self._massCC

    def SetMassCC(self, v):
        self._massCC = v
        if self._molarMass == 0.0 and v == 0.0:
            self._molarCC = 0.0
        else:
            self._molarCC = v / self._molarMass
    massCC = property(GetMassCC, SetMassCC, None, None)

    def GetMassCCUnit(self):
        return self._massCCUnit

    def SetMassCCUnit(self, v):
        self._massCCUnit = v
    massCCUnit = property(GetMassCCUnit, SetMassCCUnit, None, None)

# *******************************************************************************
# Internal helpers

    def __UpdateMolarMass(self):

        if len(self._atoms) == 0:
            return

        for entry in self._atoms:
            assert isinstance(entry, str), 'oops'
            tmp = entry.split('*')
            nuclide = tmp[-1]
            element = nuclide.split('-')[0]
            assert element in ELEMENTS, 'element = %r' % (element)

        self._nAtoms = 0
        self._nNuclideTypes = 0

        nuclides = dict()

        nAtoms = 0
        summ = 0.0
        for entry in self._atoms:
            assert isinstance(entry, str), 'oops'
            # format example:  3.2*O-18, or 3*O or O or O-16
            tmp = entry.split('*')
            multiple = 1.0
            # single nuclide
            if len(tmp) == 1:
                nuclide = tmp[0]
            # multiple nuclide
            elif len(tmp) == 2:
                multiple = float(tmp[0])
                nuclide = tmp[1]
            else:
                assert False

            nuclides[nuclide] = multiple
            nAtoms += multiple

            try:
                tmp = nuclide.split('-')
                if len(tmp) == 1:
                    element = ELEMENTS[tmp[0]]
                    molarMass = element.exactmass  # from isotopic composition
                    if molarMass == 0.0:
                        molarMass = element.mass
                elif len(tmp) == 2:
                    element = ELEMENTS[tmp[0]].isotopes[int(tmp[1].strip('m'))]
                    molarMass = element.mass
                else:
                    assert False
            except KeyError:
                summ += multiple * 0.0
            else:
                summ += multiple * molarMass

        self._molarMass = summ
#   print( summ )
        self._nAtoms = nAtoms
        self._nNuclideTypes = len(nuclides)

        return

    def __ReorderFormula(self):

        atoms1 = self._atoms[:]  # shallow copy
        atoms2 = list()

        if len(self._atoms) <= 1:
            return atoms1

        if len(self._atoms) > 1:

            # save the multiplier value as a string type of scientific notation
            for entry in self._atoms:

                assert isinstance(entry, str), 'oops'

                # format example:  3.2*O-18, or 3*O or O or O-16
                tmp = entry.split('*')

                multiplier = 0.0

                if len(tmp) == 1:
                    continue
                elif len(tmp) == 2:
                    multiplier = float(tmp[0])
                else:
                    assert False

                assert multiplier != 0.0, 'multiplier = %r' % (multiplier)

                multiplier = '{0:9.3e}'.format(multiplier)

                atoms1[self._atoms.index(entry)] = multiplier + '*' + tmp[1]

            # order in decreasing order of multiplier magnitude
            multipliers_lst = list()

            for entry in atoms1:

                tmp = entry.split('*')

                multiplier = 0.0

                if len(tmp) == 1:
                    continue
                elif len(tmp) == 2:
                    multiplier = float(tmp[0])
                else:
                    assert False

                multipliers_lst.append(float(multiplier))

            sortedAtoms_lst = [a for (i, a) in sorted(zip(multipliers_lst, atoms1),
                                                      key=lambda pair: pair[0],
                                                      reverse=True)]

            atoms2 = sortedAtoms_lst

        return atoms2


# *******************************************************************************
# Printing of data members

    def __str__(self):
        s = '\n\t Specie(): name=%s;' + ' formulaName=%s;' + ' phase=%s;' + '\n\t formula=%s;' + '\n\t # atoms=%s;' + ' # nuclide types=%s;' + ' molar mass=%9.3e[%s];' + ' molar cc=%9.3e[%s];' + ' mass cc=%9.3e[%s];' + '\n\t flag=%s;' + '\n\t molar radioactivity=%9.3e[%s];' + \
            '\n\t radioactivity  dens.=%9.3e[%s];' + '\n\t molar heat pwr=%9.3e[%s];' + '\n\t heat pwr dens.=%9.3e[%s];' + \
            '\n\t molar gamma pwr=%9.3e[%s];' + '\n\t gamma pwr dens.=%9.3e[%s];' + \
            '\n\t atoms=%s;' + '\n\t molar radioactivity fractions=%s'
        return s % (self.name, self.formulaName, self.phase, self.__ReorderFormula(), self.nAtoms, self.nNuclideTypes, self.molarMass, self.molarMassUnit, self.molarCC, self.molarCCUnit, self.massCC, self.massCCUnit, self.flag, self.molarRadioactivity, self.molarRadioactivityUnit, self.molarRadioactivity *
                    self.molarCC, '[Ci/cc]', self.molarHeatPwr, self.molarHeatPwrUnit, self.molarHeatPwr * self.molarCC, '[W/cc]', self.molarGammaPwr, self.molarGammaPwrUnit, self.molarGammaPwr * self.molarCC, '[W/cc]', [i.split('*')[-1] for i in self.formula], ['%9.3e' % i for i in self.molarRadioactivityFractions])

    def __repr__(self):
        s = '\n\t Specie(): name=%s;' + ' formulaName=%s;' + ' phase=%s;' + '\n\t formula=%s;' + '\n\t # atoms=%s;' + ' # nuclide types=%s;' + ' molar mass=%9.3e[%s];' + ' molar cc=%9.3e[%s];' + ' mass cc=%9.3e[%s];' + '\n\t flag=%s;' + '\n\t molar radioactivity=%9.3e[%s];' + \
            '\n\t radioactivity  dens.=%9.3e[%s];' + '\n\t molar heat pwr=%9.3e[%s];' + '\n\t heat pwr dens.=%9.3e[%s];' + \
            '\n\t molar gamma pwr=%9.3e[%s];' + '\n\t gamma pwr dens.=%9.3e[%s];' + \
            '\n\t atoms=%s;' + '\n\t molar radioactivity fractions=%s'
        return s % (self.name, self.formulaName, self.phase, self.__ReorderFormula(), self.nAtoms, self.nNuclideTypes, self.molarMass, self.molarMassUnit, self.molarCC, self.molarCCUnit, self.massCC, self.massCCUnit, self.flag, self.molarRadioactivity, self.molarRadioactivityUnit, self.molarRadioactivity *
                    self.molarCC, '[Ci/cc]', self.molarHeatPwr, self.molarHeatPwrUnit, self.molarHeatPwr * self.molarCC, '[W/cc]', self.molarGammaPwr, self.molarGammaPwrUnit, self.molarGammaPwr * self.molarCC, '[W/cc]', [i.split('*')[-1] for i in self.formula], ['%9.3e' % i for i in self.molarRadioactivityFractions])
# *******************************************************************************
