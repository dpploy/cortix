#!/usr/bin/env python
"""
Author: Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import datetime

# constructor helper
from ._cortix import _Cortix
#*********************************************************************************

#*********************************************************************************
class Cortix():

 def __init__( self,
               name = None,
               configFile = 'cortix-config.xml'
             ):

    _Cortix( self, name, configFile )

    return

#---------------------------------------------------------------------------------
# Simulate                  

 def RunSimulations(self, taskName=None):

   for sim in self.simulations: 
       sim.Execute( taskName )
  
   return

#*********************************************************************************
# Unit testing. Usage: -> python cortix.py
if __name__ == "__main__":

  print('Unit testing for Cortix')
  cortix = Cortix("cortix-config.xml")
