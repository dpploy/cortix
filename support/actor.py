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
This is a simple way to hide the name of species of interest in a simulation.
The user would modify and copy this class into the Cortix module of interest
and keep it private.
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda
Sat Aug 15 13:41:12 EDT 2015
'''
#*********************************************************************************
import os
import sys
#*********************************************************************************

class Actor():
    '''
    See atoms list in Specie.
    '''

#*********************************************************************************
# Construction
#*********************************************************************************

    def __init__( self, name ):

        assert isinstance(name, str)

        # ** this is the section to be modified by the user of this class **
        self.__name_atoms_formula = {
              'water16'   : [['2*H-1','O-16'],'H2O'],
              'spc(v)'    : [['2*O-16'],'O2'],
              'spc1(v)'   : [['O-16'],'O'],
              'spc2(v)'   : [['Xe-136'],'Xe'],
              'spc3(v)'   : [['I-127'],'I'],
               }

        # ** do not modify beyond this point **

        assert name in self.__name_atoms_formula.keys(), 'name %r not valid.' % name

        self.__atoms = self.__name_atoms_formula[name][0]

        formula = self.__name_atoms_formula[name][1]
        assert isinstance(formula, str), 'formula %r not valid.' % formula
        self.__formula = formula

        return

#*********************************************************************************
# Public member functions
#*********************************************************************************

    def __get_atoms(self):
        '''
        Returns the specific nuclides found in the specified chemical.

        Parameters
        ----------
        empty:

        Returns
        -------
        atoms: list(str)
        '''

        return self.__atoms
    atoms = property(__get_atoms, None, None, None)

    def __get_formula(self):
        '''
        Returns the formula of the chemical in question.

        Parameters
        ----------
        empty:

        Returns
        -------
        formula: str
        '''

        return self.__formula
    formula = property(__get_formula, None, None, None)

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

#======================= end class Actor =========================================
