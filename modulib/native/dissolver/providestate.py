#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Nitrino module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import xml.etree.ElementTree as ElementTree
from .getfuelmass   import GetFuelMass
from .getfuelvolume import GetFuelVolume
#*********************************************************************************

#---------------------------------------------------------------------------------
def ProvideState( self, portFile, atTime ):
 
  gDec  = self.gramDecimals
  ccDec = self.ccDecimals   
 
  pyplotScale = 'linear'

  # if the first time step, write the header of a time-sequence data file
  if atTime == 0.0:

    assert os.path.isfile(portFile) is False, 'portFile %r exists; stop.' % portFile

    tree = ElementTree.ElementTree()
    rootNode = tree.getroot()

    a = ElementTree.Element('time-sequence')
    a.set('name','dissolver-state')

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
    b.set('name','Fuel')
    tmp = GetFuelMass(self)
    if tmp is not None:
      (fuelMass,unit) = tmp
    else:
      fuelMass = 0.0
      unit = 'gram'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',pyplotScale)

    # second variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Fuel')
    tmp = GetFuelVolume(self)
    if tmp is not None:
      (fuelVolume,unit) = tmp
    else:
      fuelVolume = 0.0
      unit = 'cc'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',pyplotScale)

    # third variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','I2 Liquid')
    if len(self.historyI2MassLiquid.keys()) > 0:
      massI2Liquid = self.historyI2MassLiquid[ atTime ]
    else:
      massI2Liquid = 0.0
    unit = 'gram'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',pyplotScale)

    # fourth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','HTO Liquid')
    if len(self.historyHTOMassLiquid.keys()) > 0:
      massHTOLiquid = self.historyHTOMassLiquid[ atTime ]
    else:
      massHTOLiquid = 0.0
    unit = 'gram'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',pyplotScale)

    # fifth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','HNO3 Liquid')
    if len(self.historyHNO3MolarLiquid.keys()) > 0:
      molarHNO3Liquid = self.historyHNO3MolarLiquid[ atTime ]
    else:
      molarHNO3Liquid = 0.0
    unit = 'M'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',pyplotScale)

    # sixth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','UO2(NO3)2 Liquid')
    if len(self.historyUNMassConcLiquid.keys()) > 0:
      massConcUNLiquid = self.historyUNMassConcLiquid[ atTime ]
    else:
      massConcUNLiquid = 0.0
    unit = 'g/L'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',pyplotScale)

    # seventh variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Pu(NO3)4 Liquid')
    if len(self.historyPuNMassConcLiquid.keys()) > 0:
      massConcPuNLiquid = self.historyPuNMassConcLiquid[ atTime ]
    else:
      massConcPuNLiquid = 0.0
    unit = 'g/L'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',pyplotScale)

    # eighth variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','FP(NO3)2.36 Liquid')
    if len(self.historyFPNMassConcLiquid.keys()) > 0:
      massConcFPNLiquid = self.historyFPNMassConcLiquid[ atTime ]
    else:
      massConcFPNLiquid = 0.0
    unit = 'g/L'
    b.set('unit',unit)
    b.set('legend','Dissolver-state')
    b.set('scale',pyplotScale)

    # values for all variables
    b = ElementTree.SubElement(a,'timeStamp')
    b.set('value',str(atTime))
    fuelMass   = round(fuelMass,gDec)
    fuelVolume = round(fuelVolume,ccDec)
    massI2Liquid  = round(massI2Liquid,gDec)
    massHTOLiquid = round(massHTOLiquid,gDec)
    b.text = str(fuelMass)+','+\
             str(fuelVolume)+','+\
             str(massI2Liquid)+','+\
             str(massHTOLiquid)+','+\
             str(molarHNO3Liquid)+','+\
             str(massConcUNLiquid)+','+\
             str(massConcPuNLiquid)+','+\
             str(massConcFPNLiquid)

    tree = ElementTree.ElementTree(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  # if not the first time step then parse the existing history file and append
  else:

    tree = ElementTree.parse( portFile )
    rootNode = tree.getroot()
    a = ElementTree.Element('timeStamp')
    a.set('value',str(atTime))

    # all variables
    tmp = GetFuelMass(self)
    if tmp is not None:
       (fuelMass,unit) = tmp
    else:
      fuelMass = 0.0

    tmp = GetFuelVolume(self)
    if tmp is not None:
       (fuelVolume,unit) = tmp
    else:
      fuelVolume = 0.0

    if len(self.historyI2MassLiquid.keys()) > 0:
      massI2Liquid = self.historyI2MassLiquid[ atTime ]
    else:
      massI2Liquid = 0.0

    if len(self.historyHTOMassLiquid.keys()) > 0:
      massHTOLiquid = self.historyHTOMassLiquid[ atTime ]
    else:
      massHTOLiquid = 0.0

    if len(self.historyHNO3MolarLiquid.keys()) > 0:
      molarHNO3Liquid = self.historyHNO3MolarLiquid[ atTime ]
    else:
      molarHNO3Liquid = 0.0

    if len(self.historyUNMassConcLiquid.keys()) > 0:
      massConcUNLiquid = self.historyUNMassConcLiquid[ atTime ]
    else:
      massConcUNLiquid = 0.0

    if len(self.historyPuNMassConcLiquid.keys()) > 0:
      massConcPuNLiquid = self.historyPuNMassConcLiquid[ atTime ]
    else:
      massConcPuNLiquid = 0.0

    if len(self.historyFPNMassConcLiquid.keys()) > 0:
      massConcFPNLiquid = self.historyFPNMassConcLiquid[ atTime ]
    else:
      massConcFPNLiquid = 0.0

    if len(self.historyNOMassVapor.keys()) > 0:
      massNOVapor = self.historyNOMassVapor[ atTime ]
    else:
      massNOVapor = 0.0

    if len(self.historyNO2MassVapor.keys()) > 0:
      massNO2Vapor = self.historyNO2MassVapor[ atTime ]
    else:
      massNO2Vapor = 0.0

    a.text = str(round(fuelMass,3))+','+\
             str(round(fuelVolume,ccDec))+','+\
             str(round(massI2Liquid,gDec))+','+\
             str(round(massHTOLiquid,gDec))+','+\
             str(round(molarHNO3Liquid,3))+','+\
             str(round(massConcUNLiquid,3))+','+\
             str(round(massConcPuNLiquid,3))+','+\
             str(round(massConcFPNLiquid,3))

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#*********************************************************************************
