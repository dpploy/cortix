"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Tue Dec 10 11:21:30 EDT 2013
"""
#*********************************************************************************
import os, sys, io
from src.configtree import ConfigTree
#*********************************************************************************

#---------------------------------------------------------------------------------
# Private method: setup module              

def _setup( self ):

# Save config data
  for child in self.configNode.GetNodeChildren():

    ( tag, attributes, text ) = child
    text = text.strip()

    if self.modType != 'native':
       if tag == 'executableName': self.executableName = text
       if tag == 'executablePath': 
        if text[-1] != '/': text += '/'
        self.executablePath = text

    if tag == 'inputFileName': self.inputFileName = text
    if tag == 'inputFilePath': 
     if text[-1] != '/': text += '/'
     self.inputFilePath = text

    if tag == 'port': 
       assert len(attributes) == 3, 'only 3 attribute allowed/required at this moment.'

       tmp = dict() # store port name and three attributes

       for attribute in attributes:

         key = attribute[0]
         val = attribute[1].strip()

         if key == 'type':
           assert val == 'use' or val == 'provide' or val == 'input', 'port attribute value invalid.'
           tmp['portName']=text  # portName
           tmp['portType']=val   # portType
         elif key == 'mode': 
           v = val.split('.')[0]
           assert v == 'file' or v == 'directory', 'port attribute value invalid.'
           tmp['portMode'] = val
         elif key == 'multiplicity': 
           tmp['portMultiplicity']=int(val)  # portMultiplicity
         else:
           assert True, 'invalid port attribute. fatal.'

       assert len(tmp) == 4
       store = (tmp['portName'],tmp['portType'],tmp['portMode'],tmp['portMultiplicity'])
       self.ports.append( store ) # (portName, portType, portMode, portMultiplicity)
       tmp = None
       store = None
    
#  print('\t\tCortix::Simulation::Application::Module: executableName',self.executableName)
#  print('\t\tCortix::Simulation::Application::Module: executablePath',self.executablePath)
#  print('\t\tCortix::Simulation::Application::Module: inputFileName',self.inputFileName)
#  print('\t\tCortix::Simulation::Application::Module: inputFilePath',self.inputFilePath)
#  print('\t\tCortix::Simulation::Application::Module: ports',self.ports)

  return

#*********************************************************************************
