 #!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
'''
Suupport class for working with chemical reactions.
'''
import copy
import math
import numpy       # used in asserts
import numpy as np
from itertools import combinations
import random

from cortix.support.species import Species


class ReactionMechanism:
    '''Chemical reaction mechanism.
    Quantites and services: stoichiometric matrix, mass conservation, reaction rate density vector,
    species production rate density vector.

    Attributes
    ----------

    header: str
        Concatenated string of comments preceded by # in the reaction header.

    reactions: list(str)
        List of strings for each reaction.

    species_names: list(str)
        List of species names.

    species: list(Species)
        List of Species corresponding to the `species_names` list.

    data: list(dict)
        List (one element per reaction) of dicitionaries (key, value) of data given in the reaction
        mechanism.  Special keys: `alpha`, `beta` contain a dictionary of the empirical power-law
        exponents of reaction rates for reactants and products respectively; `k_f`, `k_b` contain the
        reaction rate constants  per reaction; `info` contains any `string` type for information about
        the reaction.
        E.g.: self.data[idx]['alpha'] = {'e^-': 1e7, 'NO3': 15}
              self.data[idx]['k_f'] = 1e3
              self.data[idx]['info'] = 'condensation reaction'

    stoic_mtrx: numpy.ndarray
        Stoichiometric matrix; 2D `numpy` array.

    latex_species: str
        String containing the LaTeX typetting of the species in the order they appear in the stoichiometric
        matrix. Use the Python print function to print this attribute and copy/paste into a LaTex
        environment.

    latex_rxn: str
        String containing the LaTeX typsetting of all reactions into the LaTeX `align` environment.
    '''

    def __init__(self, header='no-header', file_name=None, mechanism=None, order_species=True,
                 reparam=False, bounds=None):
        '''Module class constructor.

        Build data structures for a reaction mechanism. Namely, species list,
        reactions list, data (equilibrium constant list, etc.), and stoichiometric matrix.

        Reaction mechanism format is as follows:

        # comment
        # comment
        4 NH3 + 5 O2 <=> 4 NO + 6 H2O : quantity1 = 2.5e+02 : quantity2 = '2+2'

        Data follows reaction after ":" as `quantity` = `number`. A `data` dictionary will be
        created as: data['`quantity`'] = `number`. Any number of pairs of keys,value can be
        given.

        Special control word for `alpha` and `beta` data given as power-law exponent of the
        reaction rate empirical formula in the order of reactants and products. E.g.:

        4 NH3 + 5 O2 <=> 4 NO + 6 H2O  :  alpha = (4.3, 5.8) : beta = (4.1, 6.7)

        therefore, alpha[0] is the empirical power-law exponent of the NH3 reactant.
        The data will be stored as a dictionary of a dictionary.
        E.g.: self.data['alpha'] = {'NH3': 4.3, 'O2': 5.8}


        Any amount of spacing in the reaction mechanism description is allowed except:

        a) there must be only one blank space between the stoichiometric coefficient and its
           species name.

        b) there must be at least one blank space before and after each + sign in the reaction.

        c) species formula name are stated as described in Cortix Species() e.g.:
            charge preceded with ^: O2^2+, X^1-, X^+, X^-
            phase in parenthesis (): O2^2+(a), O2^2+(aq), O2^2+(aqu)
            etc.

        There must be no blank lines. A stoichiometric coefficient equal to 1 can be ommited.

        Parameters
        ----------
        file_name: str
            Full path file name of the reaction mechanism file. If the reaction has data
            sucha as equilibrium constant or reaction rate constant, etc., it will follow the
            reaction separated by a colon.

        mechanism: list(str)
            List of reaction strings per above convention. Alternative to information contained
            in a file.

        order_species: bool
            Alphabetically order the species names in the mechanism.

        reparam: bool
           Reparameterize the reaction rate parameters: all reaction rate constants and power-law
           exponents using an exponential transformation: e.g. k_f = exp(k_f'). Now k_f' is the
           actual parameter used in the reaction rate law. This way k_f is guaranteed to be positive
           for any value of k_f'. The entire mechanism is affected.

        Examples
        --------

       '''

        assert file_name is not None or mechanism is not None
        assert isinstance(header, str)
        self.header = header

        if mechanism is not None:
            assert isinstance(mechanism, list)
            assert file_name is None

        if file_name is not None:
            assert isinstance(file_name, str)
            assert mechanism is None

            finput = open(file_name, 'rt')

            mechanism = list()

            for line in finput:
                stripped_line = line.strip()
                mechanism.append(stripped_line)

            finput.close()

        assert isinstance(reparam, bool)

        self.reparam = reparam
        if reparam and bounds is not None:

            try:
                self.kf_bnds = bounds['kf']
            except:
                self.kf_bnds = None

            try:
                self.kb_bnds = bounds['kb']
            except:
                self.kb_bnds = None

            try:
                self.alpha_bnds = bounds['alpha']
            except:
                self.alpha_bnds = None

            try:
                self.beta_bnds = bounds['beta']
            except:
                self.beta_bnds = None

        self.reactions = list()
        self.data = list()

        # Keep the original data internally for future use in sub-mechanisms
        # Remove header and comment lines
        # Also, use any zeros in the alpha/beta coefficients to indicate that the corresponding species
        # is chemically inactive for kinetic purposes.
        self.__original_mechanism = list()

        # First: read the data in the mechanism

        for m_i in mechanism:

            if m_i[0].strip() == '#':
                if self.header == 'no-header':
                    self.header = m_i.strip() + '\n'
                else:
                    self.header += m_i.strip() + '\n'
                continue

            self.__original_mechanism.append(m_i)

            data = m_i.split(':')

            self.reactions.append(data[0].strip())  # do not save comments

            tmp_dict = dict()

            if len(data) > 1:  # if colon separated data exists

                for d in data[1:]:
                    datum = d.strip()

                    name = datum.split('=')[0].strip()
                    val_str = datum.split('=')[1].strip()

                    # alpha and beta names are reserved for the exponents of the reaction rate law
                    # alpha and beta cases; convert tuple of integers into dictionary
                    if name in ('alpha', 'beta'):
                        assert '(' in val_str and ')' in val_str
                        alpha_or_beta = val_str[1:-1]  # ignore "(" and ")"
                        alpha_or_beta_dict = {}  # dict()
                        i = 0
                        for val_s in alpha_or_beta.split(','):
                            val = float(val_s.strip())
                            if self.reparam and val != 0.0:
                                alpha_or_beta_dict[i] = math.log(val)
                            elif val == 0:
                                # internal flag for inactive species
                                alpha_or_beta_dict[i] = -9999
                            else:
                                alpha_or_beta_dict[i] = val
                            i += 1
                        tmp_dict[name] = alpha_or_beta_dict
                    # any other colon separated data
                    elif name == 'info':
                        tmp_dict[name] = val_str
                    elif name == 'k_f' or name == 'k_b':
                        if self.reparam:
                            tmp_dict[name] = math.log(float(val_str))
                        else:
                            tmp_dict[name] = float(val_str)
                    else:
                        tmp_dict[name] = float(val_str)

            self.data.append(tmp_dict)

        # Second: find species

        species_tmp = list()  # temporary list for species

        for idx, rxn in enumerate(self.reactions):

            # the order of the following test matters; test reversible reaction first
            tmp = rxn.split('<=>')
            n_terms = len(tmp)
            assert n_terms == 1 or n_terms == 2

            if n_terms == 1:  # if no previous split
                tmp = rxn.split('<->')
                n_terms = len(tmp)
                assert n_terms == 1 or n_terms == 2
                if n_terms == 1:  # if no previous split
                    tmp = rxn.split('->')
                    n_terms = len(tmp)
                    assert n_terms == 1 or n_terms == 2
                    if n_terms == 1:  # if no previous split
                        tmp = rxn.split('<-')
                        n_terms = len(tmp)
                        assert n_terms == 1 or n_terms == 2

            assert n_terms == 2  # must have two terms

            left = tmp[0].strip()
            right = tmp[1].strip()

            left_terms = left.split(' + ')
            right_terms = right.split(' + ')

            terms = [t.strip() for t in left_terms] + [t.strip()
                             for t in right_terms]

            for i in terms:
                tmp = i.split(' ')
                assert len(tmp) == 1 or len(tmp) == 2, ' tmp = %r ' % tmp
                if len(tmp) == 2:
                    species_tmp.append(tmp[1].strip())
                else:
                    species_tmp.append(i.strip())

        species_filter = set(species_tmp)  # filter species as a set

        # convert species set to list
        self.species_names = list(species_filter)

        if order_species:
            self.species_names = sorted(self.species_names)

        # Create the species list
        self.species = list()

        for name in self.species_names:
            spc = Species(name=name, formula_name=name)
            self.species.append(spc)

        # Third: build the stoichiometric matrix

        s_mtrx = np.zeros(
            (len(self.reactions), len(self.species)), dtype=np.float64)

        self.reaction_direction_symbol = list()

        for r in self.reactions:

            i_row = self.reactions.index(r)

            tmp = r.split(' -> ')
            n_terms = len(tmp)
            assert n_terms == 1 or n_terms == 2
            if n_terms == 2:
                self.reaction_direction_symbol.append('->')
            if n_terms == 1:
                tmp = r.split(' <-> ')
                n_terms = len(tmp)
                assert n_terms == 1 or n_terms == 2
                if n_terms == 2:
                    self.reaction_direction_symbol.append('<->')
                if n_terms == 1:
                    tmp = r.split(' <=> ')
                    n_terms = len(tmp)
                    assert n_terms == 1 or n_terms == 2
                    if n_terms == 2:
                        self.reaction_direction_symbol.append('<=>')
                    if n_terms == 1:
                        tmp = r.split(' <- ')
                        n_terms = len(tmp)
                        assert n_terms == 1 or n_terms == 2
                        if n_terms == 2:
                            self.reaction_direction_symbol.append('<-')

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
                    assert s_mtrx[i_row, j_col] == 0.0, \
                           'duplicates not allowed r%r: %r %r %r' %\
                           (i_row, r, species_member, s_mtrx[i_row, j_col])
                    s_mtrx[i_row, j_col] = -1.0 * coeff
                else:
                    species_member = tmp[0].strip()
                    j_col = self.species_names.index(species_member)
                    assert s_mtrx[i_row, j_col] == 0.0, \
                           'duplicates not allowed r%r: %r %r %r' %\
                           (i_row, r, species_member, s_mtrx[i_row, j_col])
                    s_mtrx[i_row, j_col] = -1.0

                if 'alpha' in self.data[i_row].keys():
                    species_name = self.species_names[j_col]
                    assert len(self.data[i_row]['alpha']) == len(
                        left_terms), 'Incorrect length of alpha.'
                    # replace species index with name
                    self.data[i_row]['alpha'][species_name] = self.data[i_row]['alpha'].pop(
                        left_terms.index(t))

            for t in right_terms:
                tmp = t.split(' ')
                if len(tmp) == 2:
                    coeff = float(tmp[0].strip())
                    species_member = tmp[1].strip()
                    j_col = self.species_names.index(species_member)
                    assert s_mtrx[i_row, j_col] == 0.0, \
                           'duplicates not allowed r%r: %r %r %r' %\
                           (i_row, r, species_member, s_mtrx[i_row, j_col])
                    s_mtrx[i_row, j_col] = 1.0 * coeff
                else:
                    species_member = tmp[0].strip()
                    j_col = self.species_names.index(species_member)
                    assert s_mtrx[i_row, j_col] == 0.0, \
                           'duplicates not allowed r%r: %r %r %r' %\
                           (i_row, r, species_member, s_mtrx[i_row, j_col])
                    s_mtrx[i_row, j_col] = 1.0

                if 'beta' in self.data[i_row].keys():
                    species_name = self.species_names[j_col]
                    assert len(self.data[i_row]['beta']) == len(
                        right_terms), 'Incorrect length of beta.'
                    # replace species index with name
                    self.data[i_row]['beta'][species_name] = self.data[i_row]['beta'].pop(
                        right_terms.index(t))

        self.stoic_mtrx = s_mtrx

        # Create the latex typesetting of reactions and species
        (self.latex_species, self.latex_rxn) = self.__latex()

        # Fill-in missing k_f, k_b, alpha, and beta
        for idx, dat in enumerate(self.data):
            if 'k_f' not in dat.keys():
                if self.reparam:
                    dat['k_f'] = -1e+10  # math.log(0.0)
                else:
                    dat['k_f'] = 0.0
            if 'k_b' not in dat.keys():
                if self.reparam:
                    dat['k_b'] = -1e+10  # math.log(0.0)
                else:
                    dat['k_b'] = 0.0
            if 'alpha' not in dat.keys():
                (reactants_ids, ) = np.where(self.stoic_mtrx[idx, :] < 0)
                tmp = dict()
                for j in reactants_ids:
                    spc_name = self.species_names[j]
                    if self.reparam:
                        tmp[spc_name] = math.log(abs(self.stoic_mtrx[idx, j]))
                    else:
                        tmp[spc_name] = abs(self.stoic_mtrx[idx, j])
                dat['alpha'] = tmp
            if 'beta' not in dat.keys():
                (products_ids, ) = np.where(self.stoic_mtrx[idx, :] > 0)
                tmp = dict()
                for j in products_ids:
                    spc_name = self.species_names[j]
                    if self.reparam:
                        tmp[spc_name] = math.log(abs(self.stoic_mtrx[idx, j]))
                    else:
                        tmp[spc_name] = abs(self.stoic_mtrx[idx, j])
                dat['beta'] = tmp

        # Fill-in missing info
        for idx, dat in enumerate(self.data):
            if 'info' not in dat.keys():
                dat['info'] = 'no-info'

    def mass_balance_residuals(self):
        '''Reaction mass balance residual vector.

        Returns
        -------

        mb_residual_vec: numpy.ndarray
            1D vector of mass balance residuals for each reaction.
        '''

        m_vec = np.zeros(len(self.species), dtype=np.float64)

        for idx, spc in enumerate(self.species):
            m_vec[idx] = spc.molar_mass

        assert np.prod(m_vec) > 0.0

        mb_residual_vec = self.stoic_mtrx @ m_vec

        return mb_residual_vec

    def max_mass_balance_residual(self):
        '''Compute the maximum magnitude reaction mass balance residual.

        Returns
        -------

        max(abs(mb): float

        '''

        mb_residual_vec = self.mass_balance_residuals()

        return np.max(np.abs(mb_residual_vec))

    def is_mass_conserved(self, tol=1e-10):
        '''Check mass conservation if species have a molar mass value.

        Returns
        -------

        bool

        '''

        residual = self.max_mass_balance_residual()

        return True if residual < tol else False

    def rank_analysis(self, verbose=False, tol=1e-8):
        '''Compute the rank of the stoichiometric matrix.

        This will establish rank deficiency.

        Parameters
        ----------

        verbose: bool
        tol: float

        Returns
        -------

        rank: int
        '''

        # assert self.is_mass_conserved(tol), 'fatal: mass conservation failed'

        s_rank = np.linalg.matrix_rank(self.stoic_mtrx, tol=tol)

        assert s_rank <= min(self.stoic_mtrx.shape)

        if verbose:
            print('*********************')
            print('# reactions = ', len(self.reactions))
            print('# species   = ', len(self.species))
            print('rank of S = ', s_rank)

            if s_rank == min(self.stoic_mtrx.shape):
                print('S is full rank.')
            else:
                print('S is rank deficient.')
            print('*********************')

        if s_rank == self.stoic_mtrx.shape[1]:
            print('***********************')
            print('Warning: rank = n')
            print('Reaction mechanism fails mass conservation')
            print('***********************')

        return s_rank

    def r_vec(self, spc_molar_cc_vec, kf_vec=None, kb_vec=None, alpha_lst=None, beta_lst=None):
        '''Compute the reaction rate density vector.

        Parameters
        ----------
        spc_molar_cc_vec: numpy.ndarray
        Ordered (same as the reaction mechanism) molar concentration vector.

        kf_vec: numpy.ndarray
        Vector of forward reaction rate constants per reaction. If not provided, it will be assembled
        internally.

        kb_vec: numpy.ndarray
        Vector of backward reaction rate constants per reaction. If not provided, it will be assembled
        internally.

        alpha_lst: list(numpy.ndarray)
        List of alpha power-law exponents as a matrix containing the reactant species ids.
        If not provided, it will be assembled internally from `self.data`.

        beta_lst: list(numpy.ndarray)
        List of beta power-law exponents as a matrix containing the product species ids.
        If not provided, it will be assembled internally from `self.data`.
        '''
        assert isinstance(spc_molar_cc_vec, numpy.ndarray), 'type(spc_molar_cc_vec) = %r' % (
            type(spc_molar_cc_vec))
        assert spc_molar_cc_vec.size == len(self.species)

        if kf_vec is not None:
            assert isinstance(kf_vec, np.ndarray)
            assert kf_vec.size == len(self.reactions)
        else:
            (kf_vec, _) = self.__get_ks()
        if self.reparam:
            if self.kf_bnds is not None:

                min_kf = self.kf_bnds[0]
                max_kf = self.kf_bnds[1]

                kf_vec = min_kf + (max_kf - min_kf) / (1 + np.exp(kf_vec))

            else:
                kf_vec = np.exp(kf_vec)

        if kb_vec is not None:
            assert isinstance(
                kb_vec, np.ndarray), 'type(kb_vec)=%r' % (type(kb_vec))
            assert kb_vec.size == len(self.reactions)
        else:
            (_, kb_vec) = self.__get_ks()

        if self.reparam:
            if self.kb_bnds is not None:

                # min_kb = self.kb_bnds[0]
                # max_kb = self.kb_bnds[1]

                # kb_vec = min_kb + (max_kb - min_kb) / (1 + np.exp(kb_vec))
                kb_vec = self.bounded_reparam(kb_vec, self.kb_bnds)

            else:
                kb_vec = np.exp(kb_vec)

        if alpha_lst is not None:
            assert isinstance(alpha_lst, list)
            assert len(alpha_lst) == len(self.reactions), '# reactions=%r alpha_lst=\n%r' % (
                len(self.reactions), alpha_lst)
            assert isinstance(alpha_lst[0], np.ndarray)
            assert alpha_lst[0].shape[0] == 2
        else:
            (alpha_lst, _) = self.__get_power_law_exponents()

        if self.reparam:
            alpha_lst = copy.deepcopy(alpha_lst)

            if self.alpha_bnds is not None:

               min_alpha = self.alpha_bnds[0]
               max_alpha = self.alpha_bnds[1]

               for idx, alpha_mtrx in enumerate(alpha_lst):
                   a_vec = min_alpha[idx]
                   b_vec = max_alpha[idx]

                   local_alpha_vec = alpha_mtrx[1, :]

                   local_alpha_vec = a_vec + \
                       (b_vec - a_vec) / (1 + np.exp(local_alpha_vec))

                   alpha_lst[idx] = np.array(
                       (alpha_mtrx[0, :], local_alpha_vec))

            else:

                for idx, alpha_mtrx in enumerate(alpha_lst):
                    alpha_lst[idx] = np.array(
                        (alpha_mtrx[0, :], np.exp(alpha_mtrx[1, :])))

        if beta_lst is not None:
            assert isinstance(beta_lst, list)
            assert len(beta_lst) == len(self.reactions)
            assert isinstance(beta_lst[0], np.ndarray)
            assert beta_lst[0].shape[0] == 2
        else:
            (_, beta_lst) = self.__get_power_law_exponents()

        if self.reparam:
            beta_lst = copy.deepcopy(beta_lst)

            if self.beta_bnds is not None:

               min_beta = self.beta_bnds[0]
               max_beta = self.beta_bnds[1]

               for idx, beta_mtrx in enumerate(beta_lst):

                   a_vec = min_beta[idx]
                   b_vec = max_beta[idx]

                   local_beta_vec = beta_mtrx[1, :]

                   local_beta_vec = a_vec + \
                       (b_vec - a_vec) / (1 + np.exp(local_beta_vec))

                   beta_lst[idx] = np.vstack([beta_mtrx[0, :], local_beta_vec])

            else:

                for idx, beta_mtrx in enumerate(beta_lst):
                    beta_lst[idx] = np.array(
                        (beta_mtrx[0, :], np.exp(beta_mtrx[1, :])))

        # Compute the reaction rate density vector
        r_vec = np.zeros(len(self.reactions), dtype=np.float64)

        for (idx, rxn_data) in enumerate(self.data):

            alpha_mtrx = alpha_lst[idx]

            reactants_ids = alpha_mtrx[0, :].astype(int)

            # must be oredered as in rxn_mech
            reactants_molar_cc = spc_molar_cc_vec[reactants_ids]

            '''
            print('')
            print('kf_vec[idx] =', kf_vec[idx])
            print('reactants_molar_cc =', reactants_molar_cc)
            print('alpha_mtrx[1,:] =', alpha_mtrx[1,:])
            print('reactants ids =',reactants_ids)
            print('reactants spc =',[self.species_names[i]
                  for i in reactants_ids])
            '''
            reactants_molar_cc[reactants_molar_cc < 0] = 0.0
            r_vec[idx] = kf_vec[idx] * \
                np.prod(reactants_molar_cc**alpha_mtrx[1, :])

        for (idx, rxn_data) in enumerate(self.data):

            beta_mtrx = beta_lst[idx]

            products_ids = beta_mtrx[0, :].astype(int)

            # must be oredered as in rxn_mech
            products_molar_cc = spc_molar_cc_vec[products_ids]

            r_vec[idx] -= kb_vec[idx] * \
                np.prod(products_molar_cc**beta_mtrx[1, :])

        return r_vec

    def rxn_rate_law(self, spc_molar_cc_vec, kf_vec=None, kb_vec=None, alpha_lst=None, beta_lst=None):
        '''See r_vec.
        '''

        return self.r_vec(spc_molar_cc_vec, kf_vec, kb_vec, alpha_lst, beta_lst)

    def g_vec(self, spc_molar_cc_vec, kf_vec=None, kb_vec=None, alpha_lst=None, beta_lst=None):
        '''Compute the species production rate density vector.

        Parameters:
        -----------
        '''

        g_vec = self.stoic_mtrx.transpose() @ self.r_vec(spc_molar_cc_vec,
                                        kf_vec, kb_vec, alpha_lst, beta_lst)

        return g_vec

    def bounded_reparam(self, lst_or_vec, bnds):

        if isinstance(lst_or_vec, list):

           min_beta = bnds[0]
           max_beta = bnds[1]

           beta_lst = lst_or_vec

           for idx, beta_mtrx in enumerate(beta_lst):

               a_vec = min_beta[idx]
               b_vec = max_beta[idx]

               local_beta_vec = beta_mtrx[1, :]

               local_beta_vec = a_vec + \
                       (b_vec - a_vec) / (1 + np.exp(local_beta_vec))

               beta_lst[idx] = np.vstack([beta_mtrx[0, :], local_beta_vec])

           reparamed = beta_lst

        else:
            kb_vec = lst_or_vec
            min_kb = bnds[0]
            max_kb = bnds[1]

            kb_vec = min_kb + (max_kb - min_kb) / (1 + np.exp(kb_vec))

            reparamed = kb_vec

        return reparamed

    def species_prod_rate_dens(self, spc_molar_cc_vec, kf_vec = None, kb_vec = None, alpha_lst =None, beta_lst=None):
        '''Compute the species production rate density vector.

        Parameters:
        -----------
        '''

        return self.g_vec(spc_molar_cc_vec, kf_vec, kb_vec, alpha_lst, beta_lst)

    def dr_dtheta_mtrx(self, spc_molar_cc_vec,
                      kf_vec = None, kb_vec =None, alpha_lst=None, beta_lst=None):
        '''Partial derivative of the reaction rate law vector wrt parameters.

        The parameters in the derivative are ordered as: k_fs, k_bs, alphas, betas.
        If a parameter is `None`, it indicates that it is not to be considered a varying parameter.
        As of now parameter sensitivity is either on or off for all kf's , or k'bs, or alphas, or betas.
        Maybe this can be relaxed for individual reaction parameters later.

        The matrix is m x p. Where m is the number of reactions, p is the total number of parameters.
        That is, p = 2 * m + n_Ri + n_Pi, where n_Ri is the number of active reactant species, and
        n_Pi is the number of active product species. If say, alpha_lst is not a varying parameter,
        then n_Ri = 0.
        '''

        assert isinstance(spc_molar_cc_vec, np.ndarray)
        assert spc_molar_cc_vec.size == len(self.species)
        assert np.all(spc_molar_cc_vec >= 0), 'spc_molar_cc_vec =\n%r' % spc_molar_cc_vec

        # -----------------------
        # partial_kf(r_vec) mtrx
        # -----------------------
        if kf_vec is not None:

            if self.reparam:
                kf_vec=np.exp(kf_vec)

            if alpha_lst is None:
                (alpha_lst_local, _)=self.__get_power_law_exponents()
            else:
                alpha_lst_local=alpha_lst

            if self.reparam:
                alpha_lst_local=copy.deepcopy(alpha_lst_local)
                for idx, alpha_mtrx in enumerate(alpha_lst_local):
                    alpha_lst_local[idx]= np.array((alpha_mtrx[0, :], np.exp(alpha_mtrx[1, :])))

            dr_dk_f = np.zeros((len(self.reactions), len(self.reactions)), dtype = np.float64)

            for (idx, rxn_data) in enumerate(self.data):

                alpha_mtrx=alpha_lst_local[idx]
                reactants_ids=alpha_mtrx[0, :].astype(int)

                reactants_molar_cc=spc_molar_cc_vec[reactants_ids]

                spc_cc_power_prod=np.prod(reactants_molar_cc**alpha_mtrx[1, :])

                if self.reparam:
                    dr_dk_f[idx, idx]=kf_vec[idx] * spc_cc_power_prod
                else:
                    dr_dk_f[idx, idx]=spc_cc_power_prod

            try:
                dr_dtheta_mtrx=np.hstack([dr_dtheta_mtrx, dr_dk_f])
            except NameError:
                dr_dtheta_mtrx=np.hstack([dr_dk_f])

        # -----------------------
        # partial_kb(r_vec) mtrx
        # -----------------------
        if kb_vec is not None:

            if self.reparam:
                kb_vec=np.exp(kb_vec)

            if beta_lst is None:
                (_, beta_lst_local)=self.__get_power_law_exponents()
            else:
                beta_lst_local=beta_lst

            if self.reparam:
                beta_lst_local=copy.deepcopy(beta_lst_local)
                for idx, beta_mtrx in enumerate(beta_lst_local):
                    beta_lst_local[idx]= np.array((beta_mtrx[0, :], np.exp(beta_mtrx[1, :])))

            dr_dk_b = np.zeros((len(self.reactions), len(self.reactions)), dtype = np.float64)

            for idx, rxn_data in enumerate(self.data):

                beta_mtrx=beta_lst_local[idx]
                products_ids=beta_mtrx[0, :].astype(int)

                products_molar_cc=spc_molar_cc_vec[products_ids]

                spc_cc_power_prod=np.prod(products_molar_cc**beta_mtrx[1, :])

                if self.reparam:
                    dr_dk_b[idx, idx]=- kb_vec[idx] * spc_cc_power_prod
                else:
                    dr_dk_b[idx, idx]=- spc_cc_power_prod

            try:
                dr_dtheta_mtrx=np.hstack([dr_dtheta_mtrx, dr_dk_b])
            except NameError:
                dr_dtheta_mtrx=np.hstack([dr_dk_b])

        # --------------------------
        # partial_alpha(r_vec) mtrx
        # --------------------------
        if alpha_lst is not None:

            n_alphas=0
            for alpha_mtrx in alpha_lst:
                n_alphas += alpha_mtrx.shape[1]

            if self.reparam:
                alpha_lst=copy.deepcopy(alpha_lst)
                for idx, alpha_mtrx in enumerate(alpha_lst):
                    alpha_lst[idx]= np.array((alpha_mtrx[0, :], np.exp(alpha_mtrx[1, :])))

            dr_dalpha= np.zeros((len(self.reactions), n_alphas), dtype = np.float64)

            if kf_vec is None:
                (kf_vec_local, _)=self.__get_ks()
            else:
                kf_vec_local=kf_vec

            if self.reparam:
                kf_vec_local=np.exp(kf_vec_local)

            dr_dalpha_j0=0
            for (idx, rxn_data) in enumerate(self.data):

                alpha_mtrx=alpha_lst[idx]
                reactants_ids=alpha_mtrx[0, :].astype(int)

                reactants_molar_cc=spc_molar_cc_vec[reactants_ids]

                spc_cc_power_prod=np.prod(reactants_molar_cc**alpha_mtrx[1, :])

                rf_i=kf_vec_local[idx] * spc_cc_power_prod

                min_c_j=reactants_molar_cc.min()
                if min_c_j <= 1e-25:
                    (jdx, )=np.where(reactants_molar_cc == min_c_j)
                    reactants_molar_cc[jdx]=1.0  # any non-zero value will do since rf_i will be zero

                for (jdx, c_j) in enumerate(reactants_molar_cc):

                    if self.reparam:
                        dr_dalpha[idx, dr_dalpha_j0 + jdx] = math.log(c_j) * alpha_mtrx[1, jdx] * rf_i
                    else:
                        dr_dalpha[idx, dr_dalpha_j0 + jdx]= math.log(c_j) * rf_i

                dr_dalpha_j0 += alpha_mtrx.shape[1]

            assert dr_dalpha_j0 == n_alphas, 'n_alphas = %r; sum = %r' % (n_alphas, dr_dalpha_j0)

            try:
                dr_dtheta_mtrx=np.hstack([dr_dtheta_mtrx, dr_dalpha])
            except NameError:
                dr_dtheta_mtrx=np.hstack([dr_dalpha])

        # -------------------------
        # partial_beta(r_vec) mtrx
        # -------------------------
        if beta_lst is not None:

            n_betas=0
            for beta_mtrx in beta_lst:
                n_betas += beta_mtrx.shape[1]

            if self.reparam:
                beta_lst=copy.deepcopy(beta_lst)
                for idx, beta_mtrx in enumerate(beta_lst):
                    beta_lst[idx]= np.array((beta_mtrx[0, :], np.exp(beta_mtrx[1, :])))

            dr_dbeta= np.zeros((len(self.reactions), n_betas), dtype = np.float64)

            if kb_vec is None:
                (_, kb_vec_local)=self.__get_ks()
            else:
                kb_vec_local=kb_vec

            if self.reparam:
                kb_vec_local=np.exp(kb_vec_local)

            dr_dbeta_j0=0
            for idx, rxn_data in enumerate(self.data):

                beta_mtrx=beta_lst[idx]
                products_ids=beta_mtrx[0, :].astype(int)

                products_molar_cc=spc_molar_cc_vec[products_ids]

                spc_cc_power_prod=np.prod(products_molar_cc**beta_mtrx[1, :])

                rb_i=- kb_vec_local[idx] * spc_cc_power_prod

                min_c_j=products_molar_cc.min()
                if min_c_j <= 1e-25:
                    (jdx, )=np.where(products_molar_cc == min_c_j)
                    products_molar_cc[jdx]=1.0  # any non-zero value will do it since rb_i will be zero

                for (jdx, c_j) in enumerate(products_molar_cc):

                    if self.reparam:
                        dr_dbeta[idx, dr_dbeta_j0 + jdx] = math.log(c_j) * beta_mtrx[1, jdx] * rb_i
                    else:
                        dr_dbeta[idx, dr_dbeta_j0 + jdx]= math.log(c_j) * rb_i

                dr_dbeta_j0 += beta_mtrx.shape[1]

            assert dr_dbeta_j0 == n_betas, 'n_betas = %r sum = %r' % (
                n_betas, dr_dbeta_j0)

            try:
                dr_dtheta_mtrx=np.hstack([dr_dtheta_mtrx, dr_dbeta])
            except NameError:
                dr_dtheta_mtrx=np.hstack([dr_dbeta])

        return dr_dtheta_mtrx

    def dr_dtheta_mtrx_numerical(self, spc_molar_cc_vec,
                      kf_vec = None, kb_vec =None, alpha_lst=None, beta_lst=None,
                      h_small = 1e-6):
        '''Numerical partial derivative of the reaction rate law vector wrt parameters.

        The parameters in the derivative are ordered as: k_fs, k_bs, alphas, betas.
        If a parameter is `None`, it is not considered a varying parameter.
        As of now parameter sensitivity is either on or off for all kf's , or k'bs, or alphas, or betas.
        Maybe this can be extended for individual reaction parameters later.

        The matrix is m x p. Where m is the number of reactions, p is the total number of parameters.
        That is, p = 2 * m + n_Ri + n_Pi, where n_Ri is the number of active reactant species, and
        n_Pi is the number of active product species. If say, alpha_lst is not a varying parameter,
        then n_Ri = 0.
        '''

        assert isinstance(spc_molar_cc_vec, np.ndarray)
        assert spc_molar_cc_vec.size == len(self.species)
        assert np.all(spc_molar_cc_vec >= 0), 'spc_molar_cc_vec =\n%r' % spc_molar_cc_vec

        # --------------------------------
        # Partial r_vec partial kf matrix
        # --------------------------------
        if kf_vec is not None:

            if alpha_lst is None:
                (alpha_lst_local, _)=self.__get_power_law_exponents()
            else:
                alpha_lst_local=alpha_lst

            dr_dk_f = np.zeros((len(self.reactions), len(self.reactions)), dtype = np.float64)
            i_mtrx= np.eye(len(self.reactions), dtype = np.float64)

            for jdx in range(len(self.data)):

                r_vec_h = self.r_vec(spc_molar_cc_vec, kf_vec = kf_vec + h_small*i_mtrx[:,jdx], alpha_lst =alpha_lst_local)
                r_vec = self.r_vec(spc_molar_cc_vec, kf_vec = kf_vec, alpha_lst =alpha_lst_local)

                dr_dk_f[:, jdx]=(r_vec_h - r_vec) / h_small

            try:
                dr_dtheta_mtrx=np.hstack([dr_dtheta_mtrx, dr_dk_f])
            except NameError:
                dr_dtheta_mtrx=np.hstack([dr_dk_f])

        # --------------------------------
        # Partial r_vec partial kb matrix
        # --------------------------------
        if kb_vec is not None:

            if beta_lst is None:
                (_, beta_lst_local)=self.__get_power_law_exponents()
            else:
                beta_lst_local=beta_lst

            dr_dk_b = np.zeros((len(self.reactions), len(self.reactions)), dtype = np.float64)
            i_mtrx= np.eye(len(self.reactions), dtype = np.float64)

            for jdx in range(len(self.data)):

                r_vec_h = self.r_vec(spc_molar_cc_vec, kb_vec = kb_vec + h_small*i_mtrx[:,jdx], beta_lst =beta_lst_local)
                r_vec = self.r_vec(spc_molar_cc_vec, kb_vec = kb_vec, beta_lst =beta_lst_local)

                dr_dk_b[:, jdx]=(r_vec_h - r_vec) / h_small

            try:
                dr_dtheta_mtrx=np.hstack([dr_dtheta_mtrx, dr_dk_b])
            except NameError:
                dr_dtheta_mtrx=np.hstack([dr_dk_b])

        # -----------------------------------
        # Partial r_vec partial alpha matrix
        # -----------------------------------
        if alpha_lst is not None:

            n_alphas=0
            for alpha_mtrx in alpha_lst:
                n_alphas += alpha_mtrx.shape[1]

            dr_dalpha= np.zeros((len(self.reactions), n_alphas), dtype = np.float64)
            i_mtrx= np.eye(n_alphas, dtype = np.float64)

            if kf_vec is None:
                (kf_vec_local, _)=self.__get_ks()
            else:
                kf_vec_local=kf_vec

            for jdx in range(n_alphas):

                assert False, 'FIXME'

                r_vec_h = self.r_vec(spc_molar_cc_vec, alpha_lst = alpha_lst + h_small*i_mtrx[:,jdx], kf_vec =kf_vec_local)
                r_vec = self.r_vec(spc_molar_cc_vec, alpha_lst = alpha_lst, kf_vec =kf_vec_local)

                dr_dalpha[:, jdx]=(r_vec_h - r_vec) / h_small

            try:
                dr_dtheta_mtrx=np.hstack([dr_dtheta_mtrx, dr_dalpha])
            except NameError:
                dr_dtheta_mtrx=np.hstack([dr_dalpha])

        # ----------------------------------
        # Partial r_vec partial beta matrix
        # ----------------------------------
        if beta_lst is not None:

            n_betas=0
            for beta_vec in beta_lst:
                # assert np.all(beta_vec>=0)
                n_betas += beta_vec.size

            dr_dbeta = np.zeros((len(self.reactions), n_betas), dtype = np.float64)
            i_mtrx= np.eye(n_betas, dtype = np.float64)

            if kb_vec is None:
                (_, kb_vec_local)=self.__get_ks()
            else:
                kb_vec_local=kb_vec

            for jdx in range(n_betas):

                assert False, 'FIXME'

                r_vec_h = self.r_vec(spc_molar_cc_vec, beta_lst = beta_lst + h_small*i_mtrx[:,jdx], kb_vec =kb_vec_local)
                r_vec = self.r_vec(spc_molar_cc_vec, beta_lst = beta_lst, kb_vec =kb_vec_local)

                dr_dbeta[:, jdx]=(r_vec_h - r_vec) / h_small

            try:
                dr_dtheta_mtrx=np.hstack([dr_dtheta_mtrx, dr_dbeta])
            except NameError:
                dr_dtheta_mtrx=np.hstack([dr_dbeta])

        return dr_dtheta_mtrx

    def d2ri_theta2_mtrx(self, rxn_idx, spc_molar_cc_vec,
                               kf_vec = None, kb_vec =None, alpha_lst=None, beta_lst=None):
        '''Second partial derivatives of the ith reaction rate law wrt parameters.

        Only the forward case reaction case is implemented.

        The parameters in the derivative are ordered as: k_fs, k_bs, alphas, betas.
        The matrix is p x p. Where p is the total number of parameters.
        That, is p = 2 * m + n_Ri + n_Pi, where n_Ri is the number of active reactant species, and
        n_Pi is the number of active product species.
        '''

        assert isinstance(rxn_idx, int)
        assert rxn_idx <= len(self.reactions)

        assert isinstance(spc_molar_cc_vec, np.ndarray)
        assert spc_molar_cc_vec.size == len(self.species)
        assert np.all(spc_molar_cc_vec >= 0), 'spc_molar_cc_vec =\n%r' % spc_molar_cc_vec

        # *******************************************************************************************
        # 1st row block

        # ---------------------------
        # partial_kf(partial_kf r_i)
        # ---------------------------
        if kf_vec is not None:

            d_kf_d_kf_ri_mtrx= np.zeros((len(self.reactions), len(self.reactions)), dtype = np.float64)

            if self.reparam:

                if alpha_lst is None:
                    (alpha_lst_local, _)=self.__get_power_law_exponents()
                else:
                    alpha_lst_local=alpha_lst

                alpha_lst_local=copy.deepcopy(alpha_lst_local)
                for idx, alpha_mtrx in enumerate(alpha_lst_local):
                    alpha_lst_local[idx]= np.array((alpha_mtrx[0, :], np.exp(alpha_mtrx[1, :])))

                kf_vec=np.exp(kf_vec)

                for (idx, rxn_data) in enumerate(self.data):

                    alpha_mtrx=alpha_lst_local[idx]
                    reactants_ids=alpha_mtrx[0, :].astype(int)

                    reactants_molar_cc=spc_molar_cc_vec[reactants_ids]

                    spc_cc_power_prod=np.prod(reactants_molar_cc**alpha_mtrx[1, :])

                    d_kf_d_kf_ri_mtrx[idx, idx]=kf_vec[idx] * spc_cc_power_prod

        # ---------------------------
        # partial_kb(partial_kf r_i)
        # ---------------------------
        if kf_vec is not None and kb_vec is not None:

            d_kb_d_kf_ri_mtrx= np.zeros((len(self.reactions), len(self.reactions)), dtype = np.float64)

        # ------------------------------
        # partial_alpha(partial_kf r_i)
        # ------------------------------
        if kf_vec is not None and alpha_lst is not None:

            n_alphas=0
            for alpha_mtrx in alpha_lst:
                n_alphas += alpha_mtrx.shape[1]

            d_alpha_d_kf_ri_mtrx= np.zeros((len(self.reactions), n_alphas), dtype = np.float64)

            if self.reparam:
                alpha_lst=copy.deepcopy(alpha_lst)
                for idx, alpha_mtrx in enumerate(alpha_lst):
                    alpha_lst[idx]= np.array((alpha_mtrx[0, :], np.exp(alpha_mtrx[1, :])))

            if self.reparam:
                kf_vec=np.exp(kf_vec)

            jdx_start=0
            for (idx, rxn_data) in enumerate(self.data):  # loop to find the column index

                alpha_mtrx=alpha_lst[idx]

                if idx != rxn_idx:
                    jdx_start += alpha_mtrx.shape[1]
                    continue

                reactants_ids=alpha_mtrx[0, :].astype(int)

                reactants_molar_cc=spc_molar_cc_vec[reactants_ids]

                spc_cc_power_prod=np.prod(reactants_molar_cc**alpha_mtrx[1, :])

                min_c_j=reactants_molar_cc.min()
                if min_c_j <= 1e-25:
                    (jdx, )=np.where(reactants_molar_cc == min_c_j)
                    reactants_molar_cc[jdx]=1.0  # any non-zero value will do since rb_i will be zero

                for (jdx, c_j) in enumerate(reactants_molar_cc):

                    if self.reparam:
                        d_alpha_d_kf_ri_mtrx[idx, jdx_start + jdx] = kf_vec[idx] * math.log(c_j) * alpha_mtrx[1, jdx] * spc_cc_power_prod
                    else:
                        d_alpha_d_kf_ri_mtrx[idx, jdx_start + jdx]= math.log(c_j) * spc_cc_power_prod

                jdx_start += alpha_mtrx.shape[1]

            assert jdx_start == n_alphas, 'n_alphas = %r; sum = %r' % (n_alphas, jdx_start)

        # ------------------------------
        # partial_beta(partial_kf r_i)
        # ------------------------------
        if kf_vec is not None and beta_lst is not None:

            n_betas=0
            for beta_mtrx in beta_lst:
                n_betas += beta_mtrx.shape[1]

            d_beta_d_kf_ri_mtrx= np.zeros((len(self.reactions), n_betas), dtype = np.float64)

        # *******************************************************************************************
        # 2nd row block

        # ---------------------------
        # partial_kb(partial_kb r_i)
        # ---------------------------
        if kb_vec is not None:

            d_kb_d_kb_ri_mtrx= np.zeros((len(self.reactions), len(self.reactions)), dtype = np.float64)

            if self.reparam:

                if beta_lst is None:
                    (_, beta_lst_local)=self.__get_power_law_exponents()
                else:
                    beta_lst_local=beta_lst

                beta_lst_local=copy.deepcopy(beta_lst_local)
                for idx, beta_mtrx in enumerate(beta_lst_local):
                    beta_lst_local[idx]= np.array((beta_mtrx[0, :], np.exp(beta_mtrx[1, :])))

                kb_vec=np.exp(kb_vec)

                for idx, rxn_data in enumerate(self.data):

                    beta_mtrx=beta_lst_local[idx]
                    products_ids=beta_mtrx[0, :].astype(int)

                    products_molar_cc=spc_molar_cc_vec[products_ids]

                    spc_cc_power_prod=np.prod(products_molar_cc**beta_mtrx[1, :])

                    d_kb_d_kb_ri_mtrx[idx, idx]=- \
                        kb_vec[idx] * spc_cc_power_prod

        # ------------------------------
        # partial_alpha(partial_kb r_i)
        # ------------------------------
        if kb_vec is not None and alpha_lst is not None:

            n_alphas=0
            for alpha_mtrx in alpha_lst:
                n_alphas += alpha_mtrx.shape[1]

            d_alpha_d_kb_ri_mtrx= np.zeros((len(self.reactions), n_alphas), dtype = np.float64)

        # ------------------------------
        # partial_beta(partial_kb r_i)
        # ------------------------------
        if kb_vec is not None and beta_lst is not None:

            n_betas=0
            for beta_mtrx in beta_lst:
                n_betas += beta_mtrx.shape[1]

            d_beta_d_kb_ri_mtrx= np.zeros((len(self.reactions), n_betas), dtype = np.float64)

            if self.reparam:
                beta_lst=copy.deepcopy(beta_lst)
                for idx, beta_mtrx in enumerate(beta_lst):
                    beta_lst[idx]= np.array((beta_mtrx[0, :], np.exp(beta_mtrx[1, :])))

            if self.reparam:
                kb_vec=np.exp(kb_vec)

            jdx_start=0
            for (idx, rxn_data) in enumerate(self.data):  # loop to find the column index

                beta_mtrx=beta_lst[idx]

                if idx != rxn_idx:
                    jdx_start += beta_mtrx.shape[1]
                    continue

                products_ids=beta_mtrx[0, :].astype(int)

                products_molar_cc=spc_molar_cc_vec[products_ids]

                spc_cc_power_prod=np.prod(products_molar_cc**beta_mtrx[1, :])

                min_c_j=products_molar_cc.min()
                if min_c_j <= 1e-25:
                    (jdx, )=np.where(products_molar_cc == min_c_j)
                    products_molar_cc[jdx]=1.0  # any non-zero value will do since rb_i will be zero

                for (jdx, c_j) in enumerate(products_molar_cc):

                    if self.reparam:
                        d_beta_d_kb_ri_mtrx[idx, jdx_start + jdx] = kb_vec[idx] * math.log(c_j) * beta_mtrx[1, jdx] * spc_cc_power_prod
                    else:
                        d_beta_d_kb_ri_mtrx[idx, jdx_start + jdx]= math.log(c_j) * spc_cc_power_prod

                jdx_start += beta_mtrx.shape[1]

            assert jdx_start == n_betas, 'n_betas = %r; sum = %r' % (
                n_betas, jdx_start)

        # *******************************************************************************************
        # 3rd row block

        # ---------------------------------
        # partial_alpha(partial_alpha r_i)
        # ---------------------------------
        if alpha_lst is not None:

            n_alphas=0
            for alpha_mtrx in alpha_lst:
                n_alphas += alpha_mtrx.shape[1]

            d_alpha_d_alpha_ri_mtrx= np.zeros((n_alphas, n_alphas), dtype = np.float64)

            if self.reparam:
                alpha_lst=copy.deepcopy(alpha_lst)
                for idx, alpha_mtrx in enumerate(alpha_lst):
                    alpha_lst[idx]= np.array((alpha_mtrx[0, :], np.exp(alpha_mtrx[1, :])))

            if kf_vec is None:
                (kf_vec_local, _)=self.__get_ks()
            else:
                kf_vec_local=kf_vec

            if self.reparam:
                kf_vec_local=np.exp(kf_vec_local)

            jdx_start=0
            idx_start=0
            for (idx, rxn_data) in enumerate(self.data):

                alpha_mtrx=alpha_lst[idx]

                if idx != rxn_idx:
                    idx_start += alpha_mtrx.shape[1]
                    jdx_start += alpha_mtrx.shape[1]
                    continue

                reactants_ids=alpha_mtrx[0, :].astype(int)

                reactants_molar_cc=spc_molar_cc_vec[reactants_ids]

                spc_cc_power_prod=np.prod(reactants_molar_cc**alpha_mtrx[1, :])

                rf_i=kf_vec_local[idx] * spc_cc_power_prod

                min_c_j=reactants_molar_cc.min()
                if min_c_j <= 1e-25:
                    (jdx, )=np.where(reactants_molar_cc == min_c_j)
                    reactants_molar_cc[jdx]=1.0  # any non-zero value will do since rb_i will be zero

                for (Jdx, c_J) in enumerate(reactants_molar_cc):
                    for (jdx, c_j) in enumerate(reactants_molar_cc):

                        if self.reparam:
                            d_alpha_d_alpha_ri_mtrx[idx_start +Jdx, jdx_start +jdx] = math.log(c_J) * math.log(c_j) * alpha_mtrx[1, Jdx] * alpha_mtrx[1, jdx] * rf_i
                        else:
                            d_alpha_d_alpha_ri_mtrx[idx_start + Jdx, jdx_start + jdx]= math.log(c_J) * math.log(c_j) * rf_i

                idx_start += alpha_mtrx.shape[1]
                jdx_start += alpha_mtrx.shape[1]

        # --------------------------------
        # partial_beta(partial_alpha r_i)
        # --------------------------------
        if alpha_lst is not None and beta_lst is not None:

            n_alphas=0
            for alpha_mtrx in alpha_lst:
                n_alphas += alpha_mtrx.shape[1]

            n_betas=0
            for beta_mtrx in beta_lst:
                n_betas += beta_mtrx.shape[1]

            d_beta_d_alpha_ri_mtrx= np.zeros((n_alphas, n_betas), dtype = np.float64)

        # *******************************************************************************************
        # 4th row block

        # ---------------------------------
        # partial_beta(partial_beta r_i)
        # ---------------------------------
        if beta_lst is not None:

            n_betas=0
            for beta_mtrx in beta_lst:
                n_betas += beta_mtrx.shape[1]

            d_beta_d_beta_ri_mtrx = np.zeros((n_betas, n_betas), dtype = np.float64)

            if self.reparam:
                beta_lst=copy.deepcopy(beta_lst)
                for idx, beta_mtrx in enumerate(beta_lst):
                    beta_lst[idx]= np.array((beta_mtrx[0, :], np.exp(beta_mtrx[1, :])))

            if kb_vec is None:
                (_, kb_vec_local)=self.__get_ks()
            else:
                kb_vec_local=kb_vec

            if self.reparam:
                kb_vec_local=np.exp(kb_vec_local)

            jdx_start=0
            idx_start=0
            for (idx, rxn_data) in enumerate(self.data):

                beta_mtrx=beta_lst[idx]

                if idx != rxn_idx:
                    idx_start += beta_mtrx.shape[1]
                    jdx_start += beta_mtrx.shape[1]
                    continue

                products_ids=beta_mtrx[0, :].astype(int)

                products_molar_cc=spc_molar_cc_vec[products_ids]

                spc_cc_power_prod=np.prod(products_molar_cc**beta_mtrx[1, :])

                rb_i=- kb_vec_local[idx] * spc_cc_power_prod

                min_c_j=products_molar_cc.min()
                if min_c_j <= 1e-25:
                    (jdx, )=np.where(products_molar_cc == min_c_j)
                    products_molar_cc[jdx]=1.0  # any non-zero value will do since rb_i will be zero

                for (Jdx, c_J) in enumerate(products_molar_cc):
                    for (jdx, c_j) in enumerate(products_molar_cc):

                        if self.reparam:
                            d_beta_d_beta_ri_mtrx[idx_start +Jdx, jdx_start +jdx] = math.log(c_J) * math.log(c_j) * beta_mtrx[1, Jdx] * beta_mtrx[1, jdx] * rb_i
                        else:
                            d_beta_d_beta_ri_mtrx[idx_start + Jdx, jdx_start + jdx]= math.log(c_J) * math.log(c_j) * rb_i

                idx_start += beta_mtrx.shape[1]
                jdx_start += beta_mtrx.shape[1]

        # *******************************************************************************************
        # Assembly

        # General case
        if kf_vec is not None and kb_vec is not None and alpha_lst is not None and beta_lst is not None:

            hessian_ri_1st_row=np.hstack(
                [d_kf_d_kf_ri_mtrx, d_kb_d_kf_ri_mtrx, d_alpha_d_kf_ri_mtrx, d_beta_d_kf_ri_mtrx])

            hessian_ri_2nd_row=np.hstack([d_kb_d_kf_ri_mtrx.transpose(
            ), d_kb_d_kb_ri_mtrx, d_alpha_d_kb_ri_mtrx, d_beta_d_kb_ri_mtrx])

            hessian_ri_3rd_row=np.hstack([d_alpha_d_kf_ri_mtrx.transpose(
            ), d_alpha_d_kb_ri_mtrx.transpose(), d_alpha_d_alpha_ri_mtrx, d_beta_d_alpha_ri_mtrx])

            hessian_ri_4th_row=np.hstack([d_beta_d_kf_ri_mtrx.transpose(), d_beta_d_kb_ri_mtrx.transpose(
            ), d_beta_d_alpha_ri_mtrx.transpose(), d_beta_d_beta_ri_mtrx])

            hessian_ri=np.vstack(
                [hessian_ri_1st_row, hessian_ri_2nd_row, hessian_ri_3rd_row, hessian_ri_4th_row])

        # Forward case
        elif kf_vec is not None and alpha_lst is not None and kb_vec is None and beta_lst is None:

            hessian_ri_1st_row=np.hstack(
                [d_kf_d_kf_ri_mtrx, d_alpha_d_kf_ri_mtrx])
            hessian_ri_2nd_row=np.hstack(
                [d_alpha_d_kf_ri_mtrx.transpose(), d_alpha_d_alpha_ri_mtrx])

            hessian_ri=np.vstack([hessian_ri_1st_row, hessian_ri_2nd_row])

        # k's only case
        elif kf_vec is not None and kb_vec is not None and alpha_lst is None and beta_lst is None:

            hessian_ri_1st_row=np.hstack(
                [d_kf_d_kf_ri_mtrx, d_kb_d_kf_ri_mtrx])
            hessian_ri_2nd_row=np.hstack(
                [d_kb_d_kf_ri_mtrx.transpose(), d_kb_d_kb_ri_mtrx])

            hessian_ri=np.vstack([hessian_ri_1st_row, hessian_ri_2nd_row])

        # kfs only case
        elif kf_vec is not None and kb_vec is None and alpha_lst is None and beta_lst is None:

            hessian_ri=d_kf_d_kf_ri_mtrx

        # k's and alphas only case
        elif kf_vec is not None and kb_vec is not None and alpha_lst is not None and beta_lst is None:

            hessian_ri_1st_row=np.hstack(
                [d_kf_d_kf_ri_mtrx, d_kb_d_kf_ri_mtrx, d_alpha_d_kf_ri_mtrx])
            hessian_ri_2nd_row=np.hstack(
                [d_kb_d_kf_ri_mtrx.transpose(), d_kb_d_kb_ri_mtrx, d_alpha_d_kb_ri_mtrx])
            hessian_ri_3rd_row=np.hstack([d_alpha_d_kf_ri_mtrx.transpose(
            ), d_alpha_d_kb_ri_mtrx.transpose(), d_alpha_d_alpha_ri_mtrx])

            hessian_ri=np.vstack(
                [hessian_ri_1st_row, hessian_ri_2nd_row, hessian_ri_3rd_row])

        # alphas only case
        elif kf_vec is None and kb_vec is None and alpha_lst is not None and beta_lst is None:

            hessian_ri=d_alpha_d_alpha_ri_mtrx

        # betas only case
        elif kf_vec is None and kb_vec is None and alpha_lst is None and beta_lst is not None:

            hessian_ri=d_beta_d_beta_ri_mtrx

        # alphas and betas only case
        elif kf_vec is None and kb_vec is None and alpha_lst is not None and beta_lst is not None:

            hessian_ri_1st_row=np.hstack(
                [d_alpha_d_alpha_ri_mtrx, d_beta_d_alpha_ri_mtrx])
            hessian_ri_2nd_row=np.hstack(
                [d_beta_d_alpha_ri_mtrx.transpose(), d_beta_d_beta_ri_mtrx])

            hessian_ri=np.vstack([hessian_ri_1st_row, hessian_ri_2nd_row])

        # kfs and betas only case
        elif kf_vec is not None and kb_vec is None and alpha_lst is None and beta_lst is not None:

            hessian_ri_1st_row=np.hstack(
                [d_kf_d_kf_ri_mtrx, d_beta_d_kf_ri_mtrx])
            hessian_ri_2nd_row=np.hstack(
                [d_beta_d_kf_ri_mtrx.transpose(), d_beta_d_beta_ri_mtrx])

            hessian_ri=np.vstack([hessian_ri_1st_row, hessian_ri_2nd_row])

        # kbs and alphas only case
        elif kf_vec is None and kb_vec is not None and alpha_lst is not None and beta_lst is None:

            hessian_ri_1st_row=np.hstack(
                [d_kb_d_kb_ri_mtrx, d_alpha_d_kb_ri_mtrx])
            hessian_ri_2nd_row=np.hstack(
                [d_alpha_d_kb_ri_mtrx.transpose(), d_alpha_d_alpha_ri_mtrx])

            hessian_ri=np.vstack([hessian_ri_1st_row, hessian_ri_2nd_row])

        else:
            assert False, 'Hessian ri case not implemented.'

        return hessian_ri

    def __get_kf(self):
        '''Utility for returning a packed kf vector.

        Should this return the stoichiometric coefficients in case there is no data in `self.data`?

        Returns
        -------
        kf_vec: numpy.ndarray
        '''

        kf_vec= np.zeros(len(self.reactions), dtype = np.float64)

        for idx, rxn_data in enumerate(self.data):
            kf_vec[idx]=rxn_data['k_f']

        return kf_vec
    def __set_kf(self, kf_vec):
        '''Utility for setting kf from packed vectors.

        Parameters
        ----------
        kf_vec: numpy.ndarray

        Returns
        -------
        '''

        assert isinstance(kf_vec, numpy.ndarray)
        assert kf_vec.size == len(self.reactions)

        for idx, rxn_data in enumerate(self.data):
            rxn_data['k_f']=kf_vec[idx]
    kf=property(__get_kf, __set_kf, None, None)

    def __get_kb(self):
        '''Utility for returning a packed kb vector.

        Should this return the stoichiometric coefficients in case there is no data in `self.data`?

        Returns
        -------
        kb_vec: numpy.ndarray
        '''

        kb_vec= np.zeros(len(self.reactions), dtype = np.float64)

        for idx, rxn_data in enumerate(self.data):
            kb_vec[idx]=rxn_data['k_b']

        return kb_vec
    def __set_kb(self, kb_vec):
        '''Utility for setting kb from packed vectors.

        Parameters
        ----------
        kb_vec: numpy.ndarray

        Returns
        -------
        '''

        assert isinstance(kb_vec, numpy.ndarray)
        assert kb_vec.size == len(self.reactions)

        for idx, rxn_data in enumerate(self.data):
            rxn_data['k_b']=kb_vec[idx]
    kb=property(__get_kb, __set_kb, None, None)

    def __get_ks(self):
        '''Utility for returning packed kf and kb into vectors.

        Should this return the stoichiometric coefficients in case there is no data in `self.data`?

        Returns
        -------
        (kf_vec, kb_vec): tuple(numpy.ndarray, numpy.ndarray)
        '''

        return (self.__get_kf(), self.__get_kb())
    def __set_ks(self, kf_kb_pair):
        '''Utility for setting kf and kb from packed vectors.

        Parameters
        ----------
        kf_kb_pair: tuple(numpy.ndarray, numpy.ndarray)
            If any element of the tuple is None, the corresponding data is not updated.

        Returns
        -------
        '''

        assert isinstance(kf_kb_pair, tuple)
        assert len(kf_kb_pair) == 2

        if kf_kb_pair[0] is not None:
            self.__set_kf(kf_kb_pair[0])
        if kf_kb_pair[1] is not None:
            self.__set_kb(kf_kb_pair[1])
    ks=property(__get_ks, __set_ks, None, None)

    def __get_power_law_exponents(self):
        '''Utility for packing alpha and beta exponents into a list of vectors.

        The return from this method is a pair of unstructured data since each reaction typically has
        a different number of species, hence different number of associated power-law exponents.
        The ids of the active species are passed in the first row of the matrices. Each of the alpha
        and beta matrices have 2 rows. First row with ids, second row with exponents.

        Returns
        -------
        (alpha_lst, beta_lst): tuple(list(numpy.ndarray), list(numpy.ndarray))
        '''
        alpha_lst=list()  # list of matrices
        beta_lst=list()  # list of vectors

        for (idx, rxn_data) in enumerate(self.data):

            (reactants_ids, )=np.where(self.stoic_mtrx[idx, :] < 0)
            # reactants_ids = reactants_ids_lst[idx]

            if 'alpha' in rxn_data.keys():
                alpha_dict=rxn_data['alpha']
                exponents=list()
                active_reactants_ids=list()
                for j in reactants_ids:
                    spc_name=self.species_names[j]
                    alpha=alpha_dict[spc_name]
                    if alpha != -9999:  # exclude inactive species
                        active_reactants_ids.append(j)
                        exponents.append(alpha_dict[spc_name])

                reactants_ids_alphas=np.array((active_reactants_ids, exponents))  # 2-row matrix

            else:
                assert False
                exponents=-self.stoic_mtrx[idx, reactants_ids]

            alpha_lst.append(reactants_ids_alphas)

            (products_ids, )=np.where(self.stoic_mtrx[idx, :] > 0)

            if 'beta' in rxn_data.keys():
                beta_dict=rxn_data['beta']
                exponents=list()
                active_products_ids=list()
                for j in products_ids:
                    spc_name=self.species_names[j]
                    beta=beta_dict[spc_name]
                    if beta != -9999:  # exclude inactive species
                        active_products_ids.append(j)
                        exponents.append(beta_dict[spc_name])

                products_ids_betas=np.array((active_products_ids, exponents))  # 2-row matrix

            else:
                assert False
                exponents=self.stoic_mtrx[idx, products_ids]

            beta_lst.append(products_ids_betas)

        return (alpha_lst, beta_lst)
    def __set_power_law_exponents(self, alpha_beta_pair):
        '''Utility for setting alpha and beta from packed vectors.

        The alpha and vector lists of matrices with values for the exponents and corresponding active
        species ids. Note that this will change the internal data of the object including inactive
        species if the user intends to.

        Parameters
        ----------
        alpha_beta_pair: tuple(list(numpy.ndarray), list(numpy.ndarray))
            If any element of the tuple is None, the corresponding data is not updated.

        '''

        assert isinstance(alpha_beta_pair, tuple)
        assert len(alpha_beta_pair) == 2

        if alpha_beta_pair[0] is not None:
            assert isinstance(alpha_beta_pair[0], list)
            alpha_lst=alpha_beta_pair[0]

            for idx, rxn_data in enumerate(self.data):

                if 'alpha' in rxn_data.keys():
                    alpha_dict=rxn_data['alpha']
                    alpha_mtrx=alpha_lst[idx]
                    reactants_ids=alpha_mtrx[0, :].astype(int)
                    exponents=alpha_mtrx[1, :]
                    for jdx, j in enumerate(reactants_ids):
                        spc_name=self.species_names[j]
                        alpha_dict[spc_name]=exponents[jdx]
                else:
                    assert False
                    exponents=-self.stoic_mtrx[idx, reactants_ids]

        if alpha_beta_pair[1] is not None:
            assert isinstance(alpha_beta_pair[1], list)
            beta_lst=alpha_beta_pair[1]

            for idx, rxn_data in enumerate(self.data):

                if 'beta' in rxn_data.keys():
                    beta_dict=rxn_data['beta']
                    beta_mtrx=beta_lst[idx]
                    products_ids=beta_mtrx[0, :].astype(int)
                    exponents=beta_mtrx[1, :]
                    for jdx, j in enumerate(products_ids):
                        spc_name=self.species_names[j]
                        beta_dict[spc_name]=exponents[jdx]
                else:
                    assert False
                    exponents=self.stoic_mtrx[idx, products_ids]
    power_law_exponents=property(
        __get_power_law_exponents, __set_power_law_exponents, None, None)

    def full_rank_sub_mechanisms(self, n_sub_mec = 1000):
        '''Construct sub-mechanisms with full-rank stoichiometric matrix.

        Returns
        -------
        sub_mechanisms: list([ReactionMechanism, gidxs, score])

        '''

        s_rank=np.linalg.matrix_rank(self.stoic_mtrx)

        if s_rank == min(self.stoic_mtrx.shape):
            return self

        m_reactions=self.stoic_mtrx.shape[0]

        n_mechanisms=math.factorial(m_reactions) /\
                       math.factorial(m_reactions - s_rank) /\
                       math.factorial(s_rank)
        # print('# of all possible sub_mechanisms = %i'%n_mechanisms)

        tmp=combinations(range(m_reactions), s_rank)
        reaction_sets=[i for i in tmp]
        random.shuffle(reaction_sets)  # this may be time consuming

        sub_mechanisms=list()  # list of list

        for idxs in reaction_sets:

            stoic_mtrx=self.stoic_mtrx[idxs, :]

            rank=np.linalg.matrix_rank(stoic_mtrx)

            if rank == s_rank:

                mechanism=list()
                for idx in idxs:
                    mechanism.append(self.__original_mechanism[idx])

                rxn_mech = ReactionMechanism(mechanism = mechanism, order_species =True, reparam=self.reparam)

                assert np.linalg.matrix_rank(rxn_mech.stoic_mtrx) == s_rank

                sub_mechanisms.append([rxn_mech, idxs])

            if len(sub_mechanisms) >= n_sub_mec:
                break

        # Count number of times a global reaction appear in a sub-mechanism
        reactions_hits=np.zeros(m_reactions)
        for sm in sub_mechanisms:
            gidxs=list(sm[1])
            reactions_hits[gidxs] += 1

        # Score the global reactions
        sub_mech_reactions_score=list()
        for subm in sub_mechanisms:
            score=0
            for gid in subm[1]:
                score += reactions_hits[gid]
            sub_mech_reactions_score.append(score)

        sub_mech_reactions_score=np.array(sub_mech_reactions_score)
        sub_mech_reactions_score /= sub_mech_reactions_score.max()
        sub_mech_reactions_score *= 10.0

        results=sorted(zip(sub_mechanisms, sub_mech_reactions_score),
                          key=lambda entry: entry[1], reverse=True )

        sub_mechanisms           = [a for (a,b) in results]
        sub_mech_reactions_score = [b for (a,b) in results]

        # Encode score in to sub_mech_reactions mech. list of list
        for (sr, score) in zip(sub_mechanisms, sub_mech_reactions_score):
            sr += [score]

        # max_score = max( [sm[3] for sm in sub_mechanisms] )

        return sub_mechanisms

    def print_data(self):
        '''Helper to print the reaction data line by line.
        '''

        for idx, data in enumerate(self.data):
            print(self.reactions[idx])
            print(data)
            print('')

    def __latex(self):
        '''Internal helper for LaTeX typesetting.

        See attributes.
        '''

        # Latex species
        species_str = str()
        for spc in self.species[:-1]:
            species_str += spc.latex_name + ', '
        species_str += self.species[-1].latex_name

        # Latex reactions into align environment
        rxn_str = self.header + '\n'
        rxn_str += '\\begin{align*} \n'
        for idx,row in enumerate(self.stoic_mtrx):

            (reactants_ids, ) = np.where(row < 0)

            for j in reactants_ids[:-1]:
                coeff = abs(int(self.stoic_mtrx[idx,j]))
                if coeff != 1:
                    rxn_str += str(coeff) + '\,' + self.species[j].latex_name + r'\ + \ '
                else:
                    rxn_str += self.species[j].latex_name + r'\ + \ '

            j = reactants_ids[-1]
            coeff = abs(int(self.stoic_mtrx[idx,j]))
            if coeff != 1:
                rxn_str += str(coeff) + '\,' + self.species[j].latex_name
            else:
                rxn_str += self.species[j].latex_name

            if self.reaction_direction_symbol[idx] == '->':
                rxn_str += r'\ &\longrightarrow \ '
            elif self.reaction_direction_symbol[idx] == '<->':
                rxn_str += r'\ &\longleftrightarrow \ '
            elif self.reaction_direction_symbol[idx] == '<=>':
                rxn_str += r'\ &\longleftrightarrow \ '
            elif self.reaction_direction_symbol[idx] == '<-':
                rxn_str += r'\ &\longleftarrow \ '
            else:
                assert False, 'Unknown reaction direction.'

            (products_ids, ) = np.where(row > 0)
            for j in products_ids[:-1]:
                coeff = abs(int(self.stoic_mtrx[idx,j]))
                if coeff != 1:
                    rxn_str += str(coeff) + '\,' + self.species[j].latex_name + r'\ + \ '
                else:
                    rxn_str += self.species[j].latex_name + r'\ + \ '

            j = products_ids[-1]
            coeff = abs(int(self.stoic_mtrx[idx,j]))
            if coeff != 1:
                rxn_str += str(coeff) + '\,' + self.species[j].latex_name + '\\\\ \n'
            else:
                rxn_str += self.species[j].latex_name + '\\\\ \n'

        rxn_str += '\\end{align*} \n'

        return (species_str, rxn_str)

    def __str__(self):
        s = '\n\t **ReactionMechanism()**:' + \
            '\n\t header: %s;' + \
            '\n\t reactions: %s;' + \
            '\n\t data: %s;' + \
            '\n\t species_names: %s;' + \
            '\n\t species: %s' + \
            '\n\t max mass balance residual: %s'
        return s % (self.header,
                    self.reactions,
                    self.data,
                    self.species_names,
                    self.species,
                    str(self.max_mass_balance_residual()))
    def __repr__(self):
        s = '\n\t **ReactionMechanism()**:' + \
            '\n\t header: %s;' + \
            '\n\t reactions: %s;' + \
            '\n\t data: %s;' + \
            '\n\t species_names: %s;' + \
            '\n\t species: %s;' + \
            '\n\t max mass balance residual: %s'
        return s % (self.header,
                    self.reactions,
                    self.data,
                    self.species_names,
                    self.species,
                    str(self.max_mass_balance_residual()))

def print_reaction_sub_mechanisms(sub_mechanisms, mode=None, n_sub_mech=None):
    '''
    Nice printout of a scored reaction sub-mechanism list

    Once the sub-mechanisms have been computed this function makes a printout.
    Note: This is not a class method; just a helper function to the ReactionMechanism class.

    Parameters
    ----------
    sub_mechanisms: list([ReactionMechanism, gidxs, score])
        Sorted reaction mechanims in the form of a list.

    mode: str
        Printing mode: all, top, None.

    Returns
    -------
    None:

    Examples
    --------

    '''
    assert mode is None or n_sub_mech is None
    assert mode =='top' or mode =='all' or mode==None
    assert isinstance(n_sub_mech, int) or n_sub_mech is None

    if mode is None and n_sub_mech is None:
        mode = 'all'

    if n_sub_mech is None:
        if mode == 'all':
            n_sub_mech = len(sub_mechanisms)
        elif mode == 'top':
            scores = [sm[2] for sm in sub_mechanisms]
            max_score = max(scores)
            tmp = list()
            for s in scores:
                if s == max_score:
                    tmp.append(s)
            n_sub_mech = len(tmp)
        else:
            assert False, 'illegal mode %r'%mode

    for idx, rsm in enumerate(sub_mechanisms[:n_sub_mech]):
        print('Full-Rank Reaction Sub Mechanism: %s (score %4.2f)'%(idx, rsm[2]))
        print('Species = ',rsm[0].species_names)
        for (r,data,gidx) in zip(rsm[0].reactions, rsm[0].data, rsm[1]):
            print('r%s'%gidx, r,' ', data['info'])

    return
