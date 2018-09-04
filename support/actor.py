#!/usr/bin/env python
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
This is a simple way to hide the name of species of interest in a simulation.
The user would modify and copy this class into the Cortix module of interest
and keep it private.

Author: Valmor de Almeida dealmeidav@ornl.gov; vfda
Sat Aug 15 13:41:12 EDT 2015
"""
#*******************************************************************************
import os
import sys
#*******************************************************************************

class Actor():
 """
 See atoms list in Specie.
 """

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
#----------------------- end def __init__():--------------------------------------

 def __get_atoms(self):
  return self.__atoms
 atoms = property(__get_atoms, None, None, None)

 def __get_formula(self):
  return self.__formula
 formula = property(__get_formula, None, None, None)

#======================= end class Launcher: =====================================

