#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
'''
Suupport class for working with chemical reactions.
'''
import math
import numpy       # used in asserts
import numpy as np

from cortix.support.species import Species

class ReactionMechanism:
    """Chemical reaction mechanism.
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
        reaction rate constants  per reaction.
        E.g.: self.data[idx]['alpha'] = {'e^-': 1e7, 'NO3': 15}
              self.data[idx]['k_f'] = 1e3

    stoic_mtrx: numpy.ndarray
        Stoichiometric matrix; 2D `numpy` array.

    latex_species: str
        String containing the LaTeX typetting of the species in the order they appear in the stoichiometric
        matrix. Use the Python print function to print this attribute and copy/paste into a LaTex
        environment.

    latex_rxn: str
        String containing the LaTeX typsetting of all reactions into the LaTeX `align` environment.
    """

    def __init__(self, header='no-header', file_name=None, mechanism=None, order_species=True):
        """Module class constructor.

        Returns data structures for a reaction mechanism. Namely, species list,
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
              Full path file name of the reaction mechanism file. If the reaction has an
              equilibrium constant it will follow the reaction separated by a colon.

        mechanism: list(str)
              List of reaction strings per above convention.

        order_species: bool
              Alphabetically order the species names in the mechanism.

        Examples
        --------

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

            if len(data) > 1: # if colon separated data exists

                for d in data[1:]:
                    datum = d.strip()

                    name = datum.split('=')[0].strip()
                    val_str = datum.split('=')[1].strip()

                    # alpha and beta names are reserved for the exponents of the reaction rate law
                    # alpha and beta cases; convert tuple of integers into dictionary
                    if name == 'alpha' or name == 'beta':
                        assert '(' in val_str and ')' in val_str
                        alpha_or_beta = val_str[1:-1] # ignore ( and )
                        alpha_or_beta_dict = dict()
                        i = 0
                        for s in alpha_or_beta.split(','):
                            alpha_or_beta_dict[i] = float(s.strip())
                            i += 1
                        tmp_dict[name] = alpha_or_beta_dict
                    # any other colon separated data
                    else:
                        tmp_dict[name] = float(val_str)

            self.data.append(tmp_dict)

        # find species

        species_tmp = list()  # temporary list for species

        for idx, rxn in enumerate(self.reactions):

            # the order of the following test matters; test reversible reaction first
            tmp = rxn.split('<=>')
            n_terms = len(tmp)
            assert n_terms == 1 or n_terms == 2

            if n_terms == 1: # if no previous split
                tmp = rxn.split('<->')
                n_terms = len(tmp)
                assert n_terms == 1 or n_terms == 2
                if n_terms == 1: # if no previous split
                    tmp = rxn.split('->')
                    n_terms = len(tmp)
                    assert n_terms == 1 or n_terms == 2
                    if n_terms == 1: # if no previous split
                        tmp = rxn.split('<-')
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
                           (i_row, r, species_member, s_mtrx[i_row, j_col])
                    s_mtrx[i_row,j_col] = -1.0 * coeff
                else:
                    species_member = tmp[0].strip()
                    j_col = self.species_names.index(species_member)
                    assert s_mtrx[i_row,j_col] == 0.0, \
                           'duplicates not allowed r%r: %r %r %r'%\
                           (i_row, r, species_member, s_mtrx[i_row, j_col])
                    s_mtrx[i_row,j_col] = -1.0

                if 'alpha' in self.data[i_row].keys():
                    species_name = self.species_names[j_col]
                    assert len(self.data[i_row]['alpha']) == len(left_terms), 'Incorrect length of alpha.'
                    # replace species index with name
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

                if 'beta' in self.data[i_row].keys():
                    species_name = self.species_names[j_col]
                    assert len(self.data[i_row]['beta']) == len(right_terms), 'Incorrect length of beta.'
                    # replace species index with name
                    self.data[i_row]['beta'][species_name] = self.data[i_row]['beta'].pop(right_terms.index(t))

        self.stoic_mtrx = s_mtrx

        (self.latex_species, self.latex_rxn) = self.__latex()

        # Fill-in missing k_f, k_b, alpha, and beta
        for idx,dat in enumerate(self.data):
            if 'k_f' not in dat.keys():
                dat['k_f'] = 0.0
            if 'k_b' not in dat.keys():
                dat['k_b'] = 0.0
            if 'alpha' not in dat.keys():
                (reactants_ids, ) = np.where(self.stoic_mtrx[idx, :] < 0)
                tmp = dict()
                for j in reactants_ids:
                    spc_name = self.species_names[j]
                    tmp[spc_name] = abs(self.stoic_mtrx[idx,j])
                dat['alpha'] = tmp
            if 'beta' not in dat.keys():
                (products_ids, ) = np.where(self.stoic_mtrx[idx, :] > 0)
                tmp = dict()
                for j in products_ids:
                    spc_name = self.species_names[j]
                    tmp[spc_name] = abs(self.stoic_mtrx[idx,j])
                dat['beta'] = tmp

    def mass_balance_residuals(self):
        """Reaction mass balance residual vector.

        Returns
        -------

        mb_residual_vec: numpy.ndarray
            1D vector of mass balance residuals for each reaction.
        """

        m_vec = np.zeros(len(self.species), dtype=np.float64)

        for idx, spc in enumerate(self.species):
            m_vec[idx] = spc.molar_mass

        assert np.prod(m_vec) > 0.0

        mb_residual_vec = self.stoic_mtrx @ m_vec

        return mb_residual_vec

    def max_mass_balance_residual(self):
        """Compute the maximum magnitude reaction mass balance residual.

        Returns
        -------

        max(abs(mb): float

        """

        mb_residual_vec = self.mass_balance_residuals()

        return np.max(np.abs(mb_residual_vec))

    def is_mass_conserved(self, tol=1e-10):
        """Check mass conservation if species have a molar mass value.

        Returns
        -------

        bool

        """

        residual = self.max_mass_balance_residual()

        return True if residual < tol else False

    def rank_analysis(self, verbose=False, tol=1e-8):
        """Compute the rank of the stoichiometric matrix.

        This will establish rank deficiency.

        Parameters
        ----------

        verbose: bool
        tol: float

        Returns
        -------

        rank: int
        """

        #assert self.is_mass_conserved(tol), 'fatal: mass conservation failed'

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
        """Compute the reaction rate density vector.

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
        List of alpha power-law exponents as a vector ordered in the order of appearance of reactants
        in the corresponding reaction. If not provided, it will be assembled internally.

        beta_lst: list(numpy.ndarray)
        List of beta power-law exponents as a vector ordered in the order of appearance of products
        in the corresponding reaction. If not provided, it will be assembled internally.
        """
        assert isinstance(spc_molar_cc_vec, numpy.ndarray), 'type(spc_molar_cc_vec) = %r'%(type(spc_molar_cc_vec))
        assert spc_molar_cc_vec.size == len(self.species)

        if kf_vec is not None:
            assert isinstance(kf_vec, np.ndarray)
            assert kf_vec.size == len(self.reactions)

        if kb_vec is not None:
            assert isinstance(kb_vec, np.ndarray), 'type(kb_vec)=%r'%(type(kb_vec))
            assert kb_vec.size == len(self.reactions)

        if alpha_lst is not None:
            assert isinstance(alpha_lst, list)
            assert len(alpha_lst) == len(self.reactions), '# reactions=%r alpha_lst=\n%r'%(len(self.reactions),alpha_lst)
            assert isinstance(alpha_lst[0], np.ndarray)
            for alpha_vec in alpha_lst:
                assert np.all(alpha_vec>=0), 'alpha_vec = \n%r'%alpha_vec

        if beta_lst is not None:
            assert isinstance(beta_lst, list)
            assert len(beta_lst) == len(self.reactions)
            assert isinstance(beta_lst[0], np.ndarray)
            for beta_vec in beta_lst:
                assert np.all(beta_vec>=0)

        # Compute the reaction rate density vector
        r_vec = np.zeros(len(self.reactions), dtype=np.float64)

        for (idx, rxn_data) in enumerate(self.data):

            (reactants_ids, ) = np.where(self.stoic_mtrx[idx, :] < 0)

            reactants_molar_cc = spc_molar_cc_vec[reactants_ids] # must be oredered as in rxn_mech

            if kf_vec is not None:
                kf_i = kf_vec[idx]
            else:
                kf_i = rxn_data['k_f']

            if alpha_lst is not None:
                alpha_vec = alpha_lst[idx]
            else:
                alpha_lst_local = list()
                for jdx in reactants_ids:
                    alpha_lst_local.append(rxn_data['alpha'][self.species_names[jdx]])
                alpha_vec = np.array(alpha_lst_local)

            r_vec[idx] = kf_i * np.prod(reactants_molar_cc**alpha_vec)

        for (idx, rxn_data) in enumerate(self.data):

            (products_ids, ) = np.where(self.stoic_mtrx[idx, :] > 0)

            products_molar_cc = spc_molar_cc_vec[products_ids] # must be oredered as in rxn_mech

            if kb_vec is not None:
                kb_i = kb_vec[idx]
            else:
                kb_i = rxn_data['k_b']

            if beta_lst is not None:
               beta_vec = beta_lst[idx]
            else:
                beta_lst_local = list()
                for jdx in products_ids:
                    beta_lst_local.append(rxn_data['beta'][self.species_names[jdx]])
                beta_vec = np.array(beta_lst_local)

            r_vec[idx] -= kb_i * np.prod(products_molar_cc**beta_vec)

        return r_vec

    def rxn_rate_law(self, spc_molar_cc_vec, kf_vec=None, kb_vec=None, alpha_lst=None, beta_lst=None):
        """See r_vec.
        """

        return self.r_vec(spc_molar_cc_vec, kf_vec, kb_vec, alpha_lst, beta_lst)

    def g_vec(self, spc_molar_cc_vec, kf_vec=None, kb_vec=None, alpha_lst=None, beta_lst=None):
        """Compute the species production rate density vector.

        Parameters:
        -----------
        """

        g_vec = self.stoic_mtrx.transpose() @ self.r_vec(spc_molar_cc_vec, kf_vec, kb_vec, alpha_lst, beta_lst)

        return g_vec

    def species_prod_rate_dens(self, spc_molar_cc_vec, kf_vec=None, kb_vec=None, alpha_lst=None, beta_lst=None):
        """Compute the species production rate density vector.

        Parameters:
        -----------
        """

        return self.g_vec(spc_molar_cc_vec, kf_vec, kb_vec, alpha_lst, beta_lst)

    def drdtheta_mtrx(self, spc_molar_cc_vec, kf_vec=None, kb_vec=None, alpha_lst=None, beta_lst=None):
        """Partial derivative of the reaction rate law wrt parameters.

        The parameters in the derivative are ordered as: k_fs, k_bs, alphas, betas.
        """

        assert isinstance(spc_molar_cc_vec, np.ndarray)
        assert spc_molar_cc_vec.size == len(self.species)
        assert np.all(spc_molar_cc_vec>=0), 'spc_molar_cc_vec =\n%r'%spc_molar_cc_vec

        # Partial r_vec partial kf matrix
        if kf_vec is not None:

            dr_dk_f = np.zeros((len(self.reactions),len(self.reactions)), dtype=np.float64)

            for (idx, rxn_data) in enumerate(self.data):

                (reactants_ids, ) = np.where(self.stoic_mtrx[idx, :] < 0)

                reactants_molar_cc = spc_molar_cc_vec[reactants_ids]
                assert reactants_molar_cc.size == alpha_lst[idx].size

                spc_cc_power_prod = np.prod(reactants_molar_cc**alpha_lst[idx])

                dr_dk_f[idx, idx] = spc_cc_power_prod

            try:
                drdtheta_mtrx = np.hstack([drdtheta_mtrx, dr_dk_f])
            except NameError:
                drdtheta_mtrx = np.hstack([dr_dk_f])

        # Partial r_vec partial kb matrix
        if kb_vec is not None:

            dr_dk_b = np.zeros((len(self.reactions),len(self.reactions)), dtype=np.float64)

            for idx, rxn_data in enumerate(self.data):

                (products_ids, ) = np.where(self.stoic_mtrx[idx, :] > 0)

                products_molar_cc = spc_molar_cc_vec[products_ids]

                spc_cc_power_prod = np.prod(products_molar_cc**beta_lst[idx])

                dr_dk_b[idx, idx] = - spc_cc_power_prod

            try:
                drdtheta_mtrx = np.hstack([drdtheta_mtrx, dr_dk_b])
            except NameError:
                drdtheta_mtrx = np.hstack([dr_dk_b])

        # Partial r_vec partial alpha
        if alpha_lst is not None:
            n_alphas = 0
            for alpha_vec in alpha_lst:
                assert np.all(alpha_vec>=0), 'alpha_vec =\%r'%alpha_vec
                n_alphas += alpha_vec.size

            dr_dalpha = np.zeros((len(self.reactions),n_alphas), dtype=np.float64)


            dr_dalpha_j0 = 0
            for (idx, rxn_data) in enumerate(self.data):

                (reactants_ids, ) = np.where(self.stoic_mtrx[idx, :] < 0)

                reactants_molar_cc = spc_molar_cc_vec[reactants_ids]
                assert reactants_molar_cc.size == alpha_lst[idx].size

                spc_cc_power_prod = np.prod(reactants_molar_cc**alpha_lst[idx])

                rf_i = kf_vec[idx] * spc_cc_power_prod

                min_c_j = reactants_molar_cc.min()
                if min_c_j <= 1e-8:
                    #print('min_c_j=',min_c_j)
                    (jdx, ) = np.where(reactants_molar_cc == min_c_j)
                    reactants_molar_cc[jdx] = 1.0 # any non-zero value will do since rb_i will be zero

                for (jdx, c_j) in enumerate(reactants_molar_cc):
                    dr_dalpha[idx, dr_dalpha_j0+jdx] = math.log(c_j) * rf_i
                    #dr_dalpha[idx, jdx] = math.log(c_j) * rf_i

                dr_dalpha_j0 += alpha_lst[idx].size

            assert dr_dalpha_j0 == n_alphas, 'n_alphas = %r; sum = %r'%(n_alphas, dr_dalpha_j0 )

            try:
                drdtheta_mtrx = np.hstack([drdtheta_mtrx, dr_dalpha])
            except NameError:
                drdtheta_mtrx = np.hstack([dr_dalpha])

        #print(' ')
        #print('begin here')
        # Partial r_vec partial beta
        if beta_lst is not None:
            n_betas = 0
            for beta_vec in beta_lst:
                assert np.all(beta_vec>=0)
                n_betas += beta_vec.size

            dr_dbeta = np.zeros((len(self.reactions),n_betas), dtype=np.float64)

            dr_dbeta_j0 = 0
            for idx, rxn_data in enumerate(self.data):
                #print('idx=',idx)

                (products_ids, ) = np.where(self.stoic_mtrx[idx, :] > 0)

                products_molar_cc = spc_molar_cc_vec[products_ids]
                #print('            products_molar_cc =',products_molar_cc)

                spc_cc_power_prod = np.prod(products_molar_cc**beta_lst[idx])

                rb_i = kb_vec[idx] * spc_cc_power_prod
                #print('            rb_i =',rb_i)
                #print('            kb_vec[idx] = ',kb_vec[idx])

                min_c_j = products_molar_cc.min()
                if min_c_j <= 1e-8:
                    #print('min_c_j=',min_c_j)
                    (jdx, ) = np.where(products_molar_cc == min_c_j)
                    products_molar_cc[jdx] = 1.0 # any non-zero value will do it since rb_i will be zero

                for (jdx, c_j) in enumerate(products_molar_cc):
                    dr_dbeta[idx, dr_dbeta_j0+jdx] = - math.log(c_j) * rb_i
                    #dr_dbeta[idx, jdx] = - math.log(c_j) * rb_i

                dr_dbeta_j0 += beta_lst[idx].size

                #if abs(rb_i) <= 1e-8:
                #    print('')
                #    print('jdx =',jdx, ' dr_dbeta[idx,jdx]=', dr_dbeta[idx,jdx])
                #    print('c_j=',c_j,' rb_i = ',rb_i)
                #    print('products_molar_cc =', products_molar_cc)

            assert dr_dbeta_j0 == n_betas, 'n_betas = %r sum = %r'%(n_betas, dr_dbeta_j0)

            try:
                drdtheta_mtrx = np.hstack([drdtheta_mtrx, dr_dbeta])
            except NameError:
                drdtheta_mtrx = np.hstack([dr_dbeta])

            #print('')
            #print('spc_molar_cc_vec =',spc_molar_cc_vec)
            #print('dr_dalpha=\n',dr_dalpha)
            #np.set_printoptions(precision=5, linewidth=300)
            #print('dr_dbeta =\n',dr_dbeta)

        #drdtheta_mtrx = np.hstack([dr_dk_f, dr_dk_b, dr_dalpha, dr_dbeta])

        return drdtheta_mtrx

    def __get_ks(self):
        """Utility for returning packed kf and kb into vectors.

        Returns
        -------
        (kf_vec, kb_vec): tuple(numpy.ndarray, numpy.ndarray)
        """

        # k's
        kf_vec = np.zeros(len(self.reactions), dtype=np.float64)
        kb_vec = np.zeros(len(self.reactions), dtype=np.float64)

        for idx, rxn_data in enumerate(self.data):
            kf_vec[idx] = rxn_data['k_f']
            kb_vec[idx] = rxn_data['k_b']

        return (kf_vec, kb_vec)
    def __set_ks(self, pair):
        """Utility for setting kf and kb from packed vectors.

        Parameters
        ----------
        kf_kb_pair: tuple(numpy.ndarray, numpy.ndarray)

        Returns
        -------
        """

        assert isinstance(pair, tuple)
        assert len(pair) == 2

        if pair[0] is not None:
            assert isinstance(pair[0], numpy.ndarray)
            assert pair[0].size == len(self.reactions)
            for idx, rxn_data in enumerate(self.data):
                rxn_data['k_f'] = pair[0][idx]
        if pair[1] is not None:
            assert isinstance(pair[1], numpy.ndarray)
            assert pair[1].size == len(self.reactions)
            for idx, rxn_data in enumerate(self.data):
                rxn_data['k_b'] = pair[1][idx]
    ks = property(__get_ks, __set_ks, None, None)

    def __get_power_law_exponents(self):
        """Utility for packing alpha and beta exponents into a list of vectors.

        This must be a pair of unstructured data since each reactor has different number of species and
        different number of associated power-law exponents.

        Returns
        -------
        (alpha_lst, beta_lst): tuple(list(numpy.ndarray), list(numpy.ndarray))
        """
        alpha_lst = list() # list of vectors
        beta_lst  = list() # list of vectors

        for (idx, rxn_data) in enumerate(self.data):

            (reactants_ids, ) = np.where(self.stoic_mtrx[idx, :] < 0)

            if 'alpha' in rxn_data.keys():
                alpha = rxn_data['alpha']
                exponents = list()
                for j in reactants_ids:
                    spc_name = self.species_names[j]
                    exponents.append(alpha[spc_name])
                exponents = np.array(exponents)
            else:
                exponents = -self.stoic_mtrx[idx, reactants_ids]

            alpha_lst.append(exponents)

            (products_ids, ) = np.where(self.stoic_mtrx[idx, :] > 0)

            if 'beta' in rxn_data.keys():
                beta = rxn_data['beta']
                exponents = list()
                for j in products_ids:
                    spc_name = self.species_names[j]
                    exponents.append(beta[spc_name])
                exponents = np.array(exponents)
            else:
                exponents = self.stoic_mtrx[idx, products_ids]

            beta_lst.append(exponents)

        return (alpha_lst, beta_lst)
    def __set_power_law_exponents(self, pair):
        """Utility for setting alpha and beta from packed vectors.

        The alpha and vector list of vectors must be ordered both in reactions and reactants and products. 
        """

        assert isinstance(pair, tuple)
        assert len(pair) == 2

        if pair[0] is not None:
            assert isinstance(pair[0], list)
            alpha_lst = pair[0]

            for idx, rxn_data in enumerate(self.data):

                (reactants_ids, ) = np.where(self.stoic_mtrx[idx, :] < 0)

                if 'alpha' in rxn_data.keys():
                    alpha = rxn_data['alpha']
                    exponents = alpha_lst[idx]
                    for jdx,j in enumerate(reactants_ids):
                        spc_name = self.species_names[j]
                        alpha[spc_name] = exponents[jdx]
                else:
                    exponents = -self.stoic_mtrx[idx, reactants_ids]

        if pair[1] is not None:
            assert isinstance(pair[1], list)
            beta_lst = pair[1]

            for idx, rxn_data in enumerate(self.data):

                (products_ids, ) = np.where(self.stoic_mtrx[idx, :] > 0)

                if 'beta' in rxn_data.keys():
                    beta = rxn_data['beta']
                    exponents = tuple(beta_lst[idx])
                    for jdx,j in enumerate(products_ids):
                        spc_name = self.species_names[j]
                        beta[spc_name] = exponents[jdx]
                else:
                    exponents = self.stoic_mtrx[idx, products_ids]
    power_law_exponents = property(__get_power_law_exponents, __set_power_law_exponents, None, None)

    def print_data(self):
        """Helper to print the reaction data line by line.
        """

        for idx, data in enumerate(self.data):
            print(self.reactions[idx], ' ', data)

    def __latex(self):
        """Internal helper for LaTeX typesetting.

        See attributes.
        """

        # Latex species
        species_str = str()
        for spc in self.species[:-1]:
            species_str += spc.latex_name + ', '
        species_str += self.species[-1].latex_name

        # Latex reactions into align environment
        rxn_str = self.header + '\n'
        rxn_str += '\\begin{align*} \n'
        for row in self.stoic_mtrx:

            (reactants_ids, ) = np.where(row < 0)
            for j in reactants_ids[:-1]:
                rxn_str += self.species[j].latex_name + r'\ + \ '

            rxn_str += self.species[reactants_ids[-1]].latex_name

            rxn_str += r'\ &\rightarrow \ '

            (products_ids, ) = np.where(row > 0)
            for j in products_ids[:-1]:
                rxn_str += self.species[j].latex_name + r'\ + \ '

            rxn_str += self.species[products_ids[-1]].latex_name + '\\\\ \n'

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
