#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import logging
from ._setuptask import _SetupTask
#*********************************************************************************

#---------------------------------------------------------------------------------
# Execute simulation

def _Execute( self, taskName=None ):

  s = 'start Execute('+taskName+')'
  self.log.debug(s)

  if taskName is not None: 

     _SetupTask( self, taskName )

     for task in self.tasks:
       if task.GetName() == taskName: 

         s = 'called task.Execute() on task ' + taskName
         self.log.debug(s)

         task.Execute( self.application )

  s = 'end Execute('+taskName+')'
  self.log.debug(s)

  return

#*********************************************************************************
