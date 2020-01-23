#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
'''

'''

import logging
import scipy.constants as unit
import matplotlib.pyplot as plt

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

    end_time  = 1.0 * unit.hour
    time_step = 0.5 * unit.minute
    show_time = (True,15*unit.minute)

    use_mpi = False  # True for MPI; False for Python multiprocessing

    plant = Cortix( use_mpi=use_mpi, splash=True )

    plant_net = plant.network = Network()

    #params
    params = dict()
    import math
    import iapws.iapws97 as steam_table

    params['steam flowrate'] = 1820 #kg/s
    #Data pertaining to one-group energy neutron balance
    params['gen_time']     = 1.0e-4  # s
    params['beta']         = 6.5e-3  # 
    params['k_infty']      = 1.34477
    params['buckling'] = (math.pi/237.5)**2.0 + (2.405/410)**2.0 # geometric buckling; B = (pi/R)^2 + (2.405/H)^2
    params['q_0'] = 0.1
    params['fuel macro a'] = 1.34226126162 #fuel macroscopic absorption cross section, cm^-1
    params['mod micro a'] = 0.332 * unit.zepto * unit.milli #moderator microscopic absorption cross section, cm^2
    params['n fuel'] = 1.9577906e+21 #number density of the fuel, atoms/cm^3
    params['I'] = 40.9870483 * unit.zepto * unit.milli  #resonance integral, I (dimensionless)
    params['mod micro s'] = 20 * unit.zepto * unit.milli # moderator microscopic scattering cross section, cm^2
    params['xi'] = 1 # average logarithmic energy decrement for light water
    params['E0'] = 2 * unit.mega # energy of a neutron produced by fissioning, in electron volts
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

    params['malfunction start'] = 999 * unit.hour
    params['malfunction end'] = 999 * unit.hour
    params['shutdown time'] = 0.5  * unit.hour

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

    #*****************************************************************************
    reactor = BWR(params)

    reactor.name      = 'BWR'
    reactor.save      = True
    reactor.time_step = time_step
    reactor.end_time  = end_time
    reactor.show_time = show_time

    plant_net.module(reactor)

    #*****************************************************************************
    params['turbine_inlet_pressure'] = 2
    params['turbine_outlet_pressure'] = 0.5
    params['high_pressure_turbine'] = True

    turbine1   = Turbine(params)
    print('turb1', turbine1.params['high_pressure_turbine'])

    turbine1.name = 'High Pressure Turbine'
    turbine1.save = True
    turbine1.time_step = time_step
    turbine1.end_time = end_time
    turbine1.show_time = show_time
    plant_net.module(turbine1)

    #*****************************************************************************
    params['turbine_inlet_pressure'] = 0.5
    params['turbine_outlet_pressure'] = 0.005
    params['high_pressure_turbine'] = False
    params['steam flowrate'] = params['steam flowrate']/2

    turbine2   = Turbine(params)
    print(turbine2.params['high_pressure_turbine'])

    turbine2.name = 'Low Pressure Turbine 1'
    turbine2.save = True
    turbine2.time_step = time_step
    turbine2.end_time = end_time
    turbine2.show_time = show_time
    plant_net.module(turbine2)

    #*****************************************************************************
    params['turbine_inlet_pressure'] = 0.5
    params['turbine_outlet_pressure'] = 0.005
    params['high_pressure_turbine'] = False

    turbine3   = Turbine(params)

    turbine3.name = 'Low Pressure Turbine 2'
    turbine3.save = True
    turbine3.time_step = time_step
    turbine3.end_time = end_time
    turbine3.show_time = show_time
    plant_net.module(turbine3)

    print('turb2', turbine1.params['high_pressure_turbine'])

    #*****************************************************************************
    params['steam flowrate'] = params['steam flowrate'] * 2

    condenser = Condenser(params)

    condenser.name = 'Condenser'
    condenser.save = True
    condenser.time_step = time_step
    condenser.end_time = end_time
    condenser.show_time = show_time
    plant_net.module(condenser)

    #*****************************************************************************
    plant_net.connect( [reactor, 'coolant-outflow'], [turbine1,'inflow'] )
    plant_net.connect( [turbine1, 'outflow-1'], [turbine2,'inflow'] )
    plant_net.connect( [turbine1, 'outflow-2'], [turbine3, 'inflow'])
    plant_net.connect( [turbine2, 'outflow-1'], [condenser, 'inflow-1'])
    plant_net.connect( [turbine3, 'outflow-1'], [condenser, 'inflow-2'])
    plant_net.connect( [condenser,'outflow'], [reactor,'coolant-inflow'] )

    #*****************************************************************************
    #plant_net.draw()

    plant_net.run()

    if plant.use_multiprocessing or plant.rank == 0:

        # Reactor graphs
        reactor = plant_net.modules[0]

        (quant, time_unit) = reactor.neutron_phase.get_quantity_history('neutron-dens')

        quant.plot( x_scaling=1/unit.minute, x_label='Time [m]',
                    y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('neutron-dens.png', dpi=300)

        (quant, time_unit) = reactor.neutron_phase.get_quantity_history('delayed-neutrons-cc')
        quant.plot( x_scaling=1/unit.minute, x_label='Time [m]',
                    y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('delayed-neutrons-cc.png', dpi=300)

        (quant, time_unit) = reactor.coolant_outflow_phase.get_quantity_history('temp')

        quant.plot( x_scaling=1/unit.minute, x_label='Time [m]',
                    y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('coolant-outflow-temp.png', dpi=300)

        (quant, time_unit) = reactor.reactor_phase.get_quantity_history('fuel-temp')

        quant.plot( x_scaling=1/unit.minute, x_label='Time [m]',
                    y_label =quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('fuel-temp.png', dpi=300)

        # Turbine graphs
        turbine1 = plant_net.modules[1]

        (quant, time_unit) = turbine1.outflow_phase.get_quantity_history('power')

        quant.plot( x_scaling=1/unit.minute, x_label='Time [m]',
                    y_label=quant.formal_name+' ['+quant.unit+']',
                    title='High Pressure Turbine Power')
        plt.grid()
        plt.savefig('turbine1-power.png', dpi=300)

        (quant, time_unit) = turbine1.outflow_phase.get_quantity_history('temp')

        quant.plot( x_scaling=1/unit.minute, x_label='Time [m]',
                    y_label=quant.formal_name+' ['+quant.unit+']',
                    title='High Pressure Turbine Outflow Temperature')
        plt.grid()
        plt.savefig('turbine1-outflow-temp.png', dpi=300)

        # Turbine graphs
        turbine2 = plant_net.modules[2]

        (quant, time_unit) = turbine1.outflow_phase.get_quantity_history('power')

        quant.plot( x_scaling=1/unit.minute, x_label='Time [m]',
                    y_label=quant.formal_name+' ['+quant.unit+']',
                    title='Lower Pressure Turbine 1 Power')
        plt.grid()
        plt.savefig('turbine2-power.png', dpi=300)

        (quant, time_unit) = turbine2.outflow_phase.get_quantity_history('temp')

        quant.plot( x_scaling=1/unit.minute, x_label='Time [m]',
                    y_label=quant.formal_name+' ['+quant.unit+']',
                    title='Lower Pressure Turbine 1 Outflow Temperature')
        plt.grid()
        plt.savefig('turbine2-outflow-temp.png', dpi=300)

        # Condenser graphs
        condenser = plant_net.modules[-1]

        (quant, time_unit) = condenser.outflow_phase.get_quantity_history('temp')

        quant.plot( x_scaling=1/unit.minute, x_label='Time [m]',
                    y_label=quant.formal_name+' ['+quant.unit+']')
        plt.grid()
        plt.savefig('condenser-outflow-temp.png', dpi=300)

    # Properly shutdow plant
    plant.close()

if __name__ == '__main__':
    main()
