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

  for child in self.configNode.get_node_children():

    (elem, tag, items, text) = child

    if tag == 'startTime':
       for (key,value) in items:
        if key == 'unit' : self.startTimeUnit = value
       
       self.startTime = float(text.strip())

    if tag == 'evolveTime':
       for (key,value) in items:
        if key == 'unit' : self.evolveTimeUnit = value
       
       self.evolveTime = float(text.strip())

    if tag == 'timeStep':
       for (key,value) in items:
        if key == 'unit' : self.timeStepUnit = value
       
       self.timeStep = float(text.strip())

  if self.startTimeUnit == 'null-startTimeUnit': self.startTimeUnit = self.evolveTimeUnit
  assert self.evolveTimeUnit != 'null-evolveTimeUnit', 'invalid time unit = %r'%(self.evolveTimeUnit)

  s = 'startTime value = '+str(self.startTime)
  self.log.debug(s)
  s = 'startTime unit  = '+str(self.startTimeUnit)
  self.log.debug(s)

  s = 'evolveTime value = '+str(self.evolveTime)
  self.log.debug(s)
  s = 'evolveTime unit  = '+str(self.evolveTimeUnit)
  self.log.debug(s)

  s = 'end _Setup()'
  self.log.debug(s)

  return

#*********************************************************************************
