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
def GetCondensate( self, portFile, facilityTime ):

  found = False

  while found is False:

    s = 'GetCondensate(): checking for condensate at '+str(facilityTime)
    self.log.debug(s)

    try:
      tree = ElementTree.parse( portFile )
    except ElementTree.ParseError as error:
      s = 'GetCondensate(): '+portFile+' unavailable. Error code: '+str(error.code)+' File position: '+str(error.position)+'. Retrying...'
      self.log.debug(s)
      continue

    rootNode = tree.getroot()
    assert rootNode.tag == 'time-sequence', 'invalid format.' 

    timeNode = rootNode.find('time')
    timeUnit = timeNode.get('unit').strip()
    assert timeUnit == "minute"

    varNodes = rootNode.findall('var')
    varNames = list()
    for v in varNodes:
      name = v.get('name').strip()
#      assert v.get('name').strip() == 'I2 Condensate', 'invalid variable.'
#      assert v.get('unit').strip() == 'gram/min', 'invalid mass unit'
      assert v.get('unit').strip() == 'gram', 'invalid mass unit'
      varNames.append(name)

    timeStampNodes = rootNode.findall('timeStamp')

    for tsn in timeStampNodes:

      timeStamp = float(tsn.get('value').strip())
 
      # get data at timeStamp facilityTime
      if timeStamp == facilityTime:

         found = True

         varValues = tsn.text.strip().split(',')
         assert len(varValues) == len(varNodes), 'inconsistent data; stop.'

         for varName in varNames:
           if varName == 'I2 Condensate':
              ivar = varNames.index(varName)
              mass = float(varValues[ivar])
 #             if facilityTime in self.historyI2MassLiquid.keys():
              self.historyI2MassLiquid[ facilityTime ] += mass
 #             else:
 #                self.historyI2MassLiquid[ facilityTime ] = mass

              s = 'GetCondensate(): received condensate at '+str(facilityTime)+' [min]; I2 mass [g] = '+str(round(mass,3))
              self.log.debug(s)
           # end of: if varName == 'I2 Condensate':
           if varName == 'Xe Condensate':
              ivar = varNames.index(varName)
              mass = float(varValues[ivar])
 #             if facilityTime in self.historyI2MassLiquid.keys():
              self.historyXeMassVapor[ facilityTime ] += mass
 #             else:
 #                self.historyXeMassLiquid[ facilityTime ] = mass

              s = 'GetCondensate(): received condensate at '+str(facilityTime)+' [min]; Xe mass [g] = '+str(round(mass,3))
              self.log.debug(s)
           # end of: if varName == 'Xe Condensate':
           if varName == 'Kr Condensate':
              ivar = varNames.index(varName)
              mass = float(varValues[ivar])
 #             if facilityTime in self.historyI2MassLiquid.keys():
              self.historyKrMassVapor[ facilityTime ] += mass
 #             else:
 #                self.historyKrMassLiquid[ facilityTime ] = mass

              s = 'GetCondensate(): received condensate at '+str(facilityTime)+' [min]; Kr mass [g] = '+str(round(mass,3))
              self.log.debug(s)
           # end of: if varName == 'Kr Condensate':

    # end for n in nodes:

    if found is False: time.sleep(1) 

  # end of while found is False:

  return 

#*********************************************************************************
