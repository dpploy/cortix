#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/cortix/blob/master/COPYRIGHT.txt
#
# Licensed under the University of Massachusetts Lowell LICENSE:
# https://github.com/dpploy/cortix/blob/master/LICENSE.txt
'''
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

This Specie class is to be used with other classes in plant-level process modules.

NB: Species is always used either in singular or plural cases, the class
    named here reflects one species. If many species are used in an external
    context, the species object name can be used without conflict.

For unit testing do at the linux command prompt:
    python specie.py

NB: The Specie() class encapsulates either the molecular or empirical chemical
    formula of a compound.
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
'''
#*********************************************************************************
import os
import sys

from cortix.support.periodictable import ELEMENTS
#*********************************************************************************

class Specie:
    '''
    todo: phase should not be here; concentrations should not be here
          only molar quantities should be here
          see the Phase container
    '''

#*********************************************************************************
# Construction
#*********************************************************************************

    def __init__(self,
                 name='null',
                 formula_name='null',
                 phase='null',
                 atoms=list(),
                 molarCC=0.0,      # default unit: M (mole/L)
                 massCC=0.0,      # default unit: g/L
                 flag=None):

        assert isinstance(name, str), 'oops not string.'
        self._name = name

        assert isinstance(formula_name, str), 'oops not string.'
        self.__formula_name = formula_name

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

#*********************************************************************************
# Public Member Functions
#*********************************************************************************

    def GetName(self):
        '''
        Returns the empirical name of the species. For example, "water".

        Returns
        -------
        name: str

        '''

        return self._name

    def SetName(self, n):
        '''
        Sets the empirical  name of the species to n.

        Parameters
        ----------
        n: str
        '''

        self._name = n
    name = property(GetName, SetName, None, None)

    def GetFormulaName(self):
        '''
        Returns the formulaic name of the compound. For example, "Dihydrogen
        monoxide".

        Returns
        -------
        self.__formula_name: str
        '''

        return self.__formula_name

    def SetFormulaName(self, f):
        '''
        Sets the formulaic name to f.

        Returns
        -------
        self.__formula_name: str
        '''

        self.__formula_name = f
    formula_name = property(GetFormulaName, SetFormulaName, None, None)

    def GetPhase(self):
        '''
        Returns the phase that the specie is in.

        Returns
        -------
        phase: str
        '''

        return self._phase

    def SetPhase(self, p):
        '''
        Sets the phase history to p.

        Parameters
        ----------
        p: dataFrame
        '''

        self._mass = p
    phase = property(GetPhase, SetPhase, None, None)

    def GetMolarMass(self):
        '''
        Returns the numerical value for the molar mass of the species. Units
        are given by molarMassUnit.

        Returns
        -------
        molarMass: float
        '''

        return self._molarMass

    def SetMolarMass(self, v):
        '''
        Sets the molar mass of the species equal to v.

        Parameters
        ----------
        v: float
        '''

        self._molarMass = v
    molarMass = property(GetMolarMass, SetMolarMass, None, None)

    def GetMolarMassUnit(self):
        '''
        Returns the unit used to measure the molar mass of the species.

        Returns
        -------
        molarMassUnit: str
        '''

        return self._molarMassUnit

    def SetMolarMassUnit(self, v):
        '''
        Sets the unit used to measure the molar mass of the species to v.

        Parameters
        ----------
        v: str
        '''

        self._molarMassUnit = v
    molarMassUnit = property(GetMolarMassUnit, SetMolarMassUnit, None, None)

    def GetMolarRadioactivity(self):
        '''
        Returns the numerical value for molar radioactivity of the species.

        Returns
        -------
        molarRadioactivity: float
        '''

        return self._molarRadioactivity

    def SetMolarRadioactivity(self, v):
        '''
        Sets the molar radioactivity of the species equal to v.

        Parameters
        ----------
        v: float
        '''

        self._molarRadioactivity = v
    molarRadioactivity = property( GetMolarRadioactivity, SetMolarRadioactivity,
            None, None)

    def GetMolarRadioactivityFractions(self):
        '''
        Returns a list of numbers that speciefies the % of molar reactivity
        that comes from each type of atom in the species. For example, a
        molarRadioactivityFraction of [0.65, 0.35] for water means that 65%
        of the molar radioactivity comes from the hydrogen atoms and 35% comes
        from the oxygen atom.

        Returns
        -------
        molarRadioactivityFractions: list
        '''

        return self._molarRadioactivityFractions

    def SetMolarRadioactivityFractions(self, fracs):
        '''
        Sets molarRadioactivityFractions equal to fracs. Fracs must be a list
        of floats with the same length as there are different atoms in the
        species, or the function call will fail. (e.g. self._atoms and fracs
        must be of the same length). Take care to ensure that the elements of
        fracs match with the elements of self._atoms! (65% is in the same
        position in fracs as hydrogen is in self._atoms, following the above
        example).

        Parameters
        ----------
        fracs: list
        '''

        assert isinstance(fracs, list), 'oops not list.'
        if len(fracs) > 0:
            assert len(fracs) == len(self._atoms), 'oops not right length,'
        if len(fracs) != 0:
            assert isinstance(fracs[-1], float), 'oops not float.'
        self._molarRadioactivityFractions = fracs
    molarRadioactivityFractions = property( GetMolarRadioactivityFractions,
            SetMolarRadioactivityFractions, None, None)

    def GetMolarRadioactivityUnit(self):
        '''
        Returns the unit used to measure molar radioactivity.

        Returns
        -------
        molarRadioactivityUnit: str
        '''

        return self._molarRadioactivityUnit

    def SetMolarRadioactivityUnit(self, v):
        '''
        Sets the unit used to measure molar radioactivity to v.

        Parameters
        ----------
        v: str
        '''

        self._molarRadioactivityUnit = v
    molarRadioactivityUnit = property( GetMolarRadioactivityUnit,
            SetMolarRadioactivityUnit, None, None)

    def GetMolarHeatPwr(self):
        '''
        Returns the amount of heat generated per mole of this species.

        Returns
        -------
        molarHeatPwr: float
        '''

        return self._molarHeatPwr

    def SetMolarHeatPwr(self, v):
        '''
        Sets the amount of heat generated per mole of this species to v.

        Parameters
        ----------
        v: float
        '''

        self._molarHeatPwr = v
    molarHeatPwr = property(GetMolarHeatPwr, SetMolarHeatPwr, None, None)

    def GetMolarHeatPwrUnit(self):
        '''
        Returns the unit used to measure the amount of heat generated per mole
        of this species.

        Returns
        -------
        molarHeatPwrUnit: str
        '''

        return self._molarHeatPwrUnit

    def SetMolarHeatPwrUnit(self, v):
        '''
        Sets the unit used to measure the amount of heat generated per mole of
        this species to v.

        Parameters
        ----------
        v: str
        '''

        self._molarHeatPwrUnit = v
    molarHeatPwrUnit = property( GetMolarHeatPwrUnit, SetMolarHeatPwrUnit, None,
            None)

    def GetMolarGammaPwr(self):
        '''
        Returns the amount of gamma radiation produced per mole of this species
        (measured in units of power).

        Returns
        -------
        molarGammaPwr: float
        '''

        return self._molarGammaPwr

    def SetMolarGammaPwr(self, v):
        '''
        Sets the amount of gamma radiation produced per mole of this species to
        v.

        Parameters
        ----------
        v: float
        '''

        self._molarGammaPwr = v
    molarGammaPwr = property(GetMolarGammaPwr, SetMolarGammaPwr, None, None)

    def GetMolarGammaPwrUnit(self):
        '''
        Returns the unit used to measure the amount of gamma radiation produced
        per mole of this species.

        Returns
        -------
        molarGammaPwrUnit: str
        '''

        return self._molarGammaPwrUnit

    def SetMolarGammaPwrUnit(self, v):
        '''
        Sets the unit used to measure the amount of gamma radiation produced
        per mole of this species to v.

        Parameters
        ----------
        v: str
        '''

        self._molarGammaPwrUnit = v
    molarGammaPwrUnit = property( GetMolarGammaPwrUnit, SetMolarGammaPwrUnit, None,
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
        '''
        Returns the molecular or empirical formula of the species. It is
        usually a list, for example, of the form ['2*H', 'O'].

        Returns
        -------
        formula: list
        '''

        return self._atoms

    def SetFormula(self, atoms):
        '''
        Sets the species' formula equal to atoms. Will automatically update
        the molar mass of the species, and will also fail if atoms is not a
        list of strings.

        Parameters
        ----------
        atoms: list
        '''

        assert isinstance(atoms, list), 'oops not list.'
        if len(atoms) != 0:
            assert isinstance(atoms[-1], str), 'oops not string.'
        self._atoms = atoms
        self.__UpdateMolarMass()
    formula = property(GetFormula, SetFormula, None, None)

    def GetNAtoms(self):  # number of ficticious atoms in the species (see NB above)
        '''
        Returns the total number of atoms comprising the species. For example,
        water is comprised of three atoms.

        Returns
        -------
        nAtoms: int
        '''

        return self._nAtoms
    nAtoms = property(GetNAtoms, None, None, None)

    # number of nuclide types involved in the species definition
    def GetNNuclideTypes(self):
        '''
        Returns the number of different types of atoms comprising the species.
        For example, water is composed of two different types of atoms,
        hydrogen and oxygen.

        Returns
        -------
        nNuclideTypes: int
        '''

        return self._nNuclideTypes
    nNuclideTypes = property(GetNNuclideTypes, None, None, None)

    def SetFlag(self, f):
        '''
        Sets the flag associated with the species to f.

        Parameters
        ----------
        f: str
        '''

        self._flag = f

    def GetFlag(self):
        '''
        Returns the flag associated with the species.

        Returns
        -------
        flag: str
        '''

        return self._flag
    flag = property(GetFlag, SetFlag, None, None)

    def GetMolarCC(self):
        '''
        Returns the numerical value for the number (molar) density of the
        species (moles/volume).

        Returns
        -------
        molarCC: float
        '''

        return self._molarCC

    def SetMolarCC(self, v):
        '''
        Sets the numerical value for the molar density of the species to v.

        Parameters
        ----------
        v: float
        '''

        self._molarCC = v
        self._massCC = v * self._molarMass
    molarCC = property(GetMolarCC, SetMolarCC, None, None)

    def GetMolarCCUnit(self):
        '''
        Returns the unit used to measure molar density of the species.

        Returns
        -------
        molarCCUnit: str
        '''

        return self._molarCCUnit

    def SetMolarCCUnit(self, v):
        '''
        Sets the unit used to measure the molar density of the species to v.

        Parameters
        ----------
        v: str
        '''

        self._molarCCUnit = v
    molarCCUnit = property(GetMolarCCUnit, SetMolarCCUnit, None, None)

    def GetMassCC(self):
        '''
        Returns the numerical value of the mass density of the species
        (mass/volume).

        Returns
        -------
        massCC: float
        '''

        return self._massCC

    def SetMassCC(self, v):
        '''
        Sets the numerical value of the mass density equal to v.

        Parameters
        ----------
        v: float
        '''

        self._massCC = v
        if self._molarMass == 0.0 and v == 0.0:
            self._molarCC = 0.0
        else:
            self._molarCC = v / self._molarMass
    massCC = property(GetMassCC, SetMassCC, None, None)

    def GetMassCCUnit(self):
        '''
        Returns the unit used to measure the mass density of the species.

        Returns
        -------
        massCCUnit: str
        '''

        return self._massCCUnit

    def SetMassCCUnit(self, v):
        '''
        Sets the units used to measure mass density to v.

        Parameters
        ----------
        v: str
        '''

        self._massCCUnit = v
    massCCUnit = property(GetMassCCUnit, SetMassCCUnit, None, None)

    def __str__(self):
        s = '\n\t Specie(): name=%s;' + ' formula_name=%s;' + ' phase=%s;' + '\n\t formula=%s;' + '\n\t # atoms=%s;' + ' # nuclide types=%s;' + ' molar mass=%9.3e[%s];' + ' molar cc=%9.3e[%s];' + ' mass cc=%9.3e[%s];' + '\n\t flag=%s;' + '\n\t molar radioactivity=%9.3e[%s];' + \
            '\n\t radioactivity  dens.=%9.3e[%s];' + '\n\t molar heat pwr=%9.3e[%s];' + '\n\t heat pwr dens.=%9.3e[%s];' + \
            '\n\t molar gamma pwr=%9.3e[%s];' + '\n\t gamma pwr dens.=%9.3e[%s];' + \
            '\n\t atoms=%s;' + '\n\t molar radioactivity fractions=%s'
        return s % (self.name, self.__formula_name, self.phase, self.__ReorderFormula(), self.nAtoms, self.nNuclideTypes, self.molarMass, self.molarMassUnit, self.molarCC, self.molarCCUnit, self.massCC, self.massCCUnit, self.flag, self.molarRadioactivity, self.molarRadioactivityUnit, self.molarRadioactivity *
                    self.molarCC, '[Ci/cc]', self.molarHeatPwr, self.molarHeatPwrUnit, self.molarHeatPwr * self.molarCC, '[W/cc]', self.molarGammaPwr, self.molarGammaPwrUnit, self.molarGammaPwr * self.molarCC, '[W/cc]', [i.split('*')[-1] for i in self.formula], ['%9.3e' % i for i in self.molarRadioactivityFractions])

    def __repr__(self):
        s = '\n\t Specie(): name=%s;' + ' formula_name=%s;' + ' phase=%s;' + '\n\t formula=%s;' + '\n\t # atoms=%s;' + ' # nuclide types=%s;' + ' molar mass=%9.3e[%s];' + ' molar cc=%9.3e[%s];' + ' mass cc=%9.3e[%s];' + '\n\t flag=%s;' + '\n\t molar radioactivity=%9.3e[%s];' + \
            '\n\t radioactivity  dens.=%9.3e[%s];' + '\n\t molar heat pwr=%9.3e[%s];' + '\n\t heat pwr dens.=%9.3e[%s];' + \
            '\n\t molar gamma pwr=%9.3e[%s];' + '\n\t gamma pwr dens.=%9.3e[%s];' + \
            '\n\t atoms=%s;' + '\n\t molar radioactivity fractions=%s'
        return s % (self.name, self.__formula_name, self.phase, self.__ReorderFormula(), self.nAtoms, self.nNuclideTypes, self.molarMass, self.molarMassUnit, self.molarCC, self.molarCCUnit, self.massCC, self.massCCUnit, self.flag, self.molarRadioactivity, self.molarRadioactivityUnit, self.molarRadioactivity *
                    self.molarCC, '[Ci/cc]', self.molarHeatPwr, self.molarHeatPwrUnit, self.molarHeatPwr * self.molarCC, '[W/cc]', self.molarGammaPwr, self.molarGammaPwrUnit, self.molarGammaPwr * self.molarCC, '[W/cc]', [i.split('*')[-1] for i in self.formula], ['%9.3e' % i for i in self.molarRadioactivityFractions])

#*********************************************************************************
# Private Helper Functions (Internal use: __)
#*********************************************************************************

    def __UpdateMolarMass(self):
        '''
        Updates the molar mass of the species after the molecular formula has
        been changed.
        '''

        #if len(self._atoms) == 0:
        #    self._nAtoms = 0
        #    return

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
        '''
        Takes a list of atoms for a molecular or empirical formula and places
        it in order of decreasing magnitude of stoichiometric coefficient. For
        example, [O, 2*H] will be returned as [2*H, O].

        Returns
        -------
        atoms2: list
        '''

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

#============================= end class Specie ==================================
