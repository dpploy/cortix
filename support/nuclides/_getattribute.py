#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Nuclides container 

Thu Jun 25 18:16:06 EDT 2015
"""
#*********************************************************************************
import os, sys, io, time, datetime
import math, random

from cortix.support.periodictable import ELEMENTS
from cortix.support.periodictable import SERIES
#*********************************************************************************

# Get property either overall or on a nuclide basis 

#---------------------------------------------------------------------------------
def _GetAttribute(self, attributeName, symbol=None, series=None ):

  assert attributeName in self.attributeNames, ' attribute name: %r; options: %r; fail.' % (attributeName,self.attributeNames)

  if symbol is not None: assert series is None, 'fail.'
  if series is not None: assert symbol is None, 'fail.'

  if attributeName == 'isotopes': assert symbol is not None, 'need an element symbol.'

#.................................................................................
# isotopes python list

  if attributeName == 'isotopes': 

     nuclidesNames = self.propertyDensities.index
     isotopes = [x for x in nuclidesNames if x.split('-')[0].strip()==symbol]
     return isotopes

#.................................................................................
# nuclides python list

  if attributeName == 'nuclides': 

     if series is not None:
        # CREATE A HELPER FUNCTION FOR THIS; NOTE THIS IS USED BELOW TOO!!!
        nuclidesNames = self.propertyDensities.index

        seriesNameMap = {'alkali metals':'Alkali metals', 'alkali earth metals':'Alkaline earth metals', 'lanthanides':'Lanthanides', 'actinides':'Actinides', 'transition metals':'Transition metals','noble gases':'Noble gases','metalloids':'Metalloids','fission products':'fission products','nonmetals':'Nonmetals','oxide fission products':'oxide fission products','halogens':'Halogens', 'minor actinides':'minor actnides'}
        #
        if series == 'fission products':
           nuclides = [ x for x in nuclidesNames if SERIES[ ELEMENTS[x.split('-')[0].strip()].series ] != seriesNameMap['actinides'] ]
        #
        elif series == 'oxide fission products':
           collec = [ seriesNameMap['actinides'],
                      seriesNameMap['halogens'],
                      seriesNameMap['noble gases'],
                    ]
           nuclides = [ x for x in nuclidesNames if SERIES[ ELEMENTS[x.split('-')[0].strip()].series ] not in collec ]
           collec = ['C','N','O','H']
           nuclides = [ x for x in nuclides if x.split('-')[0].strip() not in collec ]
        #
        elif series == 'minor actinides':
           nuclides = [ x for x in nuclidesNames if SERIES[ ELEMENTS[x.split('-')[0].strip()].series ] == seriesNameMap['actinides'] ]
           collec = ['U','Pu']
           nuclides = [ x for x in nuclides if x.split('-')[0].strip() not in collec ]
        #
        else:
           nuclides = [ x for x in nuclidesNames if SERIES[ ELEMENTS[x.split('-')[0].strip()].series ]== seriesNameMap[series] ]

        return nuclides

     if series is None:

        nuclidesNames = self.propertyDensities.index
        return list( nuclidesNames )

#.................................................................................
# mass or mass concentration

  if attributeName == 'massCC': 
     colName = 'Mass CC [g/cc]'

#.................................................................................
# radioactivity               

  if attributeName == 'radioactivityDens': 
     colName = 'Radioactivity Dens. [Ci/cc]'

#.................................................................................
# thermal                     

  if attributeName == 'thermalDens' or  attributeName == 'heatDens': 
     colName = 'Thermal Dens. [W/cc]'

#.................................................................................
# gamma                       

  if attributeName == 'gammaDens': 
     colName = 'Gamma Dens. [W/cc]'

#.................................................................................
##################################################################################
#.................................................................................

#.................................................................................
# all nuclide content added

  if symbol is None and series is None:

     density = 0.0
     density = self.propertyDensities[ colName ].sum()
     return float(density) # avoid numpy.float64 type

#.................................................................................
# get chemical element series

  if series is not None:
 
     density = 0.0

     assert series in self.chemicalElementSeries, 'series: %r; fail.'%(series)

     seriesNameMap = {'alkali metals':'Alkali metals', 'alkali earth metals':'Alkaline earth metals', 'lanthanides':'Lanthanides', 'actinides':'Actinides', 'transition metals':'Transition metals','noble gases':'Noble gases','metalloids':'Metalloids','fission products':'fission products','nonmetals':'Nonmetals','oxide fission products':'oxide fission products','halogens':'Halogens', 'minor actinides':'minor actnides'}

     if series in self.chemicalElementSeries:

       nuclidesNames = self.propertyDensities.index
       #
       if series == 'fission products':
          nuclides = [ x for x in nuclidesNames if SERIES[ ELEMENTS[x.split('-')[0].strip()].series ] != seriesNameMap['actinides'] ]
       #
       elif series == 'oxide fission products':
          collec = [ seriesNameMap['actinides'],
                     seriesNameMap['halogens'],
                     seriesNameMap['noble gases'],
                   ]
          nuclides = [ x for x in nuclidesNames if SERIES[ ELEMENTS[x.split('-')[0].strip()].series ] not in collec ]
          collec = ['C','N','O','H']
          nuclides = [ x for x in nuclides if x.split('-')[0].strip() not in collec ]
       #
       elif series == 'minor actinides':
          nuclides = [ x for x in nuclidesNames if SERIES[ ELEMENTS[x.split('-')[0].strip()].series ] == seriesNameMap['actinides'] ]
          collec = ['Np','Am','Cm']
          nuclides = [ x for x in nuclides if x.split('-')[0].strip() in collec ]
       #
       else:
          nuclides = [ x for x in nuclidesNames if SERIES[ ELEMENTS[x.split('-')[0].strip()].series ]== seriesNameMap[series] ]

#       print('fission products ',nuclides)

       for nuclide in nuclides:
         density += self.propertyDensities.loc[nuclide,colName]

     return float(density) # avoid numpy.float64 type
   
#.................................................................................
# get specific nuclide (either the isotopes of the nuclide or the specific isotope) property

  if symbol is not None:

    density = 0.0

  # isotope
    if len(symbol.split('-')) == 2:
      density = self.propertyDensities.loc[symbol,colName]

  # chemical element 
    else:
      nuclidesNames = self.propertyDensities.index
#    print(self.propertyDensities)
      isotopes = [x for x in nuclidesNames if x.split('-')[0].strip()==symbol]
#    print(isotopes)
      for isotope in isotopes:
        density += self.propertyDensities.loc[isotope,colName]

    return float(density) # avoid numpy.float64.type

#*********************************************************************************
