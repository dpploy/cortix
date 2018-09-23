# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/cortix
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/cortix/blob/master/COPYRIGHT.txt
#
# Licensed under the GNU General Public License v. 3, please see LICENSE file.
# https://www.gnu.org/licenses/gpl-3.0.txt
'''
PyPlot module.

Author: Valmor F. de Almeida dealmeidav@ornl.gov; vfda
Tue Jun 24 01:03:45 EDT 2014
'''
#*********************************************************************************
import os
import sys
import io
import time
import datetime
import logging
import xml.etree.ElementTree as ElementTree
import numpy as npy
import matplotlib
matplotlib.use('Agg', warn=False)
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator
import pickle 

import xml.etree.ElementTree as ElementTree
from threading import Lock

from .time_sequence import TimeSequence
# *********************************************************************************

class PyPlot():

    def __init__(self,
                 slot_id,
                 input_full_path_file_name,
                 work_dir,
                 ports = list(),
                 cortix_start_time = 0.0,
                 cortix_final_time = 0.0,
                 cortix_time_step = 0.0,
                 cortix_time_unit  = None
                 ):

        # Sanity test
        assert isinstance( slot_id, int), '-> slot_id type %r is invalid.' % \
                           type(slot_id)
        assert isinstance( ports, list), '-> ports type %r is invalid.' % type(ports)
        assert ports is not None, 'fatal.'
        assert isinstance( cortix_start_time, float), '-> time type %r is invalid.' % \
                           type(cortix_start_time)
        assert isinstance( cortix_final_time, float), '-> time type %r is invalid.' % \
                           type(cortix_final_time)
        assert isinstance( cortix_time_step, float), '-> time step type %r is invalid.' % \
                           type(cortix_time_step)

        assert isinstance( cortix_time_unit, str), '-> time unit type %r is invalid.' % \
                           type(cortix_time_unit)

        # Logger
        self.__log = logging.getLogger('launcher-modulib.pyplot_' + str(slot_id) +
                                       '.cortix_driver.pyplot')
        self.__log.info('initializing an object of PyPlot()')

        # Member data
        self.__slot_id = slot_id
        self.__ports   = ports

        self.__cortix_start_time = cortix_start_time
        self.__cortix_final_time = cortix_final_time
        self.__cortix_time_unit  = cortix_time_unit

        n_time_steps = ( cortix_final_time - cortix_start_time ) / cortix_time_step
        n_of_times_to_plot = 10 # during the entire run
        # how often to plot
        self.__plot_interval = round( n_time_steps / n_of_times_to_plot )
        # the width of the window to plot
        self.__plot_slide_window_interval = 3 * self.__plot_interval

        s = 'Plot interval = ' + str(self.__plot_interval) + ' [' + self.__cortix_time_unit + ']'
        self.__log.info(s)
        s = 'Plot slide window interval = ' + str(self.__plot_slide_window_interval) + ' [' + self.__cortix_time_unit + ']'
        self.__log.info(s)

        # This holds all time sequences, potentially, one per use port. One time sequence
        # has all the data for one port connection.
        # Time sequences are xml formatted data per Cortix convention.
        self.__time_sequences_tmp = list()  # temporary storage

        # Tables in xml format per Cortix convention
        # [(time,timeUnit)] = [column,column,...]
        self.__time_tables_data = dict(list())

# .................................................................................
# Input ports (if any)

        fin = open(input_full_path_file_name, 'r')
        input_data_full_path_file_names = list()
        for line in fin:
            input_data_full_path_file_names.append( line.strip() )
        fin.close()

        if len(input_data_full_path_file_names) == 0:
            return

        found = False
        for (portName, portType, port_file) in ports:
            if portName == 'time-sequence-input':  # this is the use port connected to the input port
                s = 'cp -f ' + input_data_full_path_file_names[0] + ' ' + port_file
                os.system(s)
                self.__log.debug(s)
                found = True

        if found is True:
            s = 'found time-sequence-input file.'
            self.__log.info(s)
        else:
            s = 'did not find time-sequence-input file.'
            self.__log.warn(s)

# ---------------------- end def __init__():------------------------------

    def call_ports(self, cortix_time=0.0):
        '''
        Transfer data at cortix_time
        '''

        if (cortix_time % self.__plot_interval <= 1e-2 and \
            cortix_time < self.__cortix_final_time)        \
           or cortix_time >= self.__cortix_final_time:

            # use ports in PyPlot have infinite multiplicity (implement
            # multiplicity later)
            assert len(self.__time_sequences_tmp) == 0

            for port in self.__ports:
                (portName, portType, thisPortFile) = port

                if portType == 'use':
                    assert portName == 'time-sequence' or portName == 'time-tables' or \
                        portName == 'time-sequence-input'

                    self.__use_data( usePortName = portName,
                                     usePortFile = thisPortFile,
                                     at_time = cortix_time )

#----------------------- end def call_ports():------------------------------------

    def execute(self, cortix_time=0.0, time_step=0.0):

        s = 'execute(): cortix time [min] = ' + str(round(cortix_time, 3))
        self.__log.debug(s)

        self.__plot_data(cortix_time, time_step)

#----------------------- end def execute():---------------------------------------

# *********************************************************************************
# Private helper functions (internal use: __)

    def __use_data(self, usePortName=None, usePortFile=None, at_time=0.0):
        '''
        This operates on a given use port;
        '''

        # Access the port file
        port_file = self.__get_port_file( usePortName = usePortName, 
                                          usePortFile = usePortFile  )

# Get data from port files
        if usePortName == 'time-sequence' or usePortName == 'time-sequence-input' \
           and port_file is not None:

            self.__get_time_sequence( port_file, at_time )

        if usePortName == 'time-tables' and port_file is not None:
            _GetTimeTables(self, port_file, at_time)

        return
#----------------------- end def __use_data():------------------------------------

    def __provide_data(self, providePortName=None, at_time=0.0):
        '''
        Nothing planned to provide at this time; but could change
        '''

        return
#----------------------- end def __provide_data():--------------------------------

    def __get_port_file(self, usePortName=None,
                        usePortFile=None, providePortName=None):

        port_file = None

        # ..........
        # Use ports
        # ..........
        if usePortName is not None:

            assert providePortName is None

            for port in self.__ports:
                (portName, portType, thisPortFile) = port
                if portName == usePortName and portType == 'use' and thisPortFile == usePortFile:
                    port_file = thisPortFile

            if port_file is None:
                return None

            max_n_trials = 50
            n_trials = 0
            while os.path.isfile(port_file) is False and n_trials <= max_n_trials:
                n_trials += 1
                time.sleep(0.1)

            if n_trials > max_n_trials:
                s = '__get_port_file(): waited ' + str(n_trials) + \
                    ' trials for port: ' + port_file
                self.__log.warn(s)

            assert os.path.isfile(port_file) is True, 'port_file %r not available; stop.' % port_file

        # ..............
        # Provide ports
        # ..............
        if providePortName is not None:

            assert usePortName is None

            for port in self.__ports:
                (portName, portType, thisPortFile) = port
                if portName == providePortName and portType == 'provide':
                    port_file = thisPortFile

        return port_file
# ---------------------- end def __get_port_file():-----------------------

    def __plot_data(self, cortix_time=0.0, time_step=0.0):

        if cortix_time % self.__plot_interval <= 1e-2 and \
           cortix_time < self.__cortix_final_time:

            s = '__plot_data(): cortix time [min] = ' + str(cortix_time)
            self.__log.debug(s)

            from_time = max(0.0, cortix_time - self.__plot_slide_window_interval)
            to_time = cortix_time

            s = '__plot_data(): from_time [min] = ' + str(from_time)
            self.__log.debug(s)
            s = '__plot_data(): to_time [min] = ' + str(to_time)
            self.__log.debug(s)

            # plot with slide window history
            self.__plot_time_seq_dashboard( from_time, to_time )

            # plot with slide window history
            self.__plot_time_tables( from_time, to_time )

        elif cortix_time >= self.__cortix_final_time:
 
            s = '__plot_data(): cortix time [min] = ' + str(cortix_time)
            self.__log.debug(s)

            self.__plot_time_seq_dashboard( self.__cortix_start_time, self.__cortix_final_time)  # plot all history

            self.__plot_time_tables( self.__cortix_start_time, self.__cortix_final_time )  # plot all history

#----------------------- end def __plot_data():-----------------------------------

    def __get_time_sequence(self, port_file, at_time):
        '''
        This uses a use port_file which is guaranteed to exist at this point
        '''

        s = '__get_time_sequence(): will get data in port_file: ' + port_file
        self.__log.debug(s)

        if at_time >= self.__cortix_final_time:
            initialTime = self.__cortix_start_time
        else:
            initialTime = max(self.__cortix_start_time, at_time - self.__plot_slide_window_interval)

        timeSequence = TimeSequence( port_file, 'xml', initialTime, at_time, 
                                     self.__cortix_time_unit, self.__log )

        self.__time_sequences_tmp.append(timeSequence)

        s = '__get_time_sequence(): loaded ' + timeSequence.get_name()
        self.__log.debug(s)

        return
#----------------------- end def __get_time_sequence():---------------------------

    def __get_time_tables(self, port_file, at_time):
        '''
        This uses a use port_file which is guaranteed at this point
        '''

        s = '__get_time_tables(): will check file: ' + port_file
        self.__log.debug(s)

        found = False

        while found is False:

            s = '__get_time_tables(): checking for value at ' + str(at_time)
            self.__log.debug(s)

#    tree = ElementTree.parse(port_file)

            try:
                mutex = Lock()
                mutex.acquire()
                tree = ElementTree.parse(port_file)
            except ElementTree.ParseError as error:
                mutex.release()
                s = '__get_time_tables(): ' + port_file + ' unavailable. Error code: ' + \
                    str(error.code) + ' File position: ' + \
                    str(error.position) + '. Retrying...'
                self.__log.debug(s)
                time.sleep(0.1)
                continue

            mutex.release()
            rootNode = tree.getroot()
            assert rootNode.tag == 'time-tables', 'invalid format.'

            timeNodes = rootNode.findall('timeStamp')

            for timeNode in timeNodes:

                timeStamp = float(timeNode.get('value').strip())

                if timeStamp == at_time:

                    found = True

                    timeUnit = timeNode.get('unit').strip()

                    self.__time_tables_data[(timeStamp, timeUnit)] = list()

                    columns = timeNode.findall('column')

                    data = list()

                    for col in columns:
                        data.append(col)

                    self.__time_tables_data[(timeStamp, timeUnit)] = data

                    s = '__get_time_tables(): added ' + str(len(data)) + ' columns of data'
                    self.__log.debug(s)

                # end of if timeStamp == at_time:

            # end of for timeNode in timeNodes:

            if found is False:
                time.sleep(0.1)

        # while found is False:

        return
#----------------------- end __get_time_tables():---------------------------------

    def __plot_time_seq_dashboard( self, initialTime=0.0, finalTime=0.0 ):
        ''' 
        All time sequences on hold will be plotted here and the temporary storage 
        of these time sequences will be cleared at the end.
        '''

        nRows = 3
        nCols = 1

        nSequences = len(self.__time_sequences_tmp)
        if nSequences == 0:
            return

        s = '__plot_time_seq_dashboard(): from: ' + str(initialTime) + \
            ' to ' + str(finalTime)
        self.__log.debug(s)

        s = '__plot_time_seq_dashboard(): # of sequences: ' + str(nSequences)
        self.__log.debug(s)

        nVar = 0
        for seq in self.__time_sequences_tmp:
            nVar += seq.GetNVariables()

        s = '__plot_time_seq_dashboard(): # of variables: ' + str(nVar)
        self.__log.debug(s)

    # multiple sequences are stored coming from various sources
    # collect all variables in a list for mapping on the dashboards
        variablesData = list()
        for seq in self.__time_sequences_tmp:
            for (spec, values) in seq.GetVariables().items():
                variablesData.append((spec, values))

        assert len(variablesData) == nVar, 'len(variablesData) = %r; nVar = %r' % (
            len(variablesData), nVar)

        today = datetime.datetime.today().strftime("%d%b%y %H:%M:%S")

        figNum = None

        # loop over variables and assign to the dashboards
        iDash = 0
        for iVar in range(nVar):

            if iVar % (
                    nRows * nCols) == 0:  # if a multiple of nRows*nCols start a new dashboard

                if iVar != 0:  # flush any current figure
                    figName = 'pyplot_' + \
                        str(self.__slot_id) + '-timeseq-dashboard-' + \
                        str(iDash).zfill(2) 
                    fig.savefig(figName+'.png', dpi=200, fomat='png')
                    plt.close(figNum)

                    pickle.dump( fig, open(figName+'.pickle','wb') )

                    s = '__plot_time_seq_dashboard(): created plot: ' + figName
                    self.__log.debug(s)

                    iDash += 1
                # end of: if iVar != 0: # flush any current figure

                figNum = str(self.__slot_id) + '.' + str(iDash)
                fig = plt.figure(num=figNum)

                gs = gridspec.GridSpec(nRows, nCols)
#                gs.update(left=0.08, right=0.98, wspace=0.4, hspace=0.4)
                gs.update(left=0.09, right=0.98, wspace=0.4, hspace=0.5)

                axlst = list()

                nPlotsNeeded = nVar - iVar
                count = 0
                for i in range(nRows):
                    for j in range(nCols):
                        axlst.append(fig.add_subplot(gs[i, j]))
                        count += 1
                        if count == nPlotsNeeded:
                            break
                    if count == nPlotsNeeded:
                        break
    
                axes = npy.array(axlst)

                text = today + ': Cortix.PyPlot_' + \
                    str(self.__slot_id) + ': Time-Sequence Dashboard'
                fig.text(.5, .95, text, horizontalalignment='center', fontsize=14)

                axs = axes.flat

                axId = 0

            # end of: if iVar % nRows*nCols == 0: # if a multiple of nRows*nCols
            # start a new dashboard

            (spec, val) = variablesData[iVar]

            ax = axs[axId]
            axId += 1

            varName = spec[0]
            varUnit = spec[1]

            if varUnit == 'gram':
                varUnit = 'g'
            if varUnit == 'gram/min':
                varUnit = 'g/min'
            if varUnit == 'gram/s':
                varUnit = 'g/s'
            if varUnit == 'gram/m3':
                varUnit = 'g/m3'
            if varUnit == 'gram/L':
                varUnit = 'g/L'
            if varUnit == 'sec':
                varUnit = 's'

            timeUnit = spec[2]
            varLegend = spec[3]
            varScale = spec[4]
            assert varScale == 'log' or varScale == 'linear' or varScale == 'log-linear' \
                or varScale == 'linear-log' or varScale == 'linear-linear' or \
                varScale == 'log-log'

            if timeUnit == 'minute':
                timeUnit = 'min'

            data = npy.array(val)  # convert to numpy ndarray

#      assert len(data.shape) == 2, 'not a 2-column shape: %r in var %r of %r; stop.' % (data.shape,varName,varLegend)
            if len(data.shape) != 2:
                s = '__plot_time_seq_dashboard(): bad data; variable: ' + varName + ' unit: ' + \
                    varUnit + ' legend: ' + varLegend + \
                    ' shape: ' + str(data.shape) + ' skipping...'
                self.__log.warn(s)
                continue  # simply skip bad data and log

            x = data[:, 0]

            if (varScale == 'linear' or varScale == 'linear-linear' or \
                varScale == 'linear-log') and x.max() >= 120.0:
                x /= 60.0
                if timeUnit == 'min':
                    timeUnit = 'h'

            y = data[:, 1]

            if y.max() >= 1e3 and varScale != 'linear-log' and \
                    varScale != 'log-log' and varScale != 'log':
                y /= 1e3
                if varUnit == 'gram' or varUnit == 'g':
                    varUnit = 'kg'
                if varUnit == 'L':
                    varUnit = 'kL'
                if varUnit == 'cc':
                    varUnit = 'L'
                if varUnit == 'Ci':
                    varUnit = 'kCi'
                if varUnit == 'W':
                    varUnit = 'kW'
                if varUnit == 'gram/min' or varUnit == 'g/min':
                    varUnit = 'kg/min'
                if varUnit == 'gram/s' or varUnit == 'g/s':
                    varUnit = 'kg/s'
                if varUnit == 'gram/m3' or varUnit == 'g/m3':
                    varUnit = 'kg/m3'
                if varUnit == 'gram/L' or varUnit == 'g/L':
                    varUnit = 'kg/L'
                if varUnit == 'W/L':
                    varUnit = 'kW/L'
                if varUnit == 'Ci/L':
                    varUnit = 'kCi/L'
                if varUnit == '':
                    varUnit = 'x1e3'
                if varUnit == 'L/min':
                    varUnit = 'kL/min'
                if varUnit == 'Pa':
                    varUnit = 'kPa'
                if varUnit == 's':
                    varUnit = 'ks'
                if varUnit == 'm':
                    varUnit = 'km'

            if y.max() < 1e-6 and varScale != 'linear-log' and \
                    varScale != 'log-log' and varScale != 'log':
                y *= 1e9
                if varUnit == 'gram' or varUnit == 'g':
                    varUnit = 'ng'
                if varUnit == 'cc':
                    varUnit = 'n-cc'
                if varUnit == 'L':
                    varUnit = 'nL'
                if varUnit == 'W':
                    varUnit = 'nW'
                if varUnit == 'Ci':
                    varUnit = 'nCi'
                if varUnit == 'gram/min' or varUnit == 'g/min':
                    varUnit = 'ng/min'
                if varUnit == 'gram/s' or varUnit == 'g/s':
                    varUnit = 'ng/s'
                if varUnit == 'gram/m3' or varUnit == 'g/m3':
                    varUnit = 'ng/m3'
                if varUnit == 'gram/L' or varUnit == 'g/L':
                    varUnit = 'ng/L'
                if varUnit == 'W/L':
                    varUnit = 'nW/L'
                if varUnit == 'Ci/L':
                    varUnit = 'nCi/L'
                if varUnit == 'L/min':
                    varUnit = 'nL/min'
                if varUnit == 'Pa':
                    varUnit = 'nPa'
                if varUnit == 's':
                    varUnit = 'ns'

            if (y.max() >= 1e-6 and y.max() < 1e-3) and varScale != 'linear-log' and \
                    varScale != 'log-log' and varScale != 'log':
                y *= 1e6
                if varUnit == 'gram' or varUnit == 'g':
                    varUnit = 'ug'
                if varUnit == 'cc':
                    varUnit = 'u-cc'
                if varUnit == 'L':
                    varUnit = 'uL'
                if varUnit == 'W':
                    varUnit = 'uW'
                if varUnit == 'Ci':
                    varUnit = 'uCi'
                if varUnit == 'gram/min' or varUnit == 'g/min':
                    varUnit = 'ug/min'
                if varUnit == 'gram/s' or varUnit == 'g/s':
                    varUnit = 'ug/s'
                if varUnit == 'gram/m3' or varUnit == 'g/m3':
                    varUnit = 'ug/m3'
                if varUnit == 'gram/L' or varUnit == 'g/L':
                    varUnit = 'ug/L'
                if varUnit == 'W/L':
                    varUnit = 'uW/L'
                if varUnit == 'Ci/L':
                    varUnit = 'uCi/L'
                if varUnit == 'L/min':
                    varUnit = 'uL/min'
                if varUnit == 'Pa':
                    varUnit = 'uPa'
                if varUnit == 's':
                    varUnit = 'us'

            if (y.max() >= 1e-3 and y.max() < 1e-1) and varScale != 'linear-log' and \
                    varScale != 'log-log' and varScale != 'log':
                y *= 1e3
                if varUnit == 'gram' or varUnit == 'g':
                    varUnit = 'mg'
                if varUnit == 'cc':
                    varUnit = 'm-cc'
                if varUnit == 'L':
                    varUnit = 'mL'
                if varUnit == 'W':
                    varUnit = 'mW'
                if varUnit == 'Ci':
                    varUnit = 'mCi'
                if varUnit == 'gram/min' or varUnit == 'g/min':
                    varUnit = 'mg/min'
                if varUnit == 'gram/s' or varUnit == 'g/s':
                    varUnit = 'mg/s'
                if varUnit == 'gram/m3' or varUnit == 'g/m3':
                    varUnit = 'mg/m3'
                if varUnit == 'gram/L' or varUnit == 'g/L':
                    varUnit = 'mg/L'
                if varUnit == 'W/L':
                    varUnit = 'mW/L'
                if varUnit == 'Ci/L':
                    varUnit = 'mCi/L'
                if varUnit == 'L/min':
                    varUnit = 'mL/min'
                if varUnit == 'Pa':
                    varUnit = 'mPa'
                if varUnit == 's':
                    varUnit = 'ms'

            ax.set_xlabel('Time [' + timeUnit + ']', fontsize=9)
            ax.set_ylabel(varName + ' [' + varUnit + ']', fontsize=9)

            ymax = y.max()
            dy = ymax * .1
            ymax += dy
            ymin = y.min()
            ymin -= dy

            if abs(ymin - ymax) <= 1.e-4:
                ymin = -1.0
                ymax = 1.0

            ax.set_ylim(ymin, ymax)

            if nCols >= 4:
                for l in ax.get_xticklabels():
                    l.set_fontsize(8)
            else:
                for l in ax.get_xticklabels():
                    l.set_fontsize(10)
            for l in ax.get_yticklabels():
                l.set_fontsize(10)

            if timeUnit == 'h' and x.max() - x.min() <= 5.0:
                majorLocator = MultipleLocator(1.0)
                minorLocator = MultipleLocator(0.5)

                ax.xaxis.set_major_locator(majorLocator)
                ax.xaxis.set_minor_locator(minorLocator)

            if varScale == 'log' or varScale == 'log-log':
                ax.set_xscale('log')
                ax.set_yscale('log')
                positiveX = x > 0.0
                x = npy.extract(positiveX, x)
                y = npy.extract(positiveX, y)
                positiveY = y > 0.0
                x = npy.extract(positiveY, x)
                y = npy.extract(positiveY, y)
                if y.size > 0:
                    if y.min() > 0.0 and y.max() > y.min():
                        ymax = y.max()
                        dy = ymax * .1
                        ymax += dy
                        ymin = y.min()
                        ymin -= dy
                        if ymin < 0.0 or ymin > ymax / 1000.0:
                            ymin = ymax / 1000.0
                        ax.set_ylim(ymin, ymax)
                    else:
                        ax.set_ylim(1.0, 10.0)
                else:
                    ax.set_ylim(1.0, 10.0)

            if varScale == 'log-linear':
                ax.set_xscale('log')
                positiveX = x > 0.0
                x = npy.extract(positiveX, x)
                y = npy.extract(positiveX, y)

            if varScale == 'linear-log':
                ax.set_yscale('log')
                positiveY = y > 0.0
                x = npy.extract(positiveY, x)
                y = npy.extract(positiveY, y)
#      assert x.size == y.size, 'size error; stop.'
                if y.size > 0:
                    if y.min() > 0.0 and y.max() > y.min():
                        ymax = y.max()
                        dy = ymax * .1
                        ymax += dy
                        ymin = y.min()
                        ymin -= dy
                        if ymin < 0.0 or ymin > ymax / 1000.0:
                            ymin = ymax / 1000.0
                        ax.set_ylim(y.min(), ymax)
                    else:
                        ax.set_ylim(1.0, 10.0)
                else:
                    ax.set_ylim(1.0, 10.0)

        # ...................
        # make the plot here

            ax.plot(x, y, 's-', color='black', linewidth=0.5, markersize=2,
                    markeredgecolor='black', label=varLegend)

        # ...................

            ax.legend(loc='best', prop={'size': 7})

            s = '__plot_time_seq_dashboard(): plotted ' + varName + ' from ' + varLegend
            self.__log.debug(s)

    # end of: for iVar in range(nVar):

        figName = 'pyplot_' + str(self.__slot_id) + \
            '-timeseq-dashboard-' + str(iDash).zfill(2) 
        fig.savefig(figName+'.png', dpi=200, fomat='png')
        plt.close(figNum)

        pickle.dump( fig, open(figName+'.pickle','wb') )

        s = '__plot_time_seq_dashboard(): created plot: ' + figName
        self.__log.debug(s)

        s = '__plot_time_seq_dashboard(): done with plotting'
        self.__log.debug(s)
 
    # clear __time_sequences_tmp
        self.__time_sequences_tmp = list()

        return
#----------------------- end __plot_time_seq_dashboard():-------------------------

    def __plot_time_tables( self, initialTime=0.0, finalTime=0.0 ):

        nTimeSteps = len(self.__time_tables_data.keys())

        if nTimeSteps == 0:
            return

        s = '__plot_time_tables(): plotting tables'
        self.log.debug(s)

#  s = '__plot_time_tables(): keys = '+str(self.__time_tables_data.items())
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

        text = 'Cortix.PyPlot: Time-Tables Dashboard'
        fig.text(.5, .95, text, horizontalalignment='center', fontsize=16)

        for (key, val) in self.__time_tables_data.items():
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
#----------------------- end __plot_time_tables():--------------------------------


#======================= end class PyPlot: =======================================
