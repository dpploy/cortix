#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import scipy.constants as const
from cortix.support.periodictable import ELEMENTS

class Species:
    '''
    All SI units (kg,s,K,Pa,J,W).

    The Specie() class encapsulates either the molecular or empirical chemical
    formula of a compound.
    This is done as follows. Say MAO2 is either a molecular or empirical chemical
    formula of a ficticious compound denoting minor actinides dioxide. The list
    of atoms is given as follows:

    ['0.49*Np-237', '0.42*Am-241', '0.08*Am-243', '0.01*Cm-244', '2.0*O-16']

    note the MA forming nuclides add to 1 = 0.49 + 0.42 + 0.08 + 0.01. Therefore
    the number of atoms in this compound is 3. 1 MA "ficticious" atom and 2 O.
    Note that the total number of "atoms" is obtained by summing all multipliers:
    0.49 + 0.42 + 0.08 + 0.01 + 2.0.
    The nuclide is indicated by the element symbol followed by a dash and the
    atomic mass number. Here the number of nuclide types is 5 (self.num_nuclide_types).

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
    '''

    def __init__( self,
                  name='null-species-name',
                  formula_name='null-species-formula-name',
                  atoms=list(),
                  flag='null-species-flag',
                  info=None):

        assert isinstance(name, str)
        self.name = name

        assert isinstance(formula_name, str)
        self.formula_name = formula_name

        assert isinstance(atoms, list)
        self.atoms = atoms

        self.flag = flag  # flag can be any type

        self.info = info # info text such as technical name or other properties info

        self.molar_mass = 0.0      # kg/mol
        self.molar_heat_pwr = 0.0
        self.molar_gamma_pwr = 0.0
        self.molar_radioactivity = 0.0

        self.molar_mass_unit = 'kg/mol'

        self.molar_heat_pwr_unit = 'W/mol'
        self.molar_gamma_pwr_unit = 'W/mol'
        self.molar_radioactivity_unit = 'Ci/mol'

        self.molar_radioactivity_fractions = list()

        self.update_molar_mass()

        return

    def update_molar_mass(self):
        '''
        Updates the molar mass of the species after the molecular formula has
        been changed.

        '''

        molar_mass_const = const.physical_constants['molar mass constant'][0]
        molar_mass_const_unit = const.physical_constants['molar mass constant'][1]

        for entry in self.atoms:
            assert isinstance(entry, str)
            tmp = entry.split('*')
            nuclide = tmp[-1]
            element = nuclide.split('-')[0]
            assert element in ELEMENTS, 'element = %r'%(element)

        self.num_atoms = 0
        self.num_nuclide_types = 0

        nuclides = dict()

        num_atoms = 0
        summ = 0.0
        for entry in self.atoms:
            assert isinstance(entry, str)
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
            num_atoms += multiple

            try:
                tmp = nuclide.split('-')
                if len(tmp) == 1:
                    element = ELEMENTS[tmp[0]]
                    rel_atomic_mass = element.exactmass  # from isotopic composition
                    if rel_atomic_mass == 0.0:
                        rel_atomic_mass = element.mass
                    molar_mass = rel_atomic_mass * molar_mass_const
                elif len(tmp) == 2:
                    element = ELEMENTS[tmp[0]].isotopes[int(tmp[1].strip('m'))]
                    molar_mass = element.mass * molar_mass_const
                else:
                    assert False
            except KeyError:
                summ += multiple * 0.0
            else:
                summ += multiple * molar_mass

        self.molar_mass = summ

        self.num_atoms = num_atoms
        self.num_nuclide_types = len(nuclides)

        return

    def reorder_formula(self):
        '''
        Takes a list of atoms for a molecular or empirical formula and places
        it in order of decreasing magnitude of stoichiometric coefficient. For
        example, [O, 2*H] will be returned as [2*H, O]. This is used for
        printing purposes. The internal order will not change.

        Returns
        -------
        atoms2: list

        '''

        atoms1 = self.atoms[:]  # shallow copy
        atoms2 = list()

        if len(self.atoms) <= 1:
            return atoms1

        if len(self.atoms) > 1:

            # save the multiplier value as a string type of scientific notation
            for entry in self.atoms:

                assert isinstance(entry, str)

                # format example:  3.2*O-18, or 3*O or O or O-16
                tmp = entry.split('*')

                nuclide = tmp[-1]

                multiplier = 0.0

                if len(tmp) == 1:
                    multiplier = 1
                elif len(tmp) == 2:
                    multiplier = float(tmp[0])
                else:
                    assert False

                assert multiplier != 0.0, 'multiplier = %r' % (multiplier)

                multiplier = '{0:9.3e}'.format(multiplier)

                atoms1[self.atoms.index(entry)] = multiplier + '*' + nuclide

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

            sorted_atoms = [a for (i, a) in sorted(zip(multipliers_lst, atoms1),
                key=lambda pair: pair[0], reverse=True)]

            atoms2 = sorted_atoms

        return atoms2

    def __str__(self):
        s = '\n\t ' + \
            '\n\t Species(): name=%s;' + \
            ' formula_name=%s;' + \
            '\n\t formula=%s;' + \
            '\n\t # atoms=%s;' + ' # nuclide types=%s;' + ' molar mass=%9.3e[%s];' + \
            '\n\t flag=%s;' + \
            '\n\t info=%s;' + \
            '\n\t molar radioactivity=%9.3e[%s];' + \
            '\n\t molar heat pwr=%9.3e[%s];' + \
            '\n\t molar gamma pwr=%9.3e[%s];' + \
            '\n\t atoms=%s;' + \
            '\n\t molar radioactivity fractions=%s'
        return s % (self.name,
                self.formula_name,
                self.reorder_formula(),
                self.num_atoms, self.num_nuclide_types, self.molar_mass, \
                        self.molar_mass_unit,
                self.flag,
                self.info,
                self.molar_radioactivity, self.molar_radioactivity_unit,
                self.molar_heat_pwr, self.molar_heat_pwr_unit,
                self.molar_gamma_pwr, self.molar_gamma_pwr_unit,
                [i.split('*')[-1] for i in self.atoms],
                ['%9.3e' % i for i in self.molar_radioactivity_fractions])

    def __repr__(self):
        s = '\n\t Species(): name=%s;' + \
            ' formula_name=%s;' + \
            '\n\t formula=%s;' + \
            '\n\t # atoms=%s;' + ' # nuclide types=%s;' + ' molar mass=%9.3e[%s];' + \
            '\n\t flag=%s;' + \
            '\n\t molar radioactivity=%9.3e[%s];' + \
            '\n\t molar heat pwr=%9.3e[%s];' + \
            '\n\t molar gamma pwr=%9.3e[%s];' + \
            '\n\t atoms=%s;' + \
            '\n\t molar radioactivity fractions=%s'
        return s % (self.name,
                self.formula_name,
                self.reorder_formula(),
                self.num_atoms, self.num_nuclide_types, self.molar_mass, \
                        self.molar_mass_unit,
                self.flag,
                self.molar_radioactivity, self.molar_radioactivity_unit,
                self.molar_heat_pwr, self.molar_heat_pwr_unit,
                self.molar_gamma_pwr, self.molar_gamma_pwr_unit,
                [i.split('*')[-1] for i in self.atoms],
                ['%9.3e' % i for i in self.molar_radioactivity_fractions])

if __name__ == '__main__':
    tbp_org = Species( name='TBP', formula_name='(C4H9O)_3PO(o)',
              atoms=['12*C','27*H','4*O','P'] )
    print(tbp_org)
    no3Minus_aqu = Species( name='NO3-', formula_name='NO3-(a)',
                   atoms=['N','3*O'] )
    print(no3Minus_aqu)
