#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Nitrino module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import math, random
import xml.etree.ElementTree as ElementTree
#*********************************************************************************

#---------------------------------------------------------------------------------
def ProvideVapor( self, portFile, atTime ):

  # if the first time step, write the header of a time-sequence data file
  if atTime == 0.0:

    assert os.path.isfile(portFile) is False, 'portFile %r exists; stop.' % portFile

    tree = ElementTree.ElementTree()
    rootNode = tree.getroot()

    a = ElementTree.Element('time-sequence')
    a.set('name','dissolver-vapor')

    b = ElementTree.SubElement(a,'comment')
    b.set('author','dissolver')
    b.set('version','0.1')

    b = ElementTree.SubElement(a,'comment')
    today = datetime.datetime.today()
    b.set('today',str(today))

    b = ElementTree.SubElement(a,'time')
    b.set('unit','minute')

    # first variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Xe Vapor')
    b.set('unit','gram')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.pyplotScale)

    # second variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Kr Vapor')
    b.set('unit','gram')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.pyplotScale)

    # third variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','I2 Vapor')
    b.set('unit','gram')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.pyplotScale)

    # fourth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','RuO4 Vapor')
    b.set('unit','gram')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.pyplotScale)

    # fifth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','CO2 Vapor')
    b.set('unit','gram')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.pyplotScale)

    # sixth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','HTO Vapor')
    b.set('unit','gram')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.pyplotScale)

    # seventh variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','NO Vapor')
    b.set('unit','gram')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.pyplotScale)

    # eight variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','NO2 Vapor')
    b.set('unit','gram')
    b.set('legend','Dissolver-vapor')
    b.set('scale',self.pyplotScale)

    # values for all variables
    b = ElementTree.SubElement(a,'timeStamp')
    b.set('value',str(atTime))
    b.text = str('0.0') + ',' + \
             str('0.0') + ',' + \
             str('0.0') + ',' + \
             str('0.0') + ',' + \
             str('0.0') + ',' + \
             str('0.0') + ',' + \
             str('0.0') + ',' + \
             str('0.0')

    tree = ElementTree.ElementTree(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  # if not the first time step then parse the existing history file and append
  else:

    tree = ElementTree.parse( portFile )
    rootNode = tree.getroot()
    a = ElementTree.Element('timeStamp')
    a.set('value',str(atTime))

    # all variables
    gDec = self.gramDecimals

    if len(self.historyXeMassVapor.keys()) > 0:
      massXe = round(self.historyXeMassVapor[atTime],gDec)
    else:
      massXe = 0.0

    if len(self.historyKrMassVapor.keys()) > 0:
      massKr = round(self.historyKrMassVapor[atTime],gDec)
    else:
      massKr = 0.0

    if len(self.historyI2MassVapor.keys()) > 0:
      massI2 = round(self.historyI2MassVapor[atTime],gDec)
    else:
      massI2 = 0.0

    if len(self.historyRuO4MassVapor.keys()) > 0:
      massRuO4 = round(self.historyRuO4MassVapor[atTime],gDec)
    else:
      massRuO4 = 0.0

    if len(self.historyCO2MassVapor.keys()) > 0:
      massCO2 = round(self.historyCO2MassVapor[atTime],gDec)
    else:
      massCO2 = 0.0

    if len(self.historyHTOMassVapor.keys()) > 0:
      massHTO = round(self.historyHTOMassVapor[atTime],gDec)
    else:
      massHTO = 0.0

    if len(self.historyNOMassVapor.keys()) > 0:
      massNO = round(self.historyNOMassVapor[atTime],gDec)
    else:
      massNO = 0.0

    if len(self.historyNO2MassVapor.keys()) > 0:
      massNO2 = round(self.historyNO2MassVapor[atTime],gDec)
    else:
      massNO2 = 0.0

    a.text = str(massXe)   +','+ \
             str(massKr)   +','+ \
             str(massI2)   +','+ \
             str(massRuO4) +','+ \
             str(massCO2)  +','+ \
             str(massHTO)  +','+ \
             str(massNO)   +','+ \
             str(massNO2)

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#*********************************************************************************
