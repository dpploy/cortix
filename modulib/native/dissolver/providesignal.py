#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Nitrino module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import xml.etree.ElementTree as ElementTree
#*********************************************************************************

#---------------------------------------------------------------------------------
# Signal to request fuel load
def ProvideSignal( self, portFile, facilityTime ):
 
  gDec = self.gramDecimals

  # if the first time step, write the header of a time-sequence data file
  if facilityTime == 0.0:

    assert os.path.isfile(portFile) is False, 'portFile %r exists; stop.' % portFile

    tree = ElementTree.ElementTree()
    rootNode = tree.getroot()

    a = ElementTree.Element('time-sequence')
    a.set('name','dissolver-signal')

    b = ElementTree.SubElement(a,'comment')
    today = datetime.datetime.today()
    b.set('author','dissolver.nitrino')
    b.set('version','0.1')

    b = ElementTree.SubElement(a,'comment')
    today = datetime.datetime.today()
    b.set('today',str(today))

    b = ElementTree.SubElement(a,'time')
    b.set('unit','minute')

    # first variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Fuel Request')
    b.set('unit','gram')
    b.set('legend','Dissolver-signal')
    b.set('scale','linear')

    # values for all variables
    b = ElementTree.SubElement(a,'timeStamp')
    b.set('value',str(facilityTime))
    if  self.ready2LoadFuel == True:
      b.text = str(round(self.solidsMassLoadMax,gDec))
    else:
      b.text = '0'

    tree = ElementTree.ElementTree(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  # if not the first time step then parse the existing history file and append
  else:

    tree = ElementTree.parse( portFile )
    rootNode = tree.getroot()
    a = ElementTree.Element('timeStamp')
    a.set('value',str(facilityTime))
    if  self.ready2LoadFuel == True:
      a.text = str(round(self.solidsMassLoadMax,gDec))
    else:
      a.text = '0'

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#*********************************************************************************
