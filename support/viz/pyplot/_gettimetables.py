"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Pyplot module.

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import xml.etree.ElementTree as ElementTree
from threading import Lock
#*********************************************************************************

#---------------------------------------------------------------------------------
# This uses a use portFile which is guaranteed at this point

def _GetTimeTables( self, portFile, atTime ):

  s = '_GetTimeTables(): will check file: ' + portFile
  self.log.debug(s)

  found = False

  while found is False:

    s = '_GetTimeTables(): checking for value at ' + str(atTime)
    self.log.debug(s)

#    tree = ElementTree.parse(portFile)

    try:
      mutex = Lock()
      mutex.acquire()
      tree = ElementTree.parse( portFile )
    except ElementTree.ParseError as error:
      mutex.release()
      s = '_GetTimeTables(): '+portFile+' unavailable. Error code: '+str(error.code)+' File position: '+str(error.position)+'. Retrying...'
      self.log.debug(s)
      time.sleep(0.1)
      continue

    mutex.release()
    rootNode = tree.getroot()
    assert rootNode.tag == 'time-tables', 'invalid format.'
  
    timeNodes = rootNode.findall('timeStamp')

    for timeNode in timeNodes:

      timeStamp = float(timeNode.get('value').strip())

      if timeStamp == atTime:

        found = True  

        timeUnit = timeNode.get('unit').strip()

        self.timeTablesData[ (timeStamp,timeUnit) ] = list()

        columns = timeNode.findall('column')

        data = list()

        for col in columns: 
            data.append( col )

        self.timeTablesData[ (timeStamp,timeUnit) ] = data

        s = '_GetTimeTables(): added '+str(len(data))+' columns of data'
        self.log.debug(s)

      # end of if timeStamp == atTime:

    # end of for timeNode in timeNodes:

    if found is False: time.sleep(0.1)

  # while found is False:

  return

#*********************************************************************************
