#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
import pandas
#import matplotlib
#matplotlib.use('Agg', warn=False)
import matplotlib.pyplot as plt

class Quantity:
    """
    todo: this probably should not have a "value" for the same reason as Species.
          this needs some thinking.
    well not so fast. This can be used to build a quantity with anything as a
    value. For instance a history of the quantity as a time series.

    """
    def __init__(self,
                 name = 'null-quantity-name',
                 formalName = 'null-quantity-formal-name', # deprecated
                 formal_name = 'null-quantity-formal-name',
                 latex_name = 'null-quantity-latex-name',
                 value = float(0.0),      # this can be any type
                 unit = 'null-quantity-unit',
                 info = 'null-quantity-info'
                ):

        assert isinstance(name, str), 'not a string.'
        self.__name = name

        assert isinstance(formalName, str), 'not a string.'
        self.__formalName = formalName  # deprecated
        self.__formal_name = formalName

        assert isinstance(formal_name, str), 'not a string.'
        self.__formal_name = formal_name

        assert isinstance(latex_name, str), 'not a string.'
        self.__latex_name = latex_name

        self.__value = value

        assert isinstance(name, str), 'not a string.'
        self.__unit = unit

        self.__name = name
        self.__value = value
        self.__unit = unit

        self.__info = info # info text such as technical name or other properties info

        return

    def SetName(self, n):
        '''
        Sets the name of the quantity in question to n.

        Parameters
        ----------
        n: str
        '''
        self.__name = n
    def get_name(self):
        '''
        Returns the name of the quantity.

        Returns
        -------
        name: str
        '''

        return self.__name
    name = property(get_name, SetName, None, None)

    def SetValue(self, v):
        '''
        Sets the numerical value of the quantity to v.

        Parameters
        ----------
        v: float

        '''
        self.__value = v
    def GetValue(self):
        '''
        Gets the numerical value of the quantity.

        Returns
        -------
        value: any type

        '''
        return self.__value
    value = property(GetValue, SetValue, None, None)

    def SetFormalName(self, fn):

        '''
        Sets the formal name of the property to fn.

        Parameters
        ----------
        fn: str
        '''

        self.__formalName = fn
        self.__formal_name = fn
    def GetFormalName(self):
        '''
        Returns the formal name of the quantity.

        Returns
        -------
        formalName: str
        '''

        #return self.__formalName
        return self.__formal_name
    formalName = property(GetFormalName, SetFormalName, None, None)
    formal_name = property(GetFormalName, SetFormalName, None, None)

    def set_latex_name(self, ln):

        '''
        Sets the LaTeX name of the property to ln.

        Parameters
        ----------
        ln: str
        '''

        self.__latex_name = ln
    def get_latex_name(self):
        '''
        Returns the formal name of the quantity.

        Returns
        -------
        formalName: str
        '''

        return self.__latex_name
    latex_name = property(get_latex_name, set_latex_name, None, None)

    def set_info(self, ln):

        '''
        Sets the LaTeX name of the property to ln.

        Parameters
        ----------
        ln: str
        '''

        self.__latex_name = ln
    def get_info(self):
        '''
        Returns the formal name of the quantity.

        Returns
        -------
        formalName: str
        '''

        return self.__info
    info = property(get_info, set_info, None, None)

    def SetUnit(self, f):
        '''
        Sets the units of the quantity to f (for example, density would be in
        units of g/cc.

        Parameters
        ----------
        f: str
        '''

        self.__unit = f
    def GetUnit(self):
        '''
        Returns the units of the quantity.

        Returns
        -------
        unit: str
        '''

        return self.__unit
    unit = property(GetUnit, SetUnit, None, None)

    def plot(self, x_scaling=1, y_scaling=1, title=None, x_label='x', y_label=None,
            file_name=None, same_axis=True, dpi=300):
        '''
        This will support a few possibities for data storage in the self.__value
        member.

        Pandas Series. If self.__value is a Pandas Series, plot against the index.
        However the type stored in the Series matter. Suppose it is a series
        of a `numpy` array. This must be of the same rank for every entry.
        This plot method assumes it is an iterable type of the same length for every
        entry in the series. A plot of all elements in the type against the index of
        the series will be made. The plot may have all elements in one axis or
        each element in its own axis.
        '''

        plt.clf()
        plt.cla()
        plt.close()

        if not isinstance(self.__value, pandas.core.series.Series):
            return
        if len(self.__value) == 1:
            return

        if not title:
            title = self.info
        if not y_label:
            if self.latex_name != 'null-quantity-latex-name':
                y_label = self.latex_name
            elif self.formal_name != 'null-quantity-formal-name':
                y_label = self.formal_name
            elif self.name != 'null-quantity-name':
                y_label = self.name
            else:
                assert False

        if isinstance(self.__value[0],float) or isinstance(self.__value[0],int) \
                or isinstance(self.__value[0],bool):
            n_dim = 1
            # Turn series of values into a series of a list of one value to allow for
            # the indexing below
            for i in range (len(self.__value[:])):
                self.__value.iat[i] = [ self.__value.iat[i] ]  # list of one element
        else:
           n_dim = len(self.__value[0])

        x = [i*x_scaling for i in self.__value.index]
        #x = self.__value.index # potential bug in matplotlib

        if same_axis:
            fig = plt.figure(self.__formal_name)
        for i in range(n_dim):
            if not same_axis:
                fig = plt.figure(self.__formal_name+str(i))
            y = list()
            for j in range(len(x)):
                y.append( self.__value.iat[j][i] ) # must use iat()

            y = [k*y_scaling for k in y]

            plt.xlabel(x_label)
            plt.ylabel(y_label)

            plt.title(title)

            plt.plot(x, y)

            if not same_axis and file_name:
                plt.savefig(file_name+str(i)+'.png', dpi=dpi)

        if same_axis and file_name:
            plt.savefig(file_name+'.png',dpi=dpi)

        return

    def __str__(self):
        '''
        Used to print the data stored by the quantity class. Will print out
        name, formal name, the value of the quantity and its unit.

        Returns
        -------
        s: str
        '''

        s = '\n\t Quantity(): \n\t name=%s; formal name=%s; latex name=%s; info=%s; value=%s[%s]'
        return s % (self.name, self.formal_name, self.latex_name, self.info, self.value, self.unit)

    def __repr__(self):
        '''
        Used to print the data stored by the quantity class. Will print out
        name, formal name, the value of the quantity and its unit.

        Returns
        -------
        s: str
        '''

        s = '\n\t Quantity(): \n\t name=%s; formal name=%s; latex name=%s; info=%s; value=%s[%s]'
        return s % (self.name, self.formal_name, self.latex_name, self.info, self.value, self.unit)
