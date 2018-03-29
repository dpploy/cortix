"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

An Application object is the composition of Module objects and Network objects.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
import logging
from cortix.utils.configtree import ConfigTree
from cortix.module.interface import Module
#*********************************************************************************

#---------------------------------------------------------------------------------
# Setup modules             

def _SetupModules( self ):

  s = 'start _SetupModules()'
  self.log.debug(s)

  for modNode in self.configNode.get_all_sub_nodes('module'):

     modConfigNode = ConfigTree( modNode )
     assert modConfigNode.get_node_name() == modNode.get('name'), 'check failed'

     newModule = Module( self.workDir, 
                         self.moduLibName, self.moduLibFullParentDir, 
                         modConfigNode )

     # check for a duplicate module before appending a new one
     for module in self.modules:
       modName       = module.GetName()
       modLibDirName = module.GetLibraryParentDir()
       modLibName    = module.GetLibraryName()

       if newModule.GetName() == modName:
         if newModule.GetLibraryParentDir() == modLibDirName:
           assert newModule.GetLibraryName != modLibName, 'duplicate module; abort.'

     # add module to list
     self.modules.append( newModule )

     s = 'appended module ' + modNode.get('name')
     self.log.debug(s)

  s = 'end _SetupModules()'
  self.log.debug(s)

  return


#*********************************************************************************
