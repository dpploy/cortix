#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
'''
Species class from Cortix support.
'''

import scipy.constants as const
from cortix.support.periodictable import ELEMENTS

class Species:
    """
    All SI units (kg,s,K,Pa,J,W).

    Notes
    -----
    The Species() class encapsulates either the molecular or empirical chemical formula of
    a compound. This is done as follows.

    Say `MAO2` is either a molecular or empirical chemical formula of a ficticious compound
    denoting minor actinides dioxide. The list of atoms is given as follows:

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
    case a hyphen may appear twice, e.g.: 1.549e-09*U-233

    Other forms can be used for common true species

    ['Np-237', '2.0*O-16'] or ['Np-237', 'O-16', 'O-16'] or [ '2*H', 'O' ] or
    [ 'H', 'O', 'H' ]  etc...

    This code will calculate the molar mass of any species with a given valid
    atom list using a provided periodic table of chemical elements. The user
    can also reset the value of the molar mass with a setter method.

    Attributes
    ----------

    """

    def __init__( self,
                  name='no-species-name',
                  formula_name='no-species-formula-name',
                  atoms=None,
                  charge=None,
                  flag='no-species-flag',
                  info=None,
                  latex_name='no-species-latex-name'):
        """Constructs a Species object.

        Parameters
        ----------
        name: str
            The name or "nick-name" of the species; often a short-hand name for the species,
            e.g. ndd for C12H26. The empirical formula name may be too long for typesetting into
            code, the name is usually a shorter variable name.

        formula_name: str
            The empirical formula name. See __atoms_from_formula_name() method for valid strings
            that allow for automatic build up of the list of atoms.

        atoms: list(str)
            List of atoms as described above in the class notes.

        flag: anytype
            Any data type specified by user. This can be used as an identification of the
            species when solving for concentration, or other designation of status.

        info: str
            A textual information about the species, e.g. the commercial name of the compound.

        latex_name: str
            A LaTeX string type varible typically generated automatically by this constructor.

        Examples
        --------

        """

        assert isinstance(name, str)
        self.name = name

        assert isinstance(formula_name, str)
        self.formula_name = formula_name

        if atoms is not None:
            assert isinstance(atoms, list)
            self.atoms = atoms
        else:
            self.atoms = list()

        if charge is not None:
            assert isinstance(charge, int)
            self.charge = charge
        else:
            self.charge = 0 # defaults to neutral species

        self.flag = flag  # flag can be any type

        self.info = info # info text such as technical name or other properties info

        assert isinstance(latex_name, str)
        self.latex_name = latex_name

        self.molar_mass = 0.0      # kg/mol
        self.molar_heat_pwr = 0.0
        self.molar_gamma_pwr = 0.0
        self.molar_radioactivity = 0.0

        self.molar_mass_unit = 'kg/mol'

        self.molar_heat_pwr_unit = 'W/mol'
        self.molar_gamma_pwr_unit = 'W/mol'
        self.molar_radioactivity_unit = 'Ci/mol'

        self.molar_radioactivity_fractions = list()

        if self.latex_name == 'no-species-latex-name' and self.formula_name != 'no-species-formula-name':
            self.__latex_name_from_formula_name()

        if len(self.atoms) == 0 and self.formula_name != 'no-species-formula-name':
            self.__atoms_from_formula_name()

        self.update_molar_mass()

    def update_molar_mass(self):
        """Recalculates the molar mass of the species and updates the species attribute.

        The typical use is to update the molar mass of the species after the list of atoms
        has been changed.

        """

        molar_mass_const = const.physical_constants['molar mass constant'][0]
        #molar_mass_const_unit = const.physical_constants['molar mass constant'][1]

        for entry in self.atoms:
            assert isinstance(entry, str)
            tmp = entry.split('*')
            nuclide = tmp[-1]
            element = nuclide.split('-')[0]
            if not element in ELEMENTS:
                print('Warning: not a chemical element %s'%element)
            #assert element in ELEMENTS, 'element = %r'%(element)

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

        # Add charge
        if self.charge > 0:
            self.molar_mass -= self.charge * const.physical_constants['electron molar mass'][0]
        else:
            self.molar_mass += -1 * self.charge * const.physical_constants['electron molar mass'][0]

        # Exception: e^- (solvated electron)
        if self.formula_name == 'e^-':
            self.molar_mass = const.physical_constants['electron molar mass'][0]

    def ordered_atoms_list(self):
        """Sorted list of the atoms in the species; mostly for printing purposes.

        This method uses the internal list of atoms for a molecular or empirical formula and
        places it in order of decreasing magnitude of stoichiometric coefficient. For
        example, [O, 2*H] will be returned as [2*H, O]. This is used for
        printing purposes. The internal order will not change.

        Returns
        -------
        atoms2: list

        """

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

    def __atoms_from_formula_name(self):
        """Try to build the atoms list from the empirical formula.

        Examples that can be handled by the code below:

            *OH^-:              * for radical, ^ for charged species
            [CH2]3OH*^2-(a):    [] for groups of atoms
            H2O2(v):            () for phase

        This is useful for automating the creation of a species list of atoms, say from a
        reaction mechanism.

        """

        formula_name = self.formula_name.strip()

        # remove radical symbol *
        formula_name = formula_name.strip('*')
        tmp = formula_name.split('*')
        if len(tmp) > 1:
            assert len(tmp) == 2, 'fatal: only one "*" allowed.'
            formula_name = tmp[0]+tmp[1]

        # remove phase indicator
        i = formula_name.find('(')
        j = formula_name.rfind(')')
        if i != -1 and j != -1:
            formula_name = formula_name.replace(formula_name[i:j+1], '')
        elif (i == -1 and j != -1) or (i != -1 and j == -1):
            assert False, 'fatal: missing pairing ")".'

        # remove charge
        i = formula_name.find('^')
        if i != -1: # if success
            if formula_name[i+1].isnumeric():    # integer followed by sign
                charge = formula_name[i+1:i+3]
                formula_name = formula_name.replace(formula_name[i:i+3], '')
            else: # just a sign
                charge = formula_name[i+1:i+2]
                formula_name = formula_name.replace(formula_name[i:i+2], '')

            sign = charge[-1]

            if len(charge) == 2:
                val = int(charge[0])
            elif len(charge) == 1:
                val = 1
            else:
                assert False, 'fatal: invalid charge = %r'%charge

            if sign == '-':
                self.charge = -1 * val
            else:
                self.charge = val

        # find atom group multiplicity
        i = formula_name.find('[')
        if i != -1: # if success
            assert False, 'fatal: "[]" not yet implemented.' # TODO

        # build the atom list
        assert isinstance(self.atoms, list)
        assert len(self.atoms) == 0

        assert formula_name.isalnum(), 'fatal: formula name = %r'%formula_name

        # Find the chemical element symbol in the general form: Xy, say He, Na, O, etc.
        upper_case_ids = list()
        lower_case_ids = list()
        number_of_atoms_ids = list()

        for id,s in enumerate(formula_name):
            if s.isupper():
                upper_case_ids.append(id)
            if s.islower():
                lower_case_ids.append(id)
            if s.isnumeric():
                number_of_atoms_ids.append(id)

        for i in upper_case_ids:
            num_atoms = 1
            symbol = formula_name[i]
            if i+1 in number_of_atoms_ids:
                num_atoms = formula_name[i+1]
            if i+1 in lower_case_ids:
                symbol += formula_name[i+1]
                if i+2 in number_of_atoms_ids:
                    num_atoms = formula_name[i+2]

            if num_atoms == 1:
                self.atoms.append(symbol)
            else:
                self.atoms.append(num_atoms+'*'+symbol)

    def __latex_name_from_formula_name(self):
        """Try to build a LaTeX name from the empirical formula.

        Examples that can be handled by the code below:

            *OH^-:              * for radical, ^ for charged species
            [CH2]3OH*^2-(a):    [] for groups of atoms
            H2O2(v):            () for phase

        This is useful for automating the creation of a species list of atoms, say from a
        reaction mechanism.

        """

        latex_name = str()

        formula_name = self.formula_name.strip()

        open_parenthesis = False

        for idx, c_i in enumerate(formula_name):

            if c_i == '(':
                open_parenthesis = True
                latex_name += r'$_\mathrm{(' # escape \
                continue
            elif c_i == ')':
                open_parenthesis = False
                latex_name += ')}$'
                continue

            if not open_parenthesis:

                if c_i == '*':
                    latex_name += r'$^\bullet$' # escape \
                    continue

                if c_i == '^':
                    if formula_name[idx+1].isnumeric():
                        latex_name += '$^{' + formula_name[idx+1:idx+3] + '}$'
                    else:
                        latex_name += '$^' + formula_name[idx+1] + '$'
                    continue

                if c_i.isalpha():
                    latex_name += c_i

                if c_i.isnumeric() and formula_name[idx-1].isalpha():
                    latex_name += '$_' + c_i + '$'
                    continue

                if c_i == '[' or c_i == ']':
                    assert False, 'fatal: "[]" not implemented yet.' #TODO

            else:
                latex_name += c_i


        self.latex_name = latex_name

    def __str__(self):
        s = '\n\t ' + \
            '\n\t Species(): name=%s;' + \
            ' formula_name=%s;' + \
            '\n\t formula=%s;' + \
            '\n\t # atoms=%s;' + ' # nuclide types=%s;' + ' molar mass=%9.3e[%s];' + \
            '\n\t charge=%s;' + \
            '\n\t flag=%s;' + \
            '\n\t info=%s;' + \
            '\n\t latex_name=%s;' + \
            '\n\t molar radioactivity=%9.3e[%s];' + \
            '\n\t molar heat pwr=%9.3e[%s];' + \
            '\n\t molar gamma pwr=%9.3e[%s];' + \
            '\n\t individual atoms=%s;' + \
            '\n\t molar radioactivity fractions=%s'
        return s % (self.name,
                self.formula_name,
                self.ordered_atoms_list(),
                self.num_atoms, self.num_nuclide_types, self.molar_mass, \
                        self.molar_mass_unit,
                self.charge,
                self.flag,
                self.info,
                self.latex_name,
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
            '\n\t charge=%s;' + \
            '\n\t flag=%s;' + \
            '\n\t latex_name=%s;' + \
            '\n\t molar radioactivity=%9.3e[%s];' + \
            '\n\t molar heat pwr=%9.3e[%s];' + \
            '\n\t molar gamma pwr=%9.3e[%s];' + \
            '\n\t individual atoms=%s;' + \
            '\n\t molar radioactivity fractions=%s'
        return s % (self.name,
                self.formula_name,
                self.ordered_atoms_list(),
                self.num_atoms, self.num_nuclide_types, self.molar_mass, \
                        self.molar_mass_unit,
                self.charge,
                self.flag,
                self.latex_name,
                self.molar_radioactivity, self.molar_radioactivity_unit,
                self.molar_heat_pwr, self.molar_heat_pwr_unit,
                self.molar_gamma_pwr, self.molar_gamma_pwr_unit,
                [i.split('*')[-1] for i in self.atoms],
                ['%9.3e' % i for i in self.molar_radioactivity_fractions])

if __name__ == '__main__':
    tbp_org = Species( name='TBP', formula_name='[C4H9O]_3PO(o)',
              atoms=['12*C','27*H','4*O','P'] )
    print(tbp_org)
    no3Minus_aqu = Species( name='NO3-', formula_name='NO3^-(a)',
                   atoms=['N','3*O'] )
    print(no3Minus_aqu)
