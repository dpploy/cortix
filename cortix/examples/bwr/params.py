# startup params

import math
import scipy.constants as unit
import numpy as np

def get_params():
    params = dict()

    params['valve_opened'] = False
    params['valve_opening_time'] = 0

    params['operating-mode'] = 'startup'

    #initial SS values for reactor startup
    params['turbine-outflow-temp'] = 293.15
    params['turbine-chi'] = 0
    params['turbine-inlet-temp'] = 293.15
    params['condenser-runoff-temp'] = 287.15
    params['n-dens'] = 0
    params['fuel-temp'] = 293.15
    params['coolant-temp'] = 293.15
    params['delayed-neutron-cc'] = [0, 0, 0, 0, 0, 0]
    params['turbine-work'] = 0
    params['initial-flowrate'] = 0

    params['steam flowrate'] = 1820 #kg/s

    params['malfunction start'] = 999 * unit.hour
    params['malfunction end'] = 999 * unit.hour
    params['shutdown time'] = 999 * unit.hour

    params['temp_f_0'] = 300
    params['temp_c_0'] = params['coolant-temp']
    params['pressure_0'] = 1.013 # bar
    params['turbine-runoff-pressure'] = 1
    params['runoff-pressure'] = params['turbine-runoff-pressure']

    return(params)
