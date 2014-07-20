#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Storage module

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import logging
import xml.etree.ElementTree as ElementTree
#*********************************************************************************

#*********************************************************************************
class Storage(object):

# Private member data
# __slots__ = [

 def __init__( self,
               ports 
             ):

  assert type(ports) is list, '-> ports type %r is invalid.' % type(ports)

  self.__ports = ports

  self.__fuelSegments = list()

  self.__withdrawMass = 0.0

  self.__log = logging.getLogger('storage')
  self.__log.info('initializing an instance of Storage')

  self.__gramDecimals = 3 # milligram significant digits
  self.__mmDecimals   = 3 # micrometer significant digits

#---------------------------------------------------------------------------------
 def CallPorts(self, evolTime=0.0, evolveTime=0.0):

  self.__UseData( usePortName='solids', evolTime=evolTime  )
 
  self.__UseData( usePortName='withdrawal-request', evolTime=evolTime  )

  self.__ProvideData( providePortName='fuel-segments', evolTime=evolTime, evolveTime=evolveTime )

  self.__ProvideData( providePortName='state', evolTime=evolTime, evolveTime=evolveTime)

#---------------------------------------------------------------------------------
 def Execute( self, evolTime=0.0, timeStep=1.0, evolveTime=0.0 ):

  s = 'Execute(): facility time [min] = ' + str(evolTime)
  self.__log.info(s)
  gDec = self.__gramDecimals
  s = 'Execute(): total mass [g] = ' + str(round(self.__GetMass(),gDec))
  self.__log.info(s)
  s = 'Execute(): # of segments  = '+str(len(self.__fuelSegments))
  self.__log.debug(s)

  self.__Store( evolTime + timeStep )

#---------------------------------------------------------------------------------
 def __UseData( self, usePortName=None, evolTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( usePortName = usePortName )

# Get data from port files
  if usePortName == 'solids': self.__GetSolids( portFile, evolTime )
  if usePortName == 'withdrawal-request': self.__GetWithdrawalRequest( portFile, evolTime )

#---------------------------------------------------------------------------------
 def __ProvideData( self, providePortName=None, evolTime=0.0, evolveTime=0.0 ):

# Access the port file
  portFile = self.__GetPortFile( providePortName = providePortName )

# Send data to port files
  if providePortName == 'fuel-segments' and portFile is not None: 
     self.__ProvideFuelSegmentsOnDemand( portFile, evolTime, evolveTime )
  if providePortName == 'state' and portFile is not None:
     self.__ProvideState( portFile, evolTime, evolveTime )

#---------------------------------------------------------------------------------
 def __GetPortFile( self, usePortName=None, providePortName=None ):

  portFile = None

  #..........
  # Use ports
  #..........
  if usePortName is not None:

    assert providePortName is None

    for port in self.__ports:
     if port[0] == usePortName and port[1] == 'use': portFile = port[2]

    maxNTrials = 50
    nTrials    = 0
    while not os.path.isfile(portFile) and nTrials < maxNTrials:
      nTrials += 1
      time.sleep(1)

    if nTrials >= 10:
      s = '__GetPortFile(): waited ' + str(nTrials) + ' trials for port: ' + portFile
      self.__log.warn(s)

    assert os.path.isfile(portFile) is True, 'portFile %r not available; stop.' % portFile
  #..............
  # Provide ports
  #..............
  if providePortName is not None:

    assert usePortName is None

    for port in self.__ports:
     if port[0] == providePortName and port[1] == 'provide': portFile = port[2]

  return portFile

#---------------------------------------------------------------------------------
# This uses a use portFile which is guaranteed at this point
 def __GetSolids( self, portFile, evolTime ):

  # THIS IS A GLITCH ON THE INPUT DATA FROM THE HEAD-END. IT SHOULD HAVE DATA
  # FOR 24 HOURS. ONLY HAS 107 minutes
  if evolTime > 107: return

  found = False

  while found is False:

    try:
      tree = ElementTree.parse( portFile )
    except ElementTree.ParseError as error:
      s = '__GetSolids(): '+portFile+' unavailable. Error code: '+str(error.code)+' File position: '+str(error.position)+'. Retrying...'
      self.__log.debug(s)
      continue

    rootNode = tree.getroot()

    durationNode = rootNode.find('Duration')
  
    timeStep = float(durationNode.get('timeStep'))
    s = '__GetSolids(): timeStep='+str(timeStep)
    self.__log.debug(s)

    streamNode = rootNode.find('Stream')
    s = '__GetSolids(): streamNode='+streamNode.get('name')
    self.__log.debug(s)

    timeNodes = streamNode.findall('Time')
    s = '__GetSolids(): # time nodes ='+str(len(timeNodes))
    self.__log.debug(s)

#.................................................................................
    for timeNode in timeNodes:

     totalMass = 0.0

     U    = 0.0
     Pu   = 0.0
     Cs   = 0.0
     Sr   = 0.0
     I    = 0.0
     Kr   = 0.0
     Xe   = 0.0
     a3H  = 0.0
     Ru   = 0.0
     O    = 0.0
     N    = 0.0
     FP   = 0.0

     timeIndex = int(timeNode.get('index'))

#   s = '__GetSolids(): timeIndex='+str(timeIndex)
#   self.__log.debug(s)

     timeStamp = timeStep*timeIndex          

#   s = '__GetSolids(): timeStamp='+str(timeStamp)
#   self.__log.debug(s)
  
     if timeStamp == evolTime: 

       #...........
       found = True
       #...........

#     s = '__GetSolids(): timeStamp='+str(timeStamp)+';'+' evolTime='+str(evolTime)
#     self.__log.debug(s)

       n = timeNode.find('Segment_Length')
 
       if not ElementTree.iselement(n): continue # to the next timeNode
 
       segmentLength = float(n.get('length'))
       segmentLengthUnit = n.get('unit')
       if   segmentLengthUnit == 'm':  segmentLength *= 1000.0
       elif segmentLengthUnit == 'cm': segmentLength *= 10.0
       elif segmentLengthUnit == 'mm': segmentLength *= 1.0
       else:                            assert True, 'invalid unit.'
        
       n = timeNode.find('Segment_Outside_Diameter')
       oD = float(n.get('outside_diameter'))
       oDUnit = n.get('unit')
       if   oDUnit == 'm':  oD *= 1000.0
       elif oDUnit == 'cm': oD *= 10.0
       elif oDUnit == 'mm': oD *= 1.0
       else:                assert True, 'invalid unit.'

       n = timeNode.find('Segment_Inside_Diameter')
       iD = float(n.get('inside_diameter'))
       iDUnit = n.get('unit')
       if   iDUnit == 'm':  iD *= 1000.0
       elif iDUnit == 'cm': iD *= 10.0
       elif iDUnit == 'mm': iD *= 1.0
       else:                assert True, 'invalid unit.'

       n = timeNode.find('Segments_Output_This_Timestep')
       nSegments = float(n.get('segments_output'))

       elements = timeNode.findall('Element')
       for element in elements:
         isotopes = element.findall('Isotope')
         for isotope in isotopes:
          for child in isotope:
             if child.tag == 'Mass': 
                mass = float(child.text.strip())
                totalMass += mass
                if element.get('key') == 'U' :  U  += mass; 
                if element.get('key') == 'Pu':  Pu += mass; 
                if element.get('key') == 'Cs':  Cs += mass; 
                if element.get('key') == 'Sr':  Sr += mass; 
                if element.get('key') == 'I' :  I  += mass; 
                if element.get('key') == 'Kr':  Kr += mass; 
                if element.get('key') == 'Xe':  Xe += mass; 
                if element.get('key') == 'H' : a3H += mass; 
                if element.get('key') == 'Ru':  Ru += mass; 
                if element.get('key') == 'O' :  O  += mass; 
                if element.get('key') == 'N' :  N  += mass; 

#  print('mass     [g]= ', mass)
#  print('#segments   = ', nSegments)
#  print('length      = ', segmentLength)
#  print('OD          = ', oD)
#  print('ID          = ', iD)

       FP = totalMass - (U + Pu + I + Kr + Xe + a3H)
#     totalNSegments += nSegments

#  print('mass U      = ', U)
#  print('mass Pu     = ', Pu)
#  print('mass Cs     = ', Cs)
#  print('mass I      = ', I)
#  print('mass O      = ', O)
#  print('mass N      = ', N)
#  print('mass FP     = ', FP)

       for seg in range(1,int(nSegments)+1):
         segMass   = totalMass / int(nSegments)
         segLength = segmentLength
         segID     = iD
         U         = U  / int(nSegments)
         Pu        = Pu / int(nSegments)
         I         = I  / int(nSegments)
         Kr        = Kr / int(nSegments)
         Xe        = Xe / int(nSegments)
         a3H       = a3H/ int(nSegments)
         FP        = FP / int(nSegments)
         segment   = ( timeStamp, segMass, segLength, segID, 
                       U, Pu, I, Kr, Xe, a3H, FP )

         self.__fuelSegments.append( segment )
  
#  print('totalMass     [g]= ', totalMass)
#  print('total # segments = ', totalNSegments)
#  print('total # pieces   = ', len(self.__fuelSegments))
#  print('total U       [g]= ', totalU)
#  print('total Pu      [g]= ', totalPu)
#  print('total Cs      [g]= ', totalCs)
#  print('total I       [g]= ', totalI)
#  print('total O       [g]= ', totalO)
#  print('total N       [g]= ', totalN)
#  print('total FP      [g]= ', totalFP)
  
#  print(self.__fuelSegments)
#  for s in self.__fuelSegments:
#   print(s[0],s[1],s[2])

       break

    if found is False: time.sleep(1) 

  # end of while found is False:

  return

#---------------------------------------------------------------------------------
# This uses a use portFile which is guaranteed to exist at this point
 def __GetWithdrawalRequest( self, portFile, evolTime ):

  found = False

  while found is False:

    s = '__GetWithdrawalRequest(): checking for withdrawal message at '+str(evolTime)
    self.__log.debug(s)

    try:
      tree = ElementTree.parse( portFile )
    except ElementTree.ParseError as error:
      s = '__GetWithdrawalRequest(): '+portFile+' unavailable. Error code: '+str(error.code)+' File position: '+str(error.position)+'. Retrying...'
      self.__log.debug(s)
      continue

    rootNode = tree.getroot()
    assert rootNode.tag == 'time-sequence', 'invalid format.' 

    node = rootNode.find('time')
    timeUnit = node.get('unit').strip()
    assert timeUnit == "minute"

    # vfda to do: check for single var element
    node = rootNode.find('var')
    assert node.get('name').strip() == 'Fuel Request', 'invalid variable.'
    assert node.get('unit').strip() == 'gram', 'invalid mass unit'

    nodes = rootNode.findall('timeStamp')

    for n in nodes:

      timeStamp = float(n.get('value').strip())
 
      # get data at timeStamp evolTime
      if timeStamp == evolTime:

         found = True

         mass = 0.0
         mass = float(n.text.strip())
         self.__withdrawMass = mass

         s = '__GetWithdrawalRequest(): received withdrawal message at '+str(evolTime)+' [min]; mass [g] = '+str(round(mass,3))
         self.__log.debug(s)

    # end for n in nodes:

    if found is False: time.sleep(1) 

  # end of while found is False:

  return 

#---------------------------------------------------------------------------------
 def __GetMass(self, timeStamp=None):
 
  mass = 0.0

  if timeStamp is None:
     for fuelSeg in self.__fuelSegments:
      mass += fuelSeg[1]

  else:
     for fuelSeg in self.__fuelSegments:
      if fuelSeg[0] <= timeStamp: mass += fuelSeg[1]

  return mass

#---------------------------------------------------------------------------------
# Provide the entire history data 
 def __ProvideFuelSegmentsOnDemand( self, portFile, evolTime, evolveTime ):

  gDec  = self.__gramDecimals
  mmDec = self.__mmDecimals

  vars1 = [('timeStamp','minute'),
           ('mass','gram'),
           ('length','mm'),
           ('innerDiameter','mm')]

  vars2 = [('U','gram'),
           ('Pu','gram'),
           ('I','gram'),
           ('Kr','gram'),
           ('Xe','gram'),
           ('3H','gram'),
           ('FP','gram')]

  withdrawMass = self.__withdrawMass

  #...........................................
  # if the first time step write a nice header
  #...........................................
  if evolTime == 0.0:

    fout = open( portFile, 'w')

    s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
    s = '<time-variable-packet name="fuelSegments">\n'; fout.write(s) 
    s = ' <comment author="cortix.modules.native.storage" version="0.1"/>\n'; fout.write(s)
    today = datetime.datetime.today()
    s = ' <comment today="'+str(today)+'"/>\n'; fout.write(s)
    s = ' <time unit="minute"/>\n'; fout.write(s)

    # first packet
    s = ' <pack1 name="Geometry">\n'; fout.write(s)
    for var in vars1:
      s = '  <var name="'+var[0]+'" unit="'+var[1]+'"/>\n'; fout.write(s)
    s = ' </pack1>\n'; fout.write(s)

    # second packet
    s = ' <pack2 name="Composition">\n'; fout.write(s)
    for var in vars2:
      s = '  <var name="'+var[0]+'" unit="'+var[1]+'"/>\n'; fout.write(s)
    s = ' </pack2>\n'; fout.write(s)

    # time stamp
    s = ' <timeStamp value="'+str(evolTime)+'">\n'; fout.write(s)

    if withdrawMass == 0.0 or withdrawMass > self.__GetMass( evolTime ): 

      s = ' </timeStamp>\n'; fout.write(s)

      s = '</time-variable-packet>\n'; fout.write(s)
      fout.close()

      s = '__ProvideFuelSegmentsOnDemand(): providing no fuel at '+str(evolTime)+' [min]'
      self.__log.debug(s)

      self.__withdrawMass = 0.0

      return

    else: # of if withdrawMass == 0.0 or withdrawMass > self.__GetMass( evolTime ): 

      fuelSegmentsLoad = list()
      fuelMassLoad = 0.0

      # withdraw fuel elements
      while fuelMassLoad <= withdrawMass:
           fuelSegmentCandidate = self.__WithdrawFuelSegment( evolTime )
           if fuelSegmentCandidate is None: break # no segments left with time stamp <= evolTime
           mass          = fuelSegmentCandidate[1]
           fuelMassLoad += mass
           if fuelMassLoad <= withdrawMass:
              fuelSegmentsLoad.append( fuelSegmentCandidate )
           else:
              self.__RestockFuelSegment( fuelSegmentCandidate )

      assert len(fuelSegmentsLoad) != 0, 'sanity check failed.'

      # Save in file data from withdrawal
      for fuelSeg in fuelSegmentsLoad:

        timeStamp = fuelSeg[0]
        assert timeStamp <=  evolTime, 'sanity check failed.'
        mass      = fuelSeg[1]
        length    = fuelSeg[2]
        segID     = fuelSeg[3]
        U         = fuelSeg[4]
        Pu        = fuelSeg[5]
        I         = fuelSeg[6]
        Kr        = fuelSeg[7]
        Xe        = fuelSeg[8]
        a3H       = fuelSeg[9]
        FP        = fuelSeg[10]

        # first packet
        s = '  <pack1>'
        fuelSegVars1 = [timeStamp,mass,length,segID]
        assert len(fuelSegVars1) == len(vars1)
        for var in fuelSegVars1: 
          s += str(var)+','
        s = s[:-1] + '</pack1>\n'; fout.write(s)

        # second packet
        s = '  <pack2>'
        fuelSegVars2 = [U,Pu,I,Kr,Xe,a3H,FP]
        assert len(fuelSegVars2) == len(vars2)
        for var in fuelSegVars2: 
          s += str(var)+','
        s = s[:-1] + '</pack2>\n'; fout.write(s)
  
        s = ' </timeStamp>\n'; fout.write(s)
  
        s = '</time-variable-packet>\n'; fout.write(s)
        fout.close()

        s = '__ProvideFuelSegmentsOnDemand(): providing '+str(len(fuelSegmentsLoad))+' fuel segments at '+str(evolTime)+' [min].'
        self.__log.debug(s)

      # endo of for fuelSeg in fuelSegmentsLoad:

      self.__withdrawMass = 0.0

      return

    # end of if withdrawMass == 0.0 or withdrawMass > self.__GetMass( evolTime ): 

  #...........................................................................
  # if not the first time step then parse the existing history file and append
  #...........................................................................
  else: # of if evolTime == 0.0:

    tree = ElementTree.parse( portFile )
    rootNode = tree.getroot()

    newTimeStamp = ElementTree.Element('timeStamp')
    newTimeStamp.set('value',str(evolTime))

    if withdrawMass == 0.0 or withdrawMass > self.__GetMass( evolTime ): 

      rootNode.append(newTimeStamp)
      tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

      self.__withdrawMass = 0.0

      s = '__ProvideFuelSegmentsOnDemand(): providing no fuel at '+str(evolTime)+' [min]'
      self.__log.debug(s)
   
      return

    else: # of if withdrawMass == 0.0 or withdrawMass > self.__GetMass( evolTime ):

      fuelSegmentsLoad = list()
      fuelMassLoad = 0.0

      # withdraw fuel elements
      while fuelMassLoad <= withdrawMass:
           fuelSegmentCandidate = self.__WithdrawFuelSegment( evolTime )
           if fuelSegmentCandidate is None: break # no segments left with time stamp <= evolTime
           mass          = fuelSegmentCandidate[1]
           fuelMassLoad += mass
           if fuelMassLoad <= withdrawMass:
              fuelSegmentsLoad.append( fuelSegmentCandidate )
           else:
              self.__RestockFuelSegment( fuelSegmentCandidate )

      assert len(fuelSegmentsLoad) != 0, 'sanity check failed.'

      for fuelSeg in fuelSegmentsLoad:

        timeStamp = fuelSeg[0]
        assert timeStamp <= evolTime, 'sanity check failed.'
        mass      = round(fuelSeg[1],gDec)
        length    = round(fuelSeg[2],mmDec)
        segID     = round(fuelSeg[3],mmDec)
        U         = round(fuelSeg[4],gDec)
        Pu        = round(fuelSeg[5],gDec)
        I         = round(fuelSeg[6],gDec)
        Kr        = round(fuelSeg[7],gDec)
        Xe        = round(fuelSeg[8],gDec)
        a3H       = round(fuelSeg[9],gDec)
        FP        = round(fuelSeg[10],gDec)
 
        # first packet
        a = ElementTree.SubElement(newTimeStamp, 'pack1')
        fuelSegVars1 = [timeStamp,mass,length,segID]
        assert len(fuelSegVars1) == len(vars1)
        s = ''
        for var in fuelSegVars1: 
          s += str(var)+','
        s = s[:-1] 
        a.text = s

        # second packet
        b = ElementTree.SubElement(newTimeStamp, 'pack2')
        fuelSegVars2 = [U,Pu,I,Kr,Xe,a3H,FP]
        assert len(fuelSegVars2) == len(vars2)
        s = ''
        for var in fuelSegVars2: 
          s += str(var)+','
        s = s[:-1] 
        b.text = s

      rootNode.append(newTimeStamp)
      tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

      s = '__ProvideFuelSegmentsOnDemand(): providing '+str(len(fuelSegmentsLoad))+' fuel segments at '+str(evolTime)+' [min].'
      self.__log.debug(s)

      self.__withdrawMass = 0.0

      return

  # end of if evolTime == 0.0:

  return

#---------------------------------------------------------------------------------
 def __ProvideState( self, portFile, evolTime, evolveTime ):

  # if the first time step, write the header of a time-sequence data file
  if evolTime == 0.0:

    assert os.path.isfile(portFile) is False, 'portFile %r exists; stop.' % portFile

    tree = ElementTree.ElementTree()
    rootNode = tree.getroot()

    a = ElementTree.Element('time-sequence')
    a.set('name','storage-state')

    b = ElementTree.SubElement(a,'comment')
    today = datetime.datetime.today()
    b.set('author','cortix.modules.native.storage')
    b.set('version','0.1')

    b = ElementTree.SubElement(a,'comment')
    today = datetime.datetime.today()
    b.set('today',str(today))

    b = ElementTree.SubElement(a,'time')
    b.set('unit','minute')

    # first variable
    b = ElementTree.SubElement(a,'var')
    b.set('name','Fuel Inventory')
    b.set('unit','gram')
    b.set('legend','Storage-state')

    # values for all variables
    b = ElementTree.SubElement(a,'timeStamp')
    b.set('value',str(evolTime))
    gDec = self.__gramDecimals
    mass = round(self.__GetMass(),gDec)
    b.text = str(mass)

    tree = ElementTree.ElementTree(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  # if not the first time step then parse the existing history file and append
  else:

    tree = ElementTree.parse( portFile )
    rootNode = tree.getroot()
    a = ElementTree.Element('timeStamp')
    a.set('value',str(evolTime))
    gDec = self.__gramDecimals
    mass = round(self.__GetMass(),gDec)
    a.text = str(mass)

    rootNode.append(a)

    tree.write( portFile, xml_declaration=True, encoding="unicode", method="xml" )

  return 

#---------------------------------------------------------------------------------
 def __GetNSegments(self, timeStamp=None):
 
  nSegments = 0

  if timeStamp is None:
      nSegments = len(self.__fuelSegments)

  else:
     for fuelSeg in self.__fuelSegments:
      if fuelSeg[0] <= timeStamp: nSegments += 1

  return nSegments

#---------------------------------------------------------------------------------
 def __WithdrawFuelSegment(self, evolTime ):

  fuelSegment = None

  for fuelSeg in self.__fuelSegments:
     if fuelSeg[0] <= evolTime:
      fuelSegment = fuelSeg
      self.__fuelSegments.remove(fuelSeg)
      break 

#  print('WithdrawFuelSegment:: fuelSegment',fuelSegment, ' evolTime=',evolTime)

  return fuelSegment # if None, it is an empty drum

#---------------------------------------------------------------------------------
 def __RestockFuelSegment( self, fuelSegment ):

  self.__fuelSegments.insert(0,fuelSegment)

#---------------------------------------------------------------------------------
 def __Store( self, facilityTime ):

  # program here the Xe off gas

  return

#*********************************************************************************
# Usage: -> python storage.py
if __name__ == "__main__":
 print('Unit testing for Storage')
