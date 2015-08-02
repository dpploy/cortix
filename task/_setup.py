"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io, time
#*********************************************************************************

#---------------------------------------------------------------------------------
# Setup task                

def _Setup(self):

  s = 'start _Setup()'
  self.log.debug(s)

  for child in self.configNode.GetNodeChildren():
    (elem, tag, items, text) = child
    if tag == 'evolveTime':
       for (key,value) in items:
        if key == 'unit' : self.evolveTimeUnit = value
       
       self.evolveTime = float(text.strip())
    if tag == 'timeStep':
       for (key,value) in items:
        if key == 'unit' : self.timeStepUnit = value
       
       self.timeStep = float(text.strip())

  s = 'evolveTime value = '+str(self.evolveTime)
  self.log.debug(s)
  s = 'evolveTime unit  = '+str(self.evolveTimeUnit)
  self.log.debug(s)

  s = 'end _Setup()'
  self.log.debug(s)

  return

#*********************************************************************************
