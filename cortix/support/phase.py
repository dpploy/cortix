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
Phase *history* container. When you think of a phase value, think of that value at
a specific point in time. This container holds the historic data of a phase;
its species and quantities. This implementation treats access of time stamps within
a tolerance. All searches for time stamped values are subjected to an approximation
of the time stamp to avoid storing values too close to each other in time, and/or to
return the closest value in time searched or no value if none can be found according
to the tolerance.

Background
----------
TODO: ATTENTION:
The species (list of Specie) AND quantities (list of Quantity) data members
have ARBITRARY density values either at an arbitrary point in the history or at
no point in the history. This needs to be removed in the future to avoid confusion.

To obtain history values, associated to the phase, at a particular point in time,
use the GetValue() method to access the history data frame (pandas) via columns and
rows. ALERT: The corresponding values in species and quantities are OVERRIDEN and NOT to
be used through the phase interface.

Author: Valmor F. de Almeida dealmeidav@ornl.gov; vfda
Sat Sep  5 01:26:53 EDT 2015

Cortix: a program for system-level modules coupling, execution, and analysis.
'''
#*********************************************************************************
import os
import sys
from copy import deepcopy
import numpy as npy
import pandas

from cortix.support.specie   import Specie
from cortix.support.quantity import Quantity
#*********************************************************************************

class Phase:
    '''
    Phase `history` container. A `Phase` consists of `Species` and `Quantities`
    varying with time. This container is meant to reproduce the basic idea of a
    material phase.
    '''

#*********************************************************************************
# Construction
#*********************************************************************************

    def __init__(self,
                 time_stamp = None,
                 time_unit  = None,
                 species    = None,
                 quantities = None
                ):
        #TODO
        '''
        Sometimes an empty Phase object is created by user code. This case needs
        adequate logic for None types.
        Note on usage: when passing quantities, do set the value argument explicitly
        to help define the type and avoid SetValue() errors with Pandas. This is
        to be investigated later. Also, the usage of a DataFrame needs to be re-evaluated.
        Maybe better to use a Quantity object and a Specie object with a Pandas Series
        history as a value to avoid the existance of a value in Quantity and a value
        in Phase that are not in sync.
        '''

        if time_stamp is None:
            time_stamp = 0.0 # default type is float
        else:
            assert isinstance(time_stamp, float)
            self.__time_stamp = time_stamp

        if time_unit is None:
            self.__time_unit = 's' # second
        else:
            assert isinstance(time_unit, str)
            self.__time_unit = time_unit

        if species is not None:
            assert isinstance(species, list)
            for specie in species:
                assert isinstance(specie, Specie)

        if quantities is not None:
            assert isinstance(quantities, list)
            for quant in quantities:
                assert isinstance(quant, Quantity)

        # List of species and quantities objects; columns of data frame are named
        # by objects.
        # A new object held by a Phase() object
        self.__species = deepcopy(species)
        # A new object held by a Phase() object
        self.__quantities = deepcopy(quantities)

        names = list()

        if species is not None:
            for specie in self.__species:
                names.append(specie.name)
                specie.massCC = 0.0  # clear these values
                                     # todo: eliminate them from Specie in the future

        if quantities is not None:
            for quant in self.__quantities:
                names.append(quant.name)
                quant.value = 0.0    # clear these values
                                     # todo: eliminate them from Quantity in the future

        # Table data phase without data type assigned; this is left to the user
        # Time stamps will always be float or int
        self.__phase = pandas.DataFrame( index=[float(time_stamp)], columns=names )

        if species is not None:
            for specie in species:
                self.__phase.loc[time_stamp, specie.name] = specie.molarCC

        if quantities is not None:
            for quant in quantities:
                self.__phase.loc[time_stamp, quant.name] = quant.value
                #self.__phase.fillna( 0.0, inplace=True )  # dtype defaults to float

        return

#*********************************************************************************
# Public member functions
#*********************************************************************************

    def has_time_stamp(self, try_time_stamp):
        '''
        Checks to see if try_time_stamp exists in the phase history.

        Parameters
        ----------
        try_time_stamp:
        '''


        time_stamp = self.__get_time_stamp( try_time_stamp )

        if time_stamp is not None:
            return True
        else:
            return False

    def __get_time_unit(self):
        '''
        Returns the time unit of the `Phase.`

        Returns
        -------
        time_unit: str
        '''

        return self.__time_unit
    time_unit = property(__get_time_unit,None,None,None)

    def GetTimeStamps(self):
        '''
        Returns a list of all the time stamps in the phase history.

        Returns
        -------
        timeStamps: list
        '''

        return list(self.__phase.index)  # return all time stamps
    timeStamps = property(GetTimeStamps, None, None, None)

    def __get_time_stamps(self):
        '''
        Get all time stamps in the index of the data frame.

        Returns
        -------
        time_stamps: list
        '''

        return list(self.__phase.index)  # return all time stamps
    time_stamps = property(__get_time_stamps, None, None, None)

    def GetSpecies(self):
        '''
        Returns every single species in the phase history.

        Returns
        -------
        species: list
        '''

        for species in self.__species:
          tmp = self.GetSpecie(species.name) # handy way to synchronize the whole list
        return self.__species
    species = property(GetSpecies, None, None, None)

    def GetQuantities(self):
        '''
        Returns the list of `Quantities`. The values in each `Quantity` are
        synchronized with the `Phase` data frame.

        Returns
        -------
        quantities: list
        '''

        for quant in self.__quantities:
          tmp = self.GetQuantity(quant.name) # handy way to synchronize the whole list
        return self.__quantities
    quantities = property(GetQuantities, None, None, None)

    def GetActors(self):
        '''
        Returns a list of all the actors in the phase history.

        Returns
        -------
        list(self.__phase.colums): list
        '''

        return list(self.__phase.columns)  # return all names in order

    def GetSpecie(self, name):
        '''
        Returns the species specified by name if it exists, or none if it
        doesn't.

        Parameters
        ----------
        name: str

        Returns
        -------
        specie: str
        '''

        for specie in self.__species:
            if specie.name == name:
                time_stamp = self.__get_time_stamp( None ) # get latest time stamp
                assert name in self.__phase.columns, 'name %r not in %r'% \
                   (name,self.__phase.columns)
                specie.massCC = self.__phase.loc[time_stamp, name]
                return specie  # return specie syncronized with the phase
        return None

    def SetSpecieId(self, name, val):
        '''
        Sets the flag of a specie "name" equal to val.

        Parameters
        ----------
        name: str
        val: int
        '''

        for specie in self.__species:
            if specie.name == name:
                specie.flag = val
                return

    def GetQuantity(self, name):
        '''
        Returns the quantity evaluated at the last time step of the phase
        history. This also updates the value of the quantity object. If the
        quantity name does not exist the return is None.

        Parameters
        ----------
        name: str
        '''

        for quant in self.__quantities:
            if quant.name == name:
                time_stamp = self.__get_time_stamp( None ) # get latest time stamp
                assert name in self.__phase.columns, 'name %r not in %r'%\
                   (name,self.__phase.columns)
                quant.value = self.__phase.loc[time_stamp, name]
                return quant  # return quantity syncronized with the phase

        return None

    def get_quantity(self, name, try_time_stamp=None):
        '''
        New version.
        Get the quantity `name` at a point in time closest to
        `try_time_stamp` up to a tolerance. If no time stamp is passed, the
        whole history is returned.

        Parameters
        ----------
        name: str
        try_time_stamp: float, int or None
            Time stamp of desired quantity value. Default: None returns the
            whole quantity history.

        Returns
        -------
        quant.value: float or int or other
        '''

        assert name in self.__phase.columns, 'name %r not in %r'%\
                (name,self.__phase.columns)

        time_stamp = self.__get_time_stamp( try_time_stamp )

        for quant in self.__quantities:
            if quant.name == name:
                quant.value = self.__phase.loc[time_stamp, name] # labels' access mode
                return quant  # return quantity syncronized with the phase

    def get_quantity_history(self, name):
        '''
        Create a Quantity `name` history. This will create a fully qualified
        Quantity object and return to the caller. The function is typically
        needed for data output to a file through `pickle`. Since the value
        attribute of a quantity can be any data structure, a time-series is
        built on the fly and stored in the value attribute. In addition the
        time unit is added to the final return value as a tuple.

        Parameters
        ----------
        name: str

        Returns
        -------
        quant_history: tuple(Quantity,str)
        '''

        assert name in self.__phase.columns, 'name %r not in %r'%\
                (name,self.__phase.columns)

        for quant in self.__quantities:
            if quant.name == name:
                quant_history = deepcopy(quant)
                quant_history.value = self.__phase[name] # whole data frame index series
                return (quant_history,self.__time_unit) # return tuple

    def AddSpecie(self, new_specie):
        '''
        Adds a new specie object to the phase history. See species.py for
        more details on the specie class.

        Parameters
        ----------
        new_specie: obj
        '''

        assert isinstance(new_specie, Specie)
        assert new_specie.name not in list(self.__phase.columns), \
               'new_specie: %r exists. Current names: %r' % \
               (new_specie, self.__phase.columns)
        speciesFormulae = [specie.formula_name for specie in self.__species]
        assert new_specie.formula_name not in speciesFormulae
        self.__species.append(new_specie)
        newName = new_specie.name
        col = pandas.DataFrame( index=list(self.__phase.index), columns=[newName] )
        tmp = self.__phase
        df = tmp.join(col, how='outer')
        self.__phase = df.fillna(0.0)   # for species have float as default

    def AddQuantity(self, newQuant):
        '''
        Adds a new quantity object to the dataframe. See quantity.py for more
        details on the quantity class.

        Parameters
        ----------
        newQuant: object
        '''

        assert isinstance(newQuant, Quantity)
        assert newQuant.name not in list(self.__phase.columns), \
               'quantity: %r exists. Current names: %r' % \
               (newQuant, self.__phase.columns)
        quantFormalNames = [quant.formalName for quant in self.__quantities]
        assert newQuant.formalName not in quantFormalNames
        self.__quantities.append(newQuant)
        newName = newQuant.name

        # create a col with object data type; user must fill out column
        col = pandas.DataFrame( index=list( self.__phase.index), columns=[newName],
                                dtype=object )
        tmp = self.__phase
        df  = tmp.join(col, how='outer')
        #self.__phase = df.fillna(newQuant.value)

    def AddRow(self, try_time_stamp, row_values):
        '''
        Adds a row to the dataframe, with a timestamp of try_time_stamp and
        row values equal to row_values. Take care that the dimensions and order
        of the data matches up!

        Parameters
        ----------
        try_time_stamp: float
        row_values: list
        '''

        assert try_time_stamp not in self.__phase.index, 'already used time_stamp: %r'%\
                (try_time_stamp)
        assert isinstance(row_values, list)

        time_stamp = self.__get_time_stamp( try_time_stamp )
        assert time_stamp is None, 'already used time_stamp: %r'%(try_time_stamp)
        time_stamp = try_time_stamp

        assert len(row_values) == self.__phase.columns.size

        # create a row with object data type; users row_values data define data type
        row = pandas.DataFrame( index=[time_stamp],
                                columns=list( self.__phase.columns ), dtype=object )

        for (col,v) in zip(row.columns, row_values):
            row.loc[time_stamp,col] = v

        frames = [self.__phase, row]
        self.__phase = pandas.concat(frames)
        return

    def GetRow(self, try_time_stamp=None):
        '''
        Returns an entire row of the phase dataframe. A row is a series of
        values that are all at the same time stamp.

        Parameters
        ----------
        try_time_stamp: float

        Returns
        -------
        list(self.__phase.loc[time_stamp, :]): list
        '''

        time_stamp = self.__get_time_stamp( try_time_stamp )
        assert time_stamp is not None, 'missing try_time_stamp: %r'%(try_time_stamp)
        return list(self.__phase.loc[time_stamp, :])

    def GetColumn(self, actor):
        '''
        Returns an entire column of data. A column is the entire history
        of data associated with a specific actor.

        Parameters
        ----------
        actor: str

        Returns
        -------
        list(self.__phase.loc[:, actor]): list
        '''

        assert isinstance(actor, str)
        assert actor in self.__phase.columns, 'actor %r not in %r'% \
                   (actor,self.__phase.columns)
        return list(self.__phase.loc[:, actor])

    def ScaleRow(self, try_time_stamp, value):
        '''
        Multiplies all of the data in a row (except time stamp) by a scalar
        value.

        Parameters
        ----------
        try_time_stamp: float
        value: float
        '''

        assert isinstance(try_time_stamp, int) or isinstance(try_time_stamp, float)
        time_stamp = self.__get_time_stamp( try_time_stamp )
        assert time_stamp is not None, 'missing try_time_stamp: %r'%(try_time_stamp)
        assert isinstance(value, int) or isinstance(value, float)
        self.__phase.loc[time_stamp, :] *= value
        return

    def ClearHistory(self, value=0.0):
        '''
        Set species and quantities of history to a given value
        (default to zero value), all time stamps are preserved.

        Parameters
        ----------
        value: float
        '''

        assert isinstance(value, int) or isinstance(value, float)
        self.__phase.loc[:, :] = value

        return

    def ResetHistory(self, try_time_stamp=None, value=None):
        '''
        Set species and quantities of history to a given value
        (default to zero value) only one time stamp is preserved (default to
        last time stamp).

        Parameters
        ----------
        try_time_stamp: float
        value: float
        '''

        if value is not None:
           assert isinstance(value, int) or isinstance(value, float) or \
                  isinstance(value, npy.ndarray)

        if try_time_stamp is not None:
           assert isinstance(try_time_stamp, int) or isinstance(try_time_stamp, float)

        time_stamp = self.__get_time_stamp( try_time_stamp )
        assert time_stamp is not None, 'missing try_time_stamp: %r'%(try_time_stamp)

        values = self.GetRow(time_stamp)  # save values

        columns = list(self.__phase.columns)
        assert len(columns) == len(values), 'FATAL: oops internal error.'

        self.__phase = pandas.DataFrame( index=[time_stamp], columns=columns )
        self.__phase.fillna( 0.0, inplace=True )

        if value is None:
            for v in values:
                idx = values.index(v)
                self.__phase.loc[time_stamp, columns[idx]] = v  # restore values
        else:
            self.__phase.loc[time_stamp, :] = value   # set user-given value

        return

    def GetValue(self, actor, try_time_stamp=None):
        '''
        Deprecated: use get_value()
        '''

        assert isinstance(actor, str)
        assert actor in self.__phase.columns, 'actor %r not in %r'% \
                   (actor,self.__phase.columns)

        if try_time_stamp is not None:
           assert isinstance(try_time_stamp, int) or isinstance(try_time_stamp, float)

        time_stamp = self.__get_time_stamp( try_time_stamp )
        assert time_stamp is not None, 'missing try_time_stamp: %r'%(try_time_stamp)

        return self.__phase.loc[time_stamp, actor]

    def get_value(self, actor, try_time_stamp=None):
        '''
        Returns the value associated with a specified actor at a specified
        time stamp.

        Parameters
        ----------
        actor: str
        try_time_stamp: float

        Returns
        -------
        self.__phase.loc[time_stamp, actor]: float
        '''

        assert isinstance(actor, str)
        assert actor in self.__phase.columns, 'actor %r not in %r'% \
                   (actor,self.__phase.columns)

        if try_time_stamp is not None:
           assert isinstance(try_time_stamp, int) or isinstance(try_time_stamp, float)

        time_stamp = self.__get_time_stamp( try_time_stamp )
        assert time_stamp is not None, 'missing try_time_stamp: %r'%(try_time_stamp)

        return self.__phase.loc[time_stamp, actor]

    def SetValue(self, actor, value, try_time_stamp=None):
        '''
        For the record: old def SetValue(self, time_stamp, actor, value):

        Parameters
        ----------
        actor: str
        value: float
        try_time_stamp: float
        '''

        assert isinstance(actor, str)
        assert actor in self.__phase.columns

        #assert isinstance(value, int) or isinstance(value, float) or \
        #       isinstance(value, npy.ndarray)

        if try_time_stamp is not None:
           assert isinstance(try_time_stamp, int) or isinstance(try_time_stamp, float)

        time_stamp = self.__get_time_stamp( try_time_stamp )
        assert time_stamp is not None, 'missing try_time_stamp: %r'%(try_time_stamp)

        #print('*value =', value)
        #print('*type(value) =', type(value))
        #print('*time_stamp =', time_stamp)
        #print('*actor =', actor)
        #print('*column values =', self.__phase[actor])
        #print('*df =', self.__phase)
        #print('*df.dtypes =', self.__phase.dtypes)
        #print('*df.shape =', self.__phase.shape)
        #print('')
        #if isinstance(value,npy.ndarray):
        #   self.__phase[actor] = self.__phase.astype({actor:type(value)})
        #print('*df.dtypes =', self.__phase.dtypes)
        #print('')

        # Note: user value could have a different type than other column values.
        # If there is a type change, this will not be checked; user has been advised.
        self.__phase.loc[time_stamp, actor] = value

        return

    def set_value(self, actor, value, try_time_stamp=None):
        '''
        New version. Discontinue using SetValue()
        '''
        assert isinstance(actor, str)
        assert actor in self.__phase.columns

        if try_time_stamp is not None:
           assert isinstance(try_time_stamp, int) or isinstance(try_time_stamp, float)

        time_stamp = self.__get_time_stamp( try_time_stamp )
        assert time_stamp is not None, 'missing try_time_stamp: %r'%(try_time_stamp)

        # Note: user value could have a different type than other column values.
        # If there is a type change, this will not be checked; user has been advised.
        self.__phase.loc[time_stamp, actor] = value

        return

    def WriteHTML(self, fileName):
        '''
        Convert the `Phase` container into an HTML file.

        Parameters
        ---------
        fileName: str
        '''

        assert isinstance(fileName, str)
        tmp = pandas.DataFrame(self.__phase)
        columnNames = tmp.columns
        speciesNames = [specie.name for specie in self.__species]
        quantityNames = [quantity.name for quantity in self.__quantities]
        for col in columnNames:
            if col in speciesNames:
                idx = speciesNames.index(col)
                specie = self.__species[idx]
                tmp.rename(columns={col: specie.formula_name}, inplace=True)
            elif col in quantityNames:
                idx = quantityNames.index(col)
                quant = self.__quantities[idx]
                tmp.rename( columns={ col: col + '[' + quant.unit + ']'},
                            inplace=True )
            else:
                assert False, 'oops fatal.'

        tmp.to_html(fileName)

        return

    def __str__(self):
        s = '\n\t **Phase()**: \n\t time unit: %s\n\t *quantities*: %s\n\t *species*: %s\n\t *history* #time_stamp=%s\n\t *history end* @%s\n%s'
        return s % (self.__time_unit,self.__quantities, self.__species, len(self.__phase.index),
                    self.__phase.index[-1], self.__phase.loc[self.__phase.index[-1], :])

    def __repr__(self):
        s = '\n\t **Phase()**: \n\t time unit: %s\n\t *quantities*: %s\n\t *species*: %s\n\t *history* #time_stamp=%s\n\t *history end* @%s\n%s'
        return s % (self.__time_unit,self.__quantities, self.__species, len(self.__phase.index),
                    self.__phase.index[-1], self.__phase.loc[self.__phase.index[-1], :])

#*********************************************************************************
# Private helper functions (internal use: __)
#*********************************************************************************

    def __get_time_stamp(self, try_time_stamp=None):
        '''
        Helper method for finding the closest time stamp to `try_time_stamp`
        in the phase history. The pandas index container used for storing
        float data type time stamps will return the nearest time stamp up to a
        tolerance. Whether the time index has one value, this function will
        inspect for the proximity to that value.

        Parameters
        ----------
        try_time_stamp: float, int or None
            Default: None will return the last time stamp.

        Returns
        -------
        self.__phase.index[loc]: float or None
            Will return None if no time stamp within tolerance is found.
        '''

        import numpy as np

        tol = 1.0e-3

        if try_time_stamp is None:
            return self.__phase.index[-1]
        else:
            time_stamps = np.array(self.__phase.index)
            if time_stamps.size >= 2:
               tol = 1.0e-3 * np.diff(time_stamps).mean() # 1e-3 * the mean delta t
            try: # abs(index_value - try_time_stamp) <= tolerance
                loc = self.__phase.index.get_loc( try_time_stamp, method='nearest',
                        tolerance=tol )
            except KeyError: # no value found withing tol
                return None
            else:
                return  self.__phase.index[loc]

#======================= end class Phase =========================================
