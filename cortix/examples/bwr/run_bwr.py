#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
'''

'''

import logging
import scipy.constants as const

from cortix import Cortix
from cortix import Network

from bwr import BWR
from turbine import Turbine
from condenser import Condenser

def main():
    '''Cortix run file for a solvent extraction network.

    Attributes
    ----------
    end_time: float
        End of the flow time in SI unit.
    time_step: float
        Size of the time step between port communications in SI unit.
    use_mpi: bool
        If set to `True` use MPI otherwise use Python multiprocessing.

    '''

    # Simulation time and stepping input

    end_time  = 4.0 * const.hour
    time_step = 1.0 * const.minute

    use_mpi = False  # True for MPI; False for Python multiprocessing

    plant = Cortix( use_mpi=use_mpi, splash=True )

    plant_net = plant.network = Network()

    # General parameters

    show_time = (True,20)
    #params
    params = dict()
    import math
    import scipy.constants as sc
    import iapws.iapws97 as steam_table
    params = dict()

    #Data pertaining to one-group energy neutron balance
    params['gen_time']     = 1.0e-4  # s
    params['beta']         = 6.5e-3  # 
    params['k_infty']      = 1.34477
    params['buckling'] = (math.pi/237.5)**2.0 + (2.405/410)**2.0 # geometric buckling; B = (pi/R)^2 + (2.405/H)^2
    params['q_0'] = 0.1
    params['fuel macro a'] = 1.34226126162 #fuel macroscopic absorption cross section, cm^-1
    params['mod micro a'] = 0.332 * sc.zepto * sc.milli #moderator microscopic absorption cross section, cm^2
    params['n fuel'] = 1.9577906e+21 #number density of the fuel, atoms/cm^3
    params['I'] = 40.9870483 * sc.zepto * sc.milli  #resonance integral, I (dimensionless)
    params['mod micro s'] = 20 * sc.zepto * sc.milli # moderator microscopic scattering cross section, cm^2
    params['xi'] = 1 # average logarithmic energy decrement for light water
    params['E0'] = 2 * sc.mega # energy of a neutron produced by fissioning, in electron volts
    params['mod mu0'] = 0.71 # migration and diffusion area constants
    params['eta'] = 1.03 # fast fission factor
    params['epsilon'] = 2.05 # neutron multiplecation factor
    params['mod molar mass'] = 18 # g/mol

    #data required by the condenser
    params['pipe_diameter'] = 0.1 #m
    params['liquid_velocity'] = 10 #m/s
    params['cooling water flowrate'] = 100000 #kg/s
    params['heat transfer area'] = 22000 #m2, or 500 4m long, 0.1m diameter pipes

    params['reg_rod_worth'] = 1.5e-4 # pcm

    params['n_dens_ss_operation'] = 1 #1.963e13/2200 * 1e4 #  #neutrons/m^2

    #Delayed neutron emission
    params['species_decay']     = [0.0124, 0.0305, 0.111, 0.301, 1.14, 3.01] # 1/sec
    params['species_rel_yield'] = [0.033, 0.219, 0.196, 0.395, 0.115, 0.042]

    #Data pertaining to two-temperature heat balances
    params['fis_energy']           = 180 * 1.602e-13 # J/fission 
    params['enrich']               = 4.3/100.
    params['fuel_mat_mass_dens']   = 10.5 # g/cc
    #params['moderator_fuel_ratio'] = 387 # atomic number concentration ratio
    params['sigma_f_o']            = 586.2 * 100 * 1e-30 # m2
    params['temp_o']               = 20 + 273.15 # K
    params['thermal_neutron_velo'] = 2200 # m/s

    params['fis_nuclide_num_dens_fake'] = 9.84e26 # (fissile nuclei)/m3

    params['q_c'] = 303 # volumetric flow rate

    params['fuel_dens']   = 10500 # kg/m3
    params['cp_fuel']     = 236.58 # J/(kg K)
    params['fuel_volume'] = 5 # m3

    params['steam flowrate'] = 1820 # kg/s
    params['coolant_dens']   = 1000 #  kg/m3
    params['cp_coolant']     =  4184# J/(mol K) - > J/(kg K)
    params['coolant_volume'] = 7.5 #m3

    params['ht_coeff'] = 10000000
    params['turbine efficiency'] = 0.8
    params['pump efficiency'] = 0.8

    params['fis_prod_beta_energy_rate']  = 1.26 * 1.602e-13 # J/(fission sec) 1.26 t^-1.2 (t in seconds)
    params['fis_prod_alpha_energy_rate'] = 1.40 * 1.602e-13 # J/(fission sec) 1.40 t^-1.2 (t in seconds)
# % subcooling based on the % subcooling that exists at steady state
    params['% subcooling'] = 1 #(1 -(steam_table._Region4(7, 0)["h"]  - steam_table._Region1(493.15, 7)["h"])/(steam_table._Region4(7,0)["h"]))
    params['shutdown temp reached'] = False
    params['q_source_status'] = 'in' # is q_source inserted (in) or withdrawn (out)

    params['malfunction start'] = 999 * sc.hour
    params['malfunction end'] = 999 * sc.hour
    params['shutdown time'] = 9999 * sc.hour

    gen_time = params['gen_time'] # retrieve neutron generation time
    params['q_0'] = 0.1

    params['n_ss'] = 0 # neutronless steady state before start up

    rho_0_over_beta = 0.25 # $
    beta = params['beta']

    params['alpha_n'] = 0 # control rod reactivity worth; enough to cancel out the negative 

    params['reactivity'] = rho_0_over_beta * beta # "rho/beta = 10 cents"

    params['temp_0'] = params['temp_o']

    params['tau_fake'] = 1 # s
    params['malfunction subcooling'] = 0.75
    params['alpha_n_malfunction'] = 0
    n_species = len(params['species_decay'])
    assert len(params['species_rel_yield']) == n_species
    import numpy as np
    c_vec_0 = np.zeros(n_species,dtype=np.float64) # initialize conentration vector
    species_decay = params['species_decay'] # retrieve list of decay constants
    lambda_vec    = np.array(species_decay) # create a numpy vector
    beta = params['beta']
    species_rel_yield = params['species_rel_yield']
    beta_vec = np.array(species_rel_yield) * beta  # create the beta_i's vector
    gen_time = params['gen_time'] # retrieve neutron generation time
    n_ss = params['n_ss']
    c_vec_ss = beta_vec/lambda_vec/gen_time * n_ss # compute the steady state precursors number density
    params['c_vec_ss'] = c_vec_ss
    # setup initial condition for variables
    params['n_0']     = n_ss
    params['c_vec_0'] = c_vec_ss
    params['rho_0']   = params['reactivity']
    params['temp_f_0'] = 300
    params['temp_c_0'] = params['temp_0']
    params['pressure_0'] = 1.013 # bar
    params['turbine-runoff-pressure'] = 1
    params['runoff-pressure'] = params['turbine-runoff-pressure']

    reactor   = BWR(params)
    plant_net.module(reactor)

    turbine   = Turbine(params)
#    plant_net.module(turbine)

    condenser = Condenser(params)
#    plant_net.module(condenser)

#    plant_net.connect( [reactor,'coolant-outflow'], [turbine,'steam-inflow'] )
#    plant_net.connect( [turbine,'runoff'], [condenser,'inflow'] )
#    plant_net.connect( [condenser,'outflow'], [reactor,'coolant-inflow'] )

    plant_net.draw()
    plant_net.run()

if __name__ == '__main__':
    main()
