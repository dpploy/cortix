#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/cortix/blob/master/COPYRIGHT.txt
#
# Licensed under the University of Massachusetts Lowell LICENSE:
# https://github.com/dpploy/cortix/blob/master/LICENSE.txt
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Pyplot module.

This class manages time-sequence data in XML or tabular formats.
It is a helper for reading and manipulating stored file data in Cortix.
The XML data is a ElementTree object.

Sat Jul 19 12:13:05 EDT 2014
"""
# *********************************************************************************
import os
import sys
import io
import time
import datetime
import logging
import xml.etree.ElementTree as ElementTree
from threading import Lock
# *********************************************************************************

class TimeSequence():

    def __init__(self,
                 fileName,   # full path file name
                 fileType,   # "xml"
                 initialTime=0.0,
                 finalTime=0.0,
                 time_unit=None,
                 logger=None
                 ):

        assert isinstance(fileName, str), 'wrong type; stop.'
        self.__fileName = fileName

        assert isinstance(fileType, str), 'wrong type; stop.'
        self.__fileType = fileType

        assert isinstance(initialTime, float), 'wrong type; stop.'
        self.__initialTime = initialTime

        assert isinstance(finalTime, float), 'wrong type; stop.'
        self.__finalTime = finalTime

        assert isinstance(time_unit, str), 'wrong type; stop.'
        self.__time_unit = time_unit

        assert finalTime >= initialTime, 'sanity check failed. stop.'
        assert initialTime >= 0.0, 'sanity check failed. stop.'
        assert finalTime >= 0.0, 'sanity check failed. stop.'

        assert isinstance(logger, logging.Logger), 'wrong type; stop.'
        assert logger is not None, 'must give a logger; stop.'
        self.log = logger

        self.__tree = None

        if fileType == 'xml':
            self.__read_xml()

#  s = 'TimeSequence::__init__(): built object'
#  self.log.debug(s)
# ---------------------- end def __init__():------------------------------

# ---------------------------------------------------------------------------------
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
        # variables[(name,unit,timeUnit,legend)] = [(time,val),(time,val),..,]
        variables = dict()
        root = self.__tree.getroot()
        timeNode = root.find('time')
        timeUnit = timeNode.get('unit').strip()
        varNodes = root.findall('var')
        timeStampNodes = root.findall('timeStamp')
        for ivar in range(len(varNodes)):
            name = varNodes[ivar].get('name').strip()
            unit = varNodes[ivar].get('unit').strip()
            legend = varNodes[ivar].get('legend').strip()
            scale = varNodes[ivar].get('scale')
            if scale is None:
                spec = (name, unit, timeUnit, legend, 'linear')
            else:
                scale = scale.strip()
                assert scale == 'log' or scale == 'linear' or scale == 'log-log' or \
                    scale == 'linear-linear' or scale == 'log-linear' or \
                    scale == 'linear-log'
                spec = (name, unit, timeUnit, legend, scale)
            timeValues = list()
            for ts in timeStampNodes:
                time = float(ts.get('value').strip())
                if time >= self.__initialTime and time <= self.__finalTime:
                    data = ts.text.strip().split(',')
                    assert len(
                        data) >= 1, 'empty data field in the %r variable; stop.' % name
# Accept missing data and fill in as zero; or neglect excess of data
#        if ivar == 0:
# assert len(data) == len(varNodes), '# variables %r != # values %r' %
# (len(data),len(varNodes))
                    if len(data) >= len(varNodes):
                        timeValues.append((time, float(data[ivar])))
                    else:
                        timeValues.append((time, float(0.0)))
            variables[spec] = timeValues

        return variables

# *********************************************************************************
# Private helper functions (internal use: __)

    def __read_xml(self):
        '''
        Read the xml data file recursively until the desired time stamp is found.
        '''

        s = 'TimeSequence::__read_xml(): try reading: ' + self.__fileName
        self.log.debug(s)

        found = False

        while found is False:

            try:
                mutex = Lock()
                mutex.acquire()
                tree = ElementTree.parse(self.__fileName)
            except ElementTree.ParseError as error:
                mutex.release()
                s = 'TimeSequence(): ' + self.__fileName + ' unavailable. Error code: ' + \
                    str(error.code) + '; File position: ' + \
                    str(error.position) + '. Retrying...'
                self.log.debug(s)
                time.sleep(0.1)
                continue

            mutex.release()
            self.__tree = tree
            rootNode = self.__tree.getroot()
            assert rootNode.tag == 'time-sequence', 'invalid format.'

            node = rootNode.find('time')
            timeUnit = node.get('unit').strip()

            time_unit_scale = 1.0
#            time_unit_scale = 60.0 # __get_time_unit_scale( timeUnit )

            # (cut-off) legacy stuff
            timeCutOff = node.get('cut-off')
            if timeCutOff is not None:
                timeCutOff = float(timeCutOff.strip())
                if self.__finalTime > timeCutOff:
                    return

            nodes = rootNode.findall('timeStamp')

            for n in nodes:

                timeStamp = float(n.get('value').strip())

                if abs(timeStamp - self.__finalTime) <= 1.0e-5:
                    return

        # end of while found is False

        return
# ---------------------- end def __read_xml():----------------------------
