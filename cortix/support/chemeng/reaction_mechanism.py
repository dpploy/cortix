#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
'''
Suupport class for working with chemical reactions.
'''

import numpy as np

from cortix.support.species import Species

class ReactionMechanism:
    """Chemical reaction mechanism.

    Attributes
    ----------

    xxxx: int
        Some attribute

    """

    def __init__(self, header='no-header', file_name=None, mechanism=None, order_species=True):
        """Module class constructor.

        Returns data structures for a reaction mechanism. Namely, species list,
        reactions list, equilibrium constant list, and stoichiometric matrix.

        Reaction mechanism format is as follows:

        # comment
        # comment
        4 NH3 + 5 O2        <=> 4 NO  + 6 H2O   :   quantity1 = 2.5e+02 : quantity2 = '2+2'

        Any amount of spacing is allowed except:
        a) there must be only one blank space between the stoichiometric coefficient and its
           species name.
        b) there must be at least one blank space before and after each + sign in the reaction.
        c) species formula name as described in Cortix Species() e.g.:
            charge preceded with ^: O2^2+, X^1-, X^+, X^-
            phase in parenthesis (): O2^2+(a), O2^2+(aq), O2^2+(aqu)

        There must be no blank lines. A stoichiometric coefficient equal to 1 can be ommited.

        Parameters
        ----------
        file_name: str, optional
              Full path file name of the reaction mechanism file. If the reaction has an
              equilibrium constant it will follow the reaction separated by a colon.
        reactions: list(str), optional
              list of reaction strings.

        Examples
        --------

        Attributes
        ----------
        (reactions, data, species, stoic_mtrx): list(str), list(str), nump.ndarray, lst(type), list(type) )
          a: type 
              A ...

       """

        assert file_name is not None or mechanism is not None
        assert isinstance(header, str)
        self.header = header


        if mechanism is not None:
            assert isinstance(mechanism, list)
            assert file_name is None

        if file_name is not None:
            assert isinstance(file_name, str)
            assert mechanism is None

            finput = open(file_name,'rt')

            mechanism = list()

            for line in finput:
                stripped_line = line.strip()
                mechanism.append(stripped_line)

            finput.close()

        self.reactions = list()
        self.data = list()

        for m_i in mechanism:

            if m_i[0].strip() == '#':
                if self.header == 'no-header':
                    self.header = m_i.strip() + '\n'
                else:
                    self.header += m_i.strip() + '\n'
                continue

            data = m_i.split(':')

            self.reactions.append(data[0].strip())

            tmp_dict = dict()

            if len(data) > 1:

                for d in data[1:]:
                    datum = d.strip()

                    name = datum.split('=')[0].strip()
                    val_str = datum.split('=')[1].strip()

                    if name == 'alpha':
                        assert '(' in val_str and ')' in val_str
                        alpha = tuple(val_str)
                        alpha_dict = dict()
                        i = 0
                        for s in alpha:
                            if s.isnumeric():
                                alpha_dict[i] = float(s)
                                i += 1
                        tmp_dict[name] = alpha_dict
                    else:
                        tmp_dict[name] = float(val_str)

            self.data.append(tmp_dict)

        # find species

        species_tmp = list()  # temporary list for species

        for r in self.reactions:

            # the order of the following test matters; test reversible reaction first
            tmp = r.split('<=>')
            n_terms = len(tmp)
            assert n_terms == 1 or n_terms == 2

            if n_terms == 1: # if no previous split
                tmp = r.split('<->')
                n_terms = len(tmp)
                assert n_terms == 1 or n_terms == 2
                if n_terms == 1: # if no previous split
                    tmp = r.split('->')
                    n_terms = len(tmp)
                    assert n_terms == 1 or n_terms == 2
                    if n_terms == 1: # if no previous split
                        tmp = r.split('<-')
                        n_terms = len(tmp)
                        assert n_terms == 1 or n_terms == 2

            assert n_terms == 2 # must have two terms

            left  = tmp[0].strip()
            right = tmp[1].strip()

            left_terms  = left.split(' + ')
            right_terms = right.split(' + ')

            terms = [t.strip() for t in left_terms] + [t.strip() for t in right_terms]

            for i in terms:
                tmp = i.split(' ')
                assert len(tmp)==1 or len(tmp)==2,' tmp = %r '%tmp
                if len(tmp) == 2:
                    species_tmp.append( tmp[1].strip() )
                else:
                    species_tmp.append( i.strip() )

        species_filter = set(species_tmp) # filter species as a set

        self.species_names = list(species_filter)  # convert species set to list

        if order_species:
            self.species_names = sorted(self.species_names)

        # Create the species list
        self.species = list()

        for name in self.species_names:
            spc = Species(name=name, formula_name=name)
            self.species.append(spc)

        # Build the stoichiometric matrix

        s_mtrx = np.zeros((len(self.reactions),len(self.species)), dtype=np.float64)

        for r in self.reactions:

            i_row = self.reactions.index(r)

            tmp = r.split(' -> ')
            n_terms = len(tmp)
            assert n_terms == 1 or n_terms == 2
            if n_terms == 1:
                tmp = r.split(' <-> ')
                n_terms = len(tmp)
                assert n_terms == 1 or n_terms == 2
                if n_terms == 1:
                    tmp = r.split(' <=> ')
                    n_terms = len(tmp)
                    assert n_terms == 1 or n_terms == 2
                    if n_terms == 1:
                        tmp = r.split(' <- ')
                        n_terms = len(tmp)
                        assert n_terms == 1 or n_terms == 2

            assert n_terms == 2

            left = tmp[0]
            left_terms = left.split(' + ')
            left_terms = [t.strip() for t in left_terms]

            right = tmp[1]
            right_terms = right.split(' + ')
            right_terms = [t.strip() for t in right_terms]

            for t in left_terms:
                tmp = t.split(' ')
                if len(tmp) == 2:
                    coeff = float(tmp[0].strip())
                    species_member = tmp[1].strip()
                    j_col = self.species_names.index(species_member)
                    assert s_mtrx[i_row,j_col] == 0.0, \
                           'duplicates not allowed r%r: %r %r %r'%\
                           (i_row,r,species_member,s_mtrx[i_row,j_col])
                    s_mtrx[i_row,j_col] = -1.0 * coeff
                else:
                    species_member = tmp[0].strip()
                    j_col = self.species_names.index(species_member)
                    assert s_mtrx[i_row,j_col] == 0.0, \
                           'duplicates not allowed r%r: %r %r %r'%\
                           (i_row,r,species_member,s_mtrx[i_row,j_col])
                    s_mtrx[i_row,j_col] = -1.0

                if 'alpha' in self.data[i_row].keys():
                    species_name = self.species_names[j_col]
                    self.data[i_row]['alpha'][species_name] = self.data[i_row]['alpha'].pop(left_terms.index(t))

            for t in right_terms:
                tmp = t.split(' ')
                if len(tmp) == 2:
                    coeff = float(tmp[0].strip())
                    species_member = tmp[1].strip()
                    j_col = self.species_names.index(species_member)
                    assert s_mtrx[i_row,j_col] == 0.0, \
                           'duplicates not allowed r%r: %r %r %r'%\
                           (i_row,r,species_member,s_mtrx[i_row,j_col])
                    s_mtrx[i_row,j_col] = 1.0 * coeff
                else:
                    species_member = tmp[0].strip()
                    j_col = self.species_names.index(species_member)
                    assert s_mtrx[i_row,j_col] == 0.0, \
                           'duplicates not allowed r%r: %r %r %r'%\
                           (i_row,r,species_member,s_mtrx[i_row,j_col])
                    s_mtrx[i_row,j_col] = 1.0

        self.stoic_mtrx = s_mtrx

    def max_mass_balance_residual(self):
        """Compute the maximum reaction mass balance residual.
        """

        m_vec = np.zeros(len(self.species), dtype=np.float64)

        for idx, spc in enumerate(self.species):
            m_vec[idx] = spc.molar_mass

        assert np.prod(m_vec) > 0.0

        mass_residual = self.stoic_mtrx @ m_vec

        #print('mass res=', mass_residual)
        #print('np.max(np.abs(mass_residual)=', np.max(np.abs(mass_residual)))

        return np.max(np.abs(mass_residual))

    def is_mass_conserved(self, tol=1e-10):
        """Check mass conservation if species have a molar mass value.
        """

        residual = self.max_mass_balance_residual()

        return True if residual < tol else False

    def rank_analysis(self, tol=1e-8):
        """Compute the rank of the stoichiometric matrix.

        This will establish rank deficiency.
        """

        assert self.is_mass_conserved(tol), 'fatal: mass conservation failed'

        s_rank = np.linalg.matrix_rank(self.stoic_mtrx, tol=1e-8)
        assert s_rank <= min(self.stoic_mtrx.shape)
        print('*********************')
        print('# reactions = ', len(self.reactions))
        print('# species   = ', len(self.species))
        print('rank of S = ', s_rank)
        if s_rank == min(self.stoic_mtrx.shape):
            print('S is full rank.')
        else:
            print('S is rank deficient.')
        print('*********************')

    def __str__(self):
        s = '\n\t **ReactionMechanism()**:' + \
            '\n\t header: %s;' + \
            '\n\t reactions: %s;' + \
            '\n\t data: %s;' + \
            '\n\t species_names: %s;' + \
            '\n\t species: %s'
        return s % (self.header,
                    self.reactions,
                    self.data,
                    self.species_names,
                    self.species)

    def __repr__(self):
        s = '\n\t **ReactionMechanism()**:' + \
            '\n\t header: %s;' + \
            '\n\t reactions: %s;' + \
            '\n\t data: %s;' + \
            '\n\t species_names: %s;' + \
            '\n\t species: %s;'
        return s % (self.header,
                    self.reactions,
                    self.data,
                    self.species_names,
                    self.species)