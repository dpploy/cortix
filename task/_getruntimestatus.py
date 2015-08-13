"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io, time
from xml.etree.cElementTree import ElementTree

#*********************************************************************************

#---------------------------------------------------------------------------------
# Check overall task status 

def _GetRuntimeStatus( self, runtimeStatusFiles ):
  
  taskStatus = 'finished'
  runningModuleSlots = list()

  for (slotName,statusFile) in runtimeStatusFiles.items():

     if not os.path.isfile(statusFile): time.sleep(0.1)
     assert os.path.isfile(statusFile), 'runtime status file %r not found.' % statusFile

     tree = ElementTree()
     tree.parse( statusFile )
     statusFileXMLRootNode = tree.getroot()
     node = statusFileXMLRootNode.find('status')
     status = node.text.strip()
     if status == 'running': 
       taskStatus = 'running'
       runningModuleSlots.append(slotName)
  
  return (taskStatus, runningModuleSlots)

#*********************************************************************************
