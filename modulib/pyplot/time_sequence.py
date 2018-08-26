# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/cortix
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/cortix/blob/master/COPYRIGHT.txt
#
# Licensed under the GNU General Public License v. 3, please see LICENSE file.
# https://www.gnu.org/licenses/gpl-3.0.txt
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Pyplot module.

This class manages time-sequence data in XML or tabular formats.
It is a helper for reading and manipulating stored file data in Cortix.
The XML data is a ElementTree object. 

Sat Jul 19 12:13:05 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import logging
import xml.etree.ElementTree as ElementTree
from threading import Lock
#*********************************************************************************

class TimeSequence():

 def __init__( self,
               fileName = None,   # full path file name
               fileType = None,   # "xml"
               initialTime = 0.0,
               finalTime   = 0.0,
               logger = None
             ):

  assert type(fileName) is str, 'wrong type; stop.'
  assert fileName is not None, 'must give a fileName; stop.' 
  self.__fileName = fileName

  assert type(fileType) is str, 'wrong type; stop.'
  assert fileType is not None, 'must give a fileType; stop.' 
  self.__fileType = fileType

  assert type(initialTime) is float, 'wrong type; stop.'
  self.__initialTime = initialTime

  assert type(finalTime) is float, 'wrong type; stop.'
  self.__finalTime   = finalTime

  assert finalTime   >= initialTime, 'sanity check failed. stop.'
  assert initialTime >= 0.0, 'sanity check failed. stop.'
  assert finalTime   >= 0.0, 'sanity check failed. stop.'

  assert type(logger) is logging.Logger, 'wrong type; stop.'
  assert logger is not None, 'must give a logger; stop.' 
  self.log = logger
     
  self.__tree = None

  if fileType == 'xml': 
     self.__read_xml()

#  s = 'TimeSequence::__init__(): built object'
#  self.log.debug(s)
#---------------------- end def __init__():---------------------------------------

#---------------------------------------------------------------------------------
# Accessors (note: all accessors of member data can potentially change the
# python object referenced to). See NB below.

 def get_name(self):
  root = self.__tree.getroot()
  return root.get('name').strip()

 def GetTimeUnit(self):
  root = self.__tree.getroot()
  timeNode = root.find('time')
  return timeNode.get('unit').strip()

 def GetNVariables(self):
  root = self.__tree.getroot()
  varNodes = root.findall('var')
  return len(varNodes)

 def GetVariableNames(self):
  names = list()
  root = self.__tree.getroot()
  varNodes = root.findall('var')
  for v in varNodes:
    name = v.get('name').strip()
    names.append(name)
  return names

 def GetVariables(self):
  variables = dict() # variables[(name,unit,timeUnit,legend)] = [(time,val),(time,val),..,]
  root = self.__tree.getroot()
  timeNode = root.find('time')
  timeUnit = timeNode.get('unit').strip()
  varNodes       = root.findall('var')
  timeStampNodes = root.findall('timeStamp')
  for ivar in range(len(varNodes)):
    name   = varNodes[ivar].get('name').strip()
    unit   = varNodes[ivar].get('unit').strip()
    legend = varNodes[ivar].get('legend').strip()
    scale  = varNodes[ivar].get('scale')
    if scale is None: 
      spec   = (name,unit,timeUnit,legend,'linear')
    else:
      scale  = scale.strip()
      assert scale == 'log' or scale == 'linear' or scale == 'log-log' or \
             scale == 'linear-linear' or scale == 'log-linear' or \
             scale == 'linear-log' 
      spec   = (name,unit,timeUnit,legend,scale)
    timeValues = list()
    for ts in timeStampNodes:
      time = float(ts.get('value').strip())
      if time >= self.__initialTime and time <= self.__finalTime:
        data = ts.text.strip().split(',')
        assert len(data) >= 1, 'empty data field in the %r variable; stop.' % name
# Accept missing data and fill in as zero; or neglect excess of data
#        if ivar == 0: 
#           assert len(data) == len(varNodes), '# variables %r != # values %r' % (len(data),len(varNodes))
        if len(data) >= len(varNodes):
           timeValues.append( (time, float(data[ivar])) )
        else:
           timeValues.append( (time, float(0.0)) )
    variables[spec] = timeValues

  return variables

#*********************************************************************************
# Private helper functions (internal use: __)

 def __read_xml(self):

  s = 'TimeSequence::__read_xml(): try reading: '+ self.__fileName
  self.log.debug(s)

  found = False

  while found is False:

    try:
      mutex = Lock()
      mutex.acquire()
      tree = ElementTree.parse( self.__fileName )
    except ElementTree.ParseError as error:
      mutex.release()
      s = 'TimeSequence(): '+self.__fileName+' unavailable. Error code: '+str(error.code)+'; File position: '+str(error.position)+'. Retrying...'
      self.log.debug(s)
      time.sleep(0.1)
      continue

    mutex.release()
    self.__tree = tree
    rootNode = self.__tree.getroot()
    assert rootNode.tag == 'time-sequence', 'invalid format.'
  
    node = rootNode.find('time')
    timeUnit = node.get('unit').strip()

    # (cut-off) legacy stuff
    timeCutOff = node.get('cut-off')
    if timeCutOff is not None: 
      timeCutOff = float(timeCutOff.strip())
      if self.__finalTime > timeCutOff: return

    nodes = rootNode.findall('timeStamp')

    for n in nodes:

      timeStamp = float(n.get('value').strip())

      if timeStamp == self.__finalTime: return

  # end of while found is False

  return 
#---------------------- end def __read_xml():-------------------------------------
