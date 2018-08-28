"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Pyplot module.

Tue Jun 24 01:03:45 EDT 2014
"""
# *********************************************************************************
import os
import sys
import io
import time
import datetime
import logging
import xml.etree.ElementTree as ElementTree
import numpy as np
import matplotlib
matplotlib.use('Agg', warn=False)
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator
# *********************************************************************************

# ---------------------------------------------------------------------------------


def _plot_time_tables(self, initialTime=0.0, finalTime=0.0):

    nTimeSteps = len(self.timeTablesData.keys())
    if nTimeSteps == 0:
        return

    s = '_plot_time_tables(): plotting tables'
    self.log.debug(s)

#  s = '_plot_time_tables(): timeTablesData keys = '+str(self.timeTablesData.items())
#  self.log.debug(s)


#  assert nVariables <= 9, 'exceeded # of variables'

    fig = plt.figure('time-tables')

    gs = gridspec.GridSpec(2, 2)
    gs.update(left=0.1, right=0.98, wspace=0.4, hspace=0.4)

    axlst = list()
    axlst.append(fig.add_subplot(gs[0, 0]))
    axlst.append(fig.add_subplot(gs[0, 1]))
    axlst.append(fig.add_subplot(gs[1, 0]))
    axlst.append(fig.add_subplot(gs[1, 1]))
    axes = np.array(axlst)

    text = 'cortix.viz.PyPlot: Time-Tables Dashboard'
    fig.text(.5, .95, text, horizontalalignment='center', fontsize=16)

    for (key, val) in self.timeTablesData.items():
        (timeStamp, timeUnit) = key
        columns = val

        if timeStamp == 0.0:
            continue

        distance = columns[0]
        xLabel = distance.get('name').strip()
        xUnit = distance.get('unit').strip()
        x = distance.text.strip().split(',')
        for i in range(len(x)):
            x[i] = float(x[i])
        x = np.array(x)

        for k in range(len(columns) - 1):

            ax = axes.flat[k]

            y = columns[k + 1]
            yLabel = y.get('name').strip()
            yUnit = y.get('unit').strip()
            yLegend = y.get('legend').strip()
            y = y.text.strip().split(',')
            for i in range(len(y)):
                y[i] = float(y[i])
            y = np.array(y)

            if k == 0 or k == 1:
                y *= 1000.0
                yUnit = 'm'


#    x = data[:,0]
#    if x.max() >= 120.0:
#      x /= 60.0
#      if timeUnit == 'm': timeUnit = 'h'

#    y = data[:,1]
#    if y.max() >= 1000.0:
#      y /= 1000.0
#      if varUnit == 'gram' or varUnit == 'g':
#        varUnit = 'kg'
#    if y.max() <= .1:
#      y *= 1000.0
#      if varUnit == 'gram' or varUnit == 'g':
#        varUnit = 'mg'

            ax.set_xlabel(xLabel + ' [' + xUnit + ']', fontsize=9)
            ax.set_ylabel(yLabel + ' [' + yUnit + ']', fontsize=9)

#    ymax  = y.max()
#    dy    = ymax * .1
#    ymax += dy
#    ymin  = y.min()
#    ymin -= dy

#    ax.set_ylim(ymin,ymax)

            for l in ax.get_xticklabels():
                l.set_fontsize(10)
            for l in ax.get_yticklabels():
                l.set_fontsize(10)
#  color  = parameters['plot-color']
#  marker = parameters['plot-marker']+'-'
#  axis.set_xlim(2e-3, 2)
#  axis.set_aspect(1)
#  axis.set_title("adjustable = box")

            ax.plot(x, y, 's-', color='black', linewidth=0.5, markersize=2,
                    markeredgecolor='black', label=yLegend)

#      if k == 2 or k == 3: ax.set_yscale("log")


#      ax.legend( loc='best', prop={'size':8} )

    # end of for (varSpec,ax) in zip( self.timeSeriesData , axes.flat ):

    fig.savefig('pyplot-timetables.png', dpi=200, fomat='png')
    plt.close('time-tables')

    return

# *********************************************************************************
