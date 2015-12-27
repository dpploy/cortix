#!/usr/bin/env python
"""
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

This Actor class is to be used with other classes in plant-level process modules.

For unit testing do at the linux command prompt:
    python actor.py

Sat Aug 15 13:41:12 EDT 2015
"""

#*******************************************************************************
import os, sys
#*******************************************************************************

#*******************************************************************************
class Actor():

# Class data
# Symbols can only be either a chemical symbol or an isotope denoted as say, U-238.
# Names can be anything
 symbol = {
       'Koko'      : 'H-3',
       'Owl'       : 'Kr-85',
       'Larry'     : 'Kr-85',
       'Bat'       : 'I-129',
       'Scott'     : 'I-129',
       'Ant'       : 'C-14',
       'Xe'        : 'Xe',
       'Xe-136'    : 'Xe-136',
       'Ru'        : 'Ru',
       'O'         : 'O'      
          }     

 atoms = {
       'Gui'       : ['2*I'],
       'water'     : ['2*H','O'],  
       'O2'        : ['2*O'],
       'Koko'      : ['H'],
       'Owl'      : ['Kr'],
       'Bat'      : ['2*I'],
       'Ant'      : ['C'],
           }
#*******************************************************************************
 def __init__( self ):
     pass


#*******************************************************************************

#*******************************************************************************
# Setters and Getters methods
#-------------------------------------------------------------------------------
# These are passing arguments by value effectively. Because the python objects
# passed into/out of the function are immutable.

#*******************************************************************************
# Internal helpers 

#*******************************************************************************
# Printing of data members
# def __str__( self ):
#     s = ' %5s %5s %5s '+' molar mass: %6s '+' molar cc: %6s '+' mass cc: %6s '+' flag: %s '+'# atoms: %s'+' atoms: %s\n'
#     return s % (self.name, self.formula, self.phase, self.molarMass, self.molarCC, self.massCC, self.flag, self.nAtoms, self.atoms)

# def __repr__( self ):
#     s = ' %5s %5s %5s '+' molar mass: %6s '+' molar cc: %6s '+' mass cc: %6s '+' flag: %s '+'# atoms: %s'+' atoms: %s\n'
#     return s % (self.name, self.formula, self.phase, self.molarMass, self.molarCC, self.massCC, self.flag, self.nAtoms, self.atoms)
#*******************************************************************************
