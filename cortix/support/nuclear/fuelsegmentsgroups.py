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
'''
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

Fuel segment

VFdALib support classes

Sat Jun 27 14:46:49 EDT 2015
'''
#*********************************************************************************
import os
import sys
import io
import time
import datetime
import math
import random

from cortix.support.nuclear.fuel_segment import FuelSegment
#*********************************************************************************

class FuelSegmentsGroups():
    '''
    Creates a dictionary of lists of fuel segment objects, with the keys
    typically being timestamps. Each fuel segment object has two data members,
    a `Pandas` Series for geometry spec and a panda DataFrame for property
    density.
    '''

#*********************************************************************************
# Construction
#*********************************************************************************

    def __init__(self,
                 key=None,
                 fuelSegments=None
                 ):

        # constructor
        # FuelSegmentsGroups simply encapsulates a dictionary of a list of
        # FuelSegment objects. The key is typically a time stamp.
        # A FuelSegment object has two data members, a pandas Series for geometry spec
        # and a pandas DataFrame for property density.

        # This is the central member data
        self.groups = dict()

        assert key not in self.groups.keys()

        if fuelSegments is not None:
            assert isinstance(fuelSegments, list)
            assert isinstance(fuelSegments[-1], FuelSegment)
            self.groups[key] = fuelSegments
        else:
            self.groups[key] = list()

        return

#*********************************************************************************
# Public Member Functions
#*********************************************************************************

    def HasGroup(self, key):

        '''
        Checks if the specified key has a group of fuel segments associated
        with it.

        Parameters
        ----------
        key: str

        Returns
        -------
        key: str
        '''

        return key in self.groups.keys()

    def AddGroup(self, key, fuelSegments=None):

        '''
        Appends the dictionary with a new key and associated list of
        fuelSegments. If the specified key is already present in the
        dictionary, then the specified list of fuel segments will be appended
        to the list of fuel segments already associated with the specified key.

        Parameters
        ----------
        key: str
        fuelSegments: list
        '''

        self.__AddGroup(key, fuelSegments)

        return

    def GetAttribute(self, groupKey=None, attributeName=None,
                     nuclideSymbol=None, nuclideSeries=None):

        '''
        Returns the average value of an attribute amongst all elements in a
        group (WARNING: keys with no values associated with them will lower
        this average!). If groupKey is not specified, the function will return
        the average attribute value of every fuel segment element in the
        entire dictionary. If attribute is not specified, the function call
        will fail. If the key value specified does not match any keys in the
        dictionary, the function will return a value of 0.

        Parameters
        ----------
        groupKey: str
        attributeName: str
        nuclideSymbol: str
        nuclideSeries: str

        Returns
        -------
        groupAttribute: float
        '''

        return self.__GetGroupAttribute(
            groupKey, attributeName, nuclideSymbol, nuclideSeries)

    def GetFuelSegments(self, groupKey=None):

        '''
        Returns a list of fuel segments associated with a specified groupkey.
        If no group key is specified, then all elements in the dictionary
        will be returned. If the specified group key does not exist, then the
        function will return an empty list.

        Parameters
        ----------
        groupKey: str

        Returns
        ----------
        fuelSegments: list
        '''

        return self.__GetFuelSegments(groupKey)

    def RemoveFuelSegment(self, groupKey, fuelSegment):

        '''
        Removes a fuel segment from a list associated with a specified group
        key. If the specified group key or fuel segment do not exist, the
        function will fail.

        Parameters
        ----------
        groupKey: str
        fuelSegment: str

        Returns
        -------
        empty:
        '''

        return self.__RemoveFuelSegment(groupKey, fuelSegment)

# def __str__( self ):
#     s = ' %5s %5s %5s '+' molar mass: %6s '+' molar cc: %6s '+' mass cc: %6s '+' flag: %s '+'# atoms: %s'+' atoms: %s\n'
#     return s % (self.name, self.formula, self.phase, self.molarMass, self.molarCC, self.massCC, self.flag, self.nAtoms, self.atoms)
#
# def __repr__( self ):
#     s = ' %5s %5s %5s '+' molar mass: %6s '+' molar cc: %6s '+' mass cc: %6s '+' flag: %s '+'# atoms: %s'+' atoms: %s\n'
#     return s % (self.name, self.formula, self.phase, self.molarMass, self.molarCC, self.massCC, self.flag, self.nAtoms, self.atoms)

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

# If an attibute is not found, Return 0 even if a groupKey is not found
# Don't change this behavior; it will break user's code.

    def __GetGroupAttribute(self, groupKey=None,
                            attributeName=None, symbol=None, series=None):

        '''
        Returns the cumulative or average densities of all fuel segments in all
        groups. Use this function with discretion, as groups with no segments
        will reduce the average density value.

        Parameters
        ----------
        groupKey: str
        attributeName: str
        symbol: str
        series: list

        Returns
        -------
        attribute: float
        '''

        assert attributeName is not None, 'fatal.'

        attribute = None

        if groupKey is None:

            attribute = 0

            for (key, fuelSegments) in self.groups.items():
                assert isinstance(fuelSegments, list), 'fail.'
                if len(fuelSegments) == 0:
                    continue  # this will reduce the average value
                groupAttribute = 0
                for fuelSegment in fuelSegments:
                    groupAttribute += fuelSegment.get_attribute(
                        attributeName, symbol, series)

                if attributeName[-4:] == 'Dens' or attributeName[-2:] == 'CC':
                    groupAttribute /= len(fuelSegments)
                attribute += groupAttribute

            if attribute != 0 and \
               (attributeName[-4:] == 'Dens' or attributeName[-2:] == 'CC'):
                attribute /= len(self.groups)

#     if attributeName[-4:] == 'Dens' or attributeName[-2:] == 'CC':
#        print('HELLO density '+attributeName+' ', attribute)

        # Get average property in all fuel segments within a groupKey
        else:

            if groupKey not in self.groups.keys():
                return 0

            fuelSegments = self.groups[groupKey]

            if len(fuelSegments) is 0:
                return 0

            attribute = 0

            for fuelSegment in fuelSegments:
                attribute += fuelSegment.get_attribute(
                    attributeName, symbol, series)

            if attribute != 0 and \
               (attributeName[-4:] == 'Dens' or attributeName[-2:] == 'CC'):
                attribute /= len(fuelSegments)

        return attribute

    def __GetFuelSegments(self, groupKey=None):

        '''
        Returns a list of fuel segments associated with a given group
        (if groupKey is specified), or an ordered list of pairs of all
        segments in all groups and their keys. [ (timeStamp, fuelSegment),
        (timeStamp, fuelSegment), ..]. If the specified groupKey does not
        exist, this function will return an empty list.

        Parameters
        ----------
        groupKey: str

        Returns
        -------
        sorted_data: type or self.groups[groupKey]: type or list(): list
        '''

        if groupKey is None:  # return an ordered list of all fuelSegments

            tmp = list()
            timeStamp = list()
            for (key, fuelSegments) in self.groups.items():
                if fuelSegments is None:
                    continue
                tmp += fuelSegments
                # all fuel segments in the group have
                timeStamp += [key for i in fuelSegments]
                # the same time stamp

            # sort fuelSegments in order of their keys
            data = zip(timeStamp, tmp)  # this is a list of pairs
            sorted_data = sorted(
                data, key=lambda entry: entry[0], reverse=False)
            #tmp = [ y for (x,y) in sorted_data ]  # oldest first
            return sorted_data

        else:

            if groupKey not in self.groups.keys():
                return list()

            return self.groups[groupKey]

    def __AddGroup(self, groupKey, fuelSegments=None):

        '''
        If a list of fuel segments and a group key is specified, the
        fuelSegment list is appended to the specified groupKey. If the groupKey
        specified does not already exist, a new one is created and the
        fuelSegments list is appended to it. fuelSegments is ALWAYS a list,
        and may be empty. A group will ALWAYS have a  fuelSegments list.

        Parameters
        ----------
        groupKey: str
        fuelSegments: list
        '''

        if fuelSegments is None:
            fuelSegments = list()
        else:
            assert isinstance(fuelSegments, list), 'fail.'

        if groupKey in self.groups.keys():
            self.groups[groupKey] += fuelSegments
        else:
            self.groups[groupKey] = fuelSegments

        return

    def __RemoveFuelSegment(self, groupKey, fuelSegment_remove):

        '''
        Removes a fuel segment from a list associated with a specified group
        key. If the specified group key or fuel segment do not exist, the
        function will fail.

        Parameters
        ----------
        groupKey: str
        fuelSegment: str
        '''

        assert groupKey in self.groups.keys(), 'fail.'

        fuelSegments = self.groups[groupKey]
        nSegments = len(fuelSegments)

        for fuelSegment in fuelSegments:
            if fuelSegment.get_attribute(
                    'segmentId') == fuelSegment_remove.get_attribute('segmentId'):
                fuelSegments.remove(fuelSegment)

        assert len(self.groups[groupKey]) == nSegments - 1, 'fatal.'

        return

#========================= end class FuelSegmentsGroups ==========================
