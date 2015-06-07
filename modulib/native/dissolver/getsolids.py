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
# Reads the solids (in the form of fuel segments) from an existing history file
def GetSolids( self, portFile, facilityTime ):

  fuelSegments = None

  found = False

  while found is False:

    try:
      tree = ElementTree.parse( portFile )
    except ElementTree.ParseError as error:
      s = 'GetSolids(): '+portFile+' unavailable. Error code: '+str(error.code)+' File position: '+str(error.position)+'. Retrying...'
      self.log.debug(s)
      continue

    rootNode = tree.getroot()

    assert rootNode.tag == 'time-variable-packet', 'invalid cortix file format; stop.'

    nodes = rootNode.findall('timeStamp')

    for n in nodes:

      timeStamp = float(n.get('value').strip())

      # get data at timeStamp facilityTime
      if timeStamp == facilityTime:

        #...........
        found = True
        #...........

        # get data packs
        pack1 = n.findall('pack1')
        pack2 = n.findall('pack2')

        # if there are data packs then proceed with parsing
        if len(pack1) != 0 or len(pack2) != 0:

          assert self.ready2LoadFuel is True, 'sanity check failed.'

          if self.dissolutionStartedTime >= 0.0:
             assert facilityTime >= self.dissolutionStartedTime + self.dutyPeriod, 'sanity check failed.'

          assert len(pack1) != 0 and len(pack2) != 0, 'sanity check failed.'
          assert len(pack1) == len(pack2), 'sanity check failed.'

          #............................................
          # read the header information into Spec lists
          #............................................

          timeElem = rootNode.find('time')
          timeStampUnit = timeElem.get('unit').strip()
          assert timeStampUnit == "minute"

          # pack1
          pack1Spec = rootNode.findall('pack1')
          assert len(pack1Spec) == 1, 'sanity check failed.'
          pack1Spec = rootNode.find('pack1')
 
          pack1Name = pack1Spec.get('name').strip()
          assert pack1Name == 'Geometry'

          # [(name,unit),(name,unit),...]
          segmentGeometrySpec = list()

          for var in pack1Spec:
            attributes = var.items()
            assert len(attributes) == 2
            for attribute in attributes:
              if   attribute[0] == 'name': name = attribute[1]
              elif attribute[0] == 'unit': unit = attribute[1]
              else: assert True
            segmentGeometrySpec.append( (name, unit) )

          # pack2
          pack2Spec = rootNode.findall('pack2')
          assert len(pack2Spec) == 1, 'sanity check failed.'
          pack2Spec = rootNode.find('pack2')
 
          pack2Name = pack2Spec.get('name').strip()
          assert pack2Name == 'Composition'

          # [(name,unit),(name,unit),...]
          segmentCompositionSpec = list()

          for var in pack2Spec:
            attributes = var.items()
            assert len(attributes) == 2
            for attribute in attributes:
              if   attribute[0] == 'name': name = attribute[1]
              elif attribute[0] == 'unit': unit = attribute[1]
              else: assert True
            segmentCompositionSpec.append( (name,unit) )

          #........................................
          # read the timeStamp data into Data lists
          #........................................

          # geometry data: list of a list of triples
          # first level: one entry for each fuel segment
          # second level: one entry (triple) for each geometry field
          # [ [(name,unit,val), (name,unit,val),...], [(name,unit,val),..], ... ]
          segmentsGeometryData = list()

          for pack in pack1: # each pack is a fuel segment
            packData = pack.text.strip().split(',')
            assert len(packData) == len(segmentGeometrySpec)
            for i in range(len(packData)): packData[i] = float(packData[i])
            segGeomData = list()
            for ((name,unit),val) in zip(segmentGeometrySpec,packData):
              segGeomData.append( (name,unit,val) )
            segmentsGeometryData.append( segGeomData )

          # composition data: list of a list of triples
          # first level: one entry for each fuel segment
          # second level: one entry (triple) for each elemental specie field
          # [ [(name,unit,val), (name,unit,val),...], [(name,unit,val),..], ... ]
          segmentsCompositionData = list()

          for pack in pack2: # each pack is a segment
            packData = pack.text.strip().split(',')
            assert len(packData) == len(segmentCompositionSpec)
            for i in range(len(packData)): packData[i] = float(packData[i])
            segCompData = list()
            for ((name,unit),val) in zip(segmentCompositionSpec,packData):
              segCompData.append( (name,unit,val) )
            segmentsCompositionData.append( segCompData )

          assert len(segmentsGeometryData) == len(segmentsCompositionData)

          fuelSegments = (segmentsGeometryData, segmentsCompositionData) 

        # end of: if len(pack1) != 0 or len(pack2) != 0:

      # end of: if timeStamp == facilityTime:

    # end of: for n in nodes:

    if found is False: 
      time.sleep(1)
      s = 'GetSolids(): did not find time stamp '+str(facilityTime)+' [min] in '+portFile
      self.log.debug(s)

  # end of: while found is False:

  if fuelSegments is None: nSegments = 0
  else:                    nSegments = len(fuelSegments[0])

  s = 'GetSolids(): got fuel load at '+str(facilityTime)+' [min], with '+str(nSegments)+' segments'
  self.log.debug(s)

  return  fuelSegments

#*********************************************************************************
