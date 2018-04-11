#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io, time

from ._getruntimestatus import _GetRuntimeStatus
#*********************************************************************************

#---------------------------------------------------------------------------------
# Execute task              

def _Execute(self, application ):

  network = application.get_network(self.name)

  runtimeStatusFiles = dict()
  
  for slotName in network.get_slot_names():

    moduleName = slotName.split('_')[0]
    slotId     = int(slotName.split('_')[1])
    mod = application.get_module( moduleName )

    paramFile = self.runtimeCortixParamFile
    commFile  = network.get_runtime_cortix_comm_file( slotName )

    # Run module in the slot
    statusFile = mod.execute( slotId, paramFile, commFile )
    assert statusFile is not None, 'module launching failed.'

    runtimeStatusFiles[ slotName ] = statusFile

# monitor runtime status

  status = 'running'

  while status == 'running': 

   time.sleep(10)  # hard coded; fix me.

   (status,slotNames) = _GetRuntimeStatus( self, runtimeStatusFiles )

   s = 'runtime status: '+status+'; module slots running: '+str(slotNames)
   self.log.info(s)

  return 


#*********************************************************************************
