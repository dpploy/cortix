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
Author: Valmor de Almeida dealmeidav@ornl.gov; vfda

Fuel segment

VFdALib support classes

Sat Jun 27 14:46:49 EDT 2015
"""

# *******************************************************************************
import os
import sys
import io
import time
import datetime
import math
import random

from cortix.support.fuel_segment import FuelSegment
# *******************************************************************************

# *******************************************************************************


class FuelSegmentsGroups():

    def __init__(self,
                 key=None,
                 fuelSegments=None
                 ):

        # *******************************************************************************
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

# *******************************************************************************
# Setters and Getters methods
# -------------------------------------------------------------------------------
# These are passing arguments by value effectively. Because the python objects
# passed into/out of the function are immutable.

    def HasGroup(self, key):

        return key in self.groups.keys()

    def AddGroup(self, key, fuelSegments=None):

        self.__AddGroup(key, fuelSegments)

    def GetAttribute(self, groupKey=None, attributeName=None,
                     nuclideSymbol=None, nuclideSeries=None):

        return self.__GetGroupAttribute(
            groupKey, attributeName, nuclideSymbol, nuclideSeries)

    def GetFuelSegments(self, groupKey=None):

        return self.__GetFuelSegments(groupKey)

    def RemoveFuelSegment(self, groupKey, fuelSegment):

        return self.__RemoveFuelSegment(groupKey, fuelSegment)


# *********************************************************************************


# If an attibute is not found, Return 0 even if a groupKey is not found
# Don't change this behavior; it will break user's code.
# ---------------------------------------------------------------------------------

    def __GetGroupAttribute(self, groupKey=None,
                            attributeName=None, symbol=None, series=None):

        assert attributeName is not None, 'fatal.'

        attribute = None

# Either cumulative or average density property for all fuel segments for *all* groups
# BE VERY CAREFUL HERE: groups with no segments will reduce the average
# density value
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

# *********************************************************************************

# Return the fuel segments of a given group (if the groupKey is given), otherwise
# returns an ordered list of pairs of all segments in all groups and their keys.
# That is, [ (timeStamp,fuelSegment), (timeStamp,fuelSegment), ... ]

# *ALWAYS* return the list of segments held by the group when a groupKey is given.

# If the groupKey does not exist return an empty list()
# ---------------------------------------------------------------------------------
    def __GetFuelSegments(self, groupKey=None):

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
#    tmp = [ y for (x,y) in sorted_data ]  # oldest first
            return sorted_data

        else:

            if groupKey not in self.groups.keys():
                return list()

            return self.groups[groupKey]

# *********************************************************************************

# Make fuelSegments *ALWAYS* a list (could be empty)
# If group key exists, add to group otherwise create a group
# If fuelSegments are not given, add an empty list to a group if it exists
# A group will *ALWAYS* have a fuelSegments list.

# ---------------------------------------------------------------------------------
    def __AddGroup(self, groupKey, fuelSegments=None):

        if fuelSegments is None:
            fuelSegments = list()
        else:
            assert isinstance(fuelSegments, list), 'fail.'

        if groupKey in self.groups.keys():
            self.groups[groupKey] += fuelSegments
        else:
            self.groups[groupKey] = fuelSegments

# *********************************************************************************

# ---------------------------------------------------------------------------------
    def __RemoveFuelSegment(self, groupKey, fuelSegment_remove):

        assert groupKey in self.groups.keys(), 'fail.'

        fuelSegments = self.groups[groupKey]
        nSegments = len(fuelSegments)

        for fuelSegment in fuelSegments:
            if fuelSegment.get_attribute(
                    'segmentId') == fuelSegment_remove.get_attribute('segmentId'):
                fuelSegments.remove(fuelSegment)

        assert len(self.groups[groupKey]) == nSegments - 1, 'fatal.'

# *********************************************************************************

# *******************************************************************************
# Printing of data members
# def __str__( self ):
#     s = ' %5s %5s %5s '+' molar mass: %6s '+' molar cc: %6s '+' mass cc: %6s '+' flag: %s '+'# atoms: %s'+' atoms: %s\n'
#     return s % (self.name, self.formula, self.phase, self.molarMass, self.molarCC, self.massCC, self.flag, self.nAtoms, self.atoms)
#
# def __repr__( self ):
#     s = ' %5s %5s %5s '+' molar mass: %6s '+' molar cc: %6s '+' mass cc: %6s '+' flag: %s '+'# atoms: %s'+' atoms: %s\n'
#     return s % (self.name, self.formula, self.phase, self.molarMass, self.molarCC, self.massCC, self.flag, self.nAtoms, self.atoms)
# *******************************************************************************
