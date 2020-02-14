#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org

import logging

import math
import numpy as np
import scipy.constants as unit
from scipy.integrate import odeint

from cortix import Module
from cortix.support.phase_new import PhaseNew as Phase
from cortix import Quantity

class UMLRR(Module):
    '''
    UMass Lowell research nuclear reactor single-point model.

    Notes
    -----
    These are the `port` names available in this module

      coolant-inflow, coolant-outflow, signal-out, signal-in

    to connect to other modules if any.
    See instance attribute `port_names_expected`.

    '''

    def __init__(self, params):
        '''
        Parameters
        ----------
        params: dict
            All parameters for the module in the form of a dictionary.

        '''

        super().__init__()

        self.port_names_expected = ['coolant-inflow', 'coolant-outflow',
                                    'signal-out', 'signal-in']

        self.initial_time = 0.0 * unit.day
        self.end_time     = 4 * unit.hour
        self.time_step    = 10.0
        self.show_time    = (False,10.0)
        self.log = logging.getLogger('cortix')

        self.params = dict()

        self.params['gen_time'] = 1.0e-4  # s
        self.params['beta']     = 6.5e-3  # 
        self.params['species_decay']     = [0.0124, 0.0305, 0.111, 0.301, 1.14, 3.01] # 1/sec
        self.params['species_rel_yield'] = [0.033, 0.219, 0.196, 0.395, 0.115, 0.042]

        self.params['alpha_n']       = -5e-4 # control rod reactivity worth
        self.params['alpha_tn_fake'] = -1e-4/20# -1.0e-6

        self.params['n_dens_ss_operation'] = 1e15 * 1e4 / 2200  # neutrons/m^2

        self.params['fis_energy']           = 180 * 1.602e-13 # J/fission 
        self.params['sigma_f_o']            = 586.2 * 100 * 1e-30 # m2
        self.params['temp_o']               = 20 + 273.15 # K
        self.params['temp_c_ss_operation']  = 550 + 273.15 # K desired ss operation temp of coolant
        self.params['temp_f_safe_max']      = 1100 + 273.15 # K
        self.params['thermal_neutron_velo'] = 2200 # m/s
        self.params['fis_nuclide_num_dens_fake'] = 1e17/40 * 1.0e+6 # (fissile nuclei)/m3

        self.params['fuel_dens']   = 2500 # kg/m3
        self.params['cp_fuel']     = 720 # J/(kg K)
        self.params['fuel_volume'] = 1.5 # m3

        self.params['coolant_dens']   = 0.1786 #  kg/m3
        self.params['cp_coolant']     = 20.78 / 4e-3 # J/(mol K) - > J/(kg K)
        self.params['coolant_volume'] = 0.8 # m3

        self.params['ht_coeff'] = 800 # W/K

        self.params['strict'] = True # apply strict testing to some quantities

        self.params['hx_malfunction'] = False
        self.params['hx_malfunction_start_time']  = 0
        self.params['hx_malfunction_down_time']   = 0
        self.params['hx_malfunction_temperature'] = 0

        self.params['hx_breakdown'] = False
        self.params['hx_breakdown_start_time'] = 0
        self.params['hx_breakdown_down_time']  = 0

        self.params['shutdown']      = False
        self.params['shutdown_time'] = 0.0 # s
        self.params['rho_shutdown']  = 0.0 # s
        self.params['hx_relax_time'] = 0 # s

        # Coolant outflow phase history
        quantities = list()

        flowrate = Quantity(name='flowrate', formal_name='q_c', unit='kg/s', value=0.0,
                info='Reactor Outflow Coolant Flowrate', latex_name='$q_c$')

        quantities.append(flowrate)

        temp = Quantity(name='temp', formal_name='T_c', unit='K', value=273.15,
                info='Reactor Outflow Coolant Temperature',latex_name='$T_c$')

        quantities.append(temp)

        self.coolant_outflow_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        # Reactor phase history
        quantities = list()

        neutron_dens = Quantity(name='neutron-dens', formal_name='n', unit='1/m^3',
                value=0.0,
                info='Reactor Neutron Density', latex_name='$n$')

        quantities.append(neutron_dens)

        delayed_neutron_cc = Quantity(name='delayed-neutrons-cc', formal_name='c_i',
                unit='1/m^3', value= np.zeros(6),
                info='Delayed Neutron Precursors', latex_name='$c_i$')

        quantities.append(delayed_neutron_cc)

        self.reactor_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        fuel_temp = Quantity( name='fuel-temp', formalName='T_f', unit='k',
                value=273.15, info='Reactor Nuclear Fuel Temperature',
                latex_name='$T_f$')

        quantities.append(fuel_temp)

        self.reactor_phase = Phase(self.initial_time, time_unit='s',
                quantities=quantities)

        # Initialize inflow
        self.params['inflow-cool-temp'] = 273.15

        return

    def run(self):

        # Some logic for logging time stamps
        if self.initial_time + self.time_step > self.end_time:
            self.end_time = self.initial_time + self.time_step

        time = self.initial_time

        print_time = self.initial_time
        print_time_step = self.show_time[1]
        if print_time_step < self.time_step:
            print_time_step = self.time_step

        while time <= self.end_time:

            last_time_stamp = time - self.time_step

            if self.show_time[0] and time>=print_time and \
                    time<print_time+print_time_step:

                self.log.info(self.name+'::run():time[s]='+ str(round(time,1)))

                self.__logit = True
                print_time += self.show_time[1]

            else:
                self.__logit = False

            # Communicate information
            #------------------------
            self.__call_ports(time)

            # Evolve one time step
            #---------------------

            time = self.__step( time )

    def __call_ports(self, time):

        # Interactions in the coolant-outflow port
        #-----------------------------------------
        # one way "to" coolant-outflow

        # send to 
        if self.get_port('coolant-outflow').connected_port:

            message_time = self.recv('coolant-outflow')

            coolant_outflow = self.__get_coolant_outflow( message_time )
            outflow_params = dict()
            self.send( (message_time, coolant_outflow), 'coolant-outflow' )

        # Interactions in the coolant-inflow port
        #----------------------------------------
        # one way "from" coolant-inflow

        # receive from
        if self.get_port('coolant-inflow').connected_port:

            self.send( time, 'coolant-inflow' )
            (check_time, inflow_cool_temp) = self.recv('coolant-inflow')

            assert abs(check_time-time) <= 1e-6
            self.params['inflow-cool-temp'] = inflow_cool_temp

        # Interactions in the signal-out port
        #-----------------------------------------
        # one way "to" signal-out 

        # send to 
        if self.get_port('signal-out').connected_port:

            message_time = self.recv('signal-out')

            signal_out = self.__get_signal_out(time)

            self.send( (message_time, signal_out), 'signal-out' )

    def __get_coolant_outflow(message_time):

        outflow = self.params['coolant-outflow']

        return(outflow)

    def __step(self, time=0.0):
        r'''
        ODE IVP problem:
        Given the initial data at :math:`t=0`,
        :math:`u = (u_1(0),u_2(0),\ldots)`
        solve :math:`\frac{\text{d}u}{\text{d}t} = f(u)` in the interval
        :math:`0\le t \le t_f`.

        Parameters
        ----------
        time: float
            Time in SI unit.

        Returns
        -------
        None

        '''

        # Get state values
        u_0 = self.__get_state_vector( time )

        t_interval_sec = np.linspace(0.0, self.time_step, num=2)

        (u_vec_hist, info_dict) = odeint( self.__f_vec,
                                          u_0, t_interval_sec,
                                          args=( self.params, ),
                                          rtol=1e-4, atol=1e-8, mxstep=200,
                                          full_output=True )

        assert info_dict['message'] =='Integration successful.', info_dict['message']

        u_vec = u_vec_hist[1,:]  # solution vector at final time step

        n_dens    = u_vec[0]
        c_vec     = u_vec[1:7]
        fuel_temp = u_vec[7]
        cool_temp = u_vec[8]

        #update state variables
        outflow  = self.coolant_outflow_phase.get_row(time)
        neutrons = self.neutron_phase.get_row(time)
        reactor  = self.reactor_phase.get_row(time)
        self.params['outflow temp'] = cool_temp
        time += self.time_step

        self.coolant_outflow_phase.add_row(time, outflow)
        self.neutron_phase.add_row(time, neutrons)
        self.reactor_phase.add_row(time, reactor)

        self.coolant_outflow_phase.set_value('temp', cool_temp, time)
        self.neutron_phase.set_value('neutron-dens', n_dens, time)
        self.neutron_phase.set_value('delayed-neutrons-cc', c_vec, time)
        self.reactor_phase.set_value('fuel-temp', fuel_temp, time)

        return time

    def __signal_out(self, time=0.0):
        '''
        Send reactor signals to anyone requesting it.

        Parameters
        ----------
        time: float
            Time in SI unit.

        Returns
        -------
        None

        '''

        signals = dict()

        return signals

    def __get_coolant_outflow(self, time=0.0):
        '''
        Get the coolant outflow stream.

        Parameters
        ----------
        time: float
            Time in SI unit.

        Returns
        -------
        None

        '''

        coolant_outflow_stream = dict()

        outflow_cool_temp = self.coolant_outflow_phase.get_value('temp', time)

        coolant_outflow_stream['temp'] = outflow_cool_temp

        return coolant_outflow_stream

    def __get_state_vector(self, time):
        '''
        Return a numpy array of all unknowns ordered as below:
        neutron density (1), delayed neutron emmiter concentrations (6),
        termperature of fuel (1), temperature of coolant (1).
        '''

        u_vec = np.empty(0,dtype=np.float64)

        neutron_dens = self.reactor_phase.get_value('neutron-dens',time)
        u_vec = np.append( u_vec, neutron_dens )

        delayed_neutrons_cc = self.reactor_phase.get_value('delayed-neutrons-cc',time)
        u_vec = np.append(u_vec, delayed_neutrons_cc)

        fuel_temp = self.reactor_phase.get_value('fuel-temp',time)
        u_vec = np.append( u_vec, fuel_temp)

        temp = self.coolant_outflow_phase.get_value('temp',time)
        u_vec = np.append(u_vec, temp)

        # sanity check
        assert not u_vec[u_vec<0.0],'%r'%u_vec

        return u_vec

    def __alpha_tn_func(self, temp, params):
        '''
        Reactivity temperature feedback coefficient.

        '''

        alpha_tn = params['alpha_tn_fake']

        return alpha_tn

    def __rho_func(self, t, n_dens, temp, params):
        '''
        Reactivity function.

        Parameters
        ----------
        t: float, required
            Time.
        temp_f: float, required
            Temperature at time t.
        params: dict, required
            Dictionary of quantities. It must have a `'rho_0'` key/value pair.

        Returns
        -------
        rho_t: float
            Value of reactivity.

        Examples
        --------

        '''

        if params['shutdown'] == False or (params['shutdown'] == True and time < params['shutdown_time']):
            rho_0 = params['rho_0']
            n_dens_ref = params['n_dens_ref']
            temp_ref = params['temp_c_ss_operation']
            alpha_n  = params['alpha_n']
            alpha_tn = alpha_tn_func( temp, params )
        elif params['shutdown'] == True and time >= params['shutdown_time']:
            rho_0 = params['rho_shutdown']
            n_dens_ref = 0.0
            temp_ref = params['temp_o']
            alpha_n  = 0
            alpha_tn = 0
        else:
            assert False

        rho_t = rho_0 + alpha_n * (n_dens - n_dens_ref) + alpha_tn * (temp - temp_ref)

        beta = params['beta']

        if params['strict'] == True:
            assert rho_t/beta < 1,'rho/beta = %r at time = %r; rho_0 = %r; rho_n = %r; rho_tn = %r'%( rho_t/beta, time, rho_0/beta, alpha_n*(n_dens - n_dens_ref)/beta, alpha_tn*(temp - temp_ref)/beta )

        return rho_t

    def __q_source(self, t, params):
        '''
        Neutron source delta function.

        Parameters
        ----------
        t: float, required
            Time.
        params: dict, required
            Dictionary of quantities. It must have a `'q_0'` key/value pair.

        Returns
        -------
        q: float
            Value of source.

        Examples
        --------

        '''

        q = 0.0
        q_0 = params['q_0']

        if t <= 1e-5: # small time value
            q = q_0
        else:
            q = 0.0

        return q

    def __sigma_fis_func(self, temp, params):
        '''
        Place holder for implementation
        '''

        sigma_f = params['sigma_f_o']

        return sigma_f

    def __nuclear_pwr_dens_func(self, time, temp, n_dens, params ):
        '''
        Place holder for implementation
        '''

        rxn_heat = params['fis_energy'] # get fission reaction energy J per reaction

        sigma_f = self.__sigma_fis_func( temp, params ) # m2

        fis_nuclide_num_dens = params['fis_nuclide_num_dens_fake'] #  #/m3

        Sigma_fis = sigma_f * fis_nuclide_num_dens # macroscopic cross section

        v_o = params['thermal_neutron_velo'] # m/s

        neutron_flux = n_dens * params['n_dens_ss_operation'] * v_o

        # reaction rate density
        rxn_rate_dens = Sigma_fis * neutron_flux

        # nuclear power source
        q3prime = - rxn_heat * rxn_rate_dens # exothermic reaction W/m3

        if params['strict'] == True:
            assert q3prime <= 0.0,"time = %r, q''' = %r, n_dens = %r"%(time,q3prime,n_dens)

        return q3prime

    def __heat_sink_rate(self, time, temp_f, temp_c, params):

        ht_coeff = params['ht_coeff']

        q_f = - ht_coeff * (temp_f - temp_c)

        if params['strict'] == True:
            assert q_f <= 0.0,'q_f = %r at time = %r; temp_f = %r, temp_c = %r'%(q_f,time,temp_f,temp_c)

        return q_f

    def __f_vec(self, u_vec, time, params):
        '''
        ODE RHS function
        '''

        import numpy as np
        #assert np.all(u_vec >= 0.0),'time = %r; u_vec = %r'%(time,u_vec)

        n_dens = u_vec[0] # get neutron dens

        c_vec = u_vec[1:-2] # get delayed neutron emitter concentration

        temp_f = u_vec[-2] # get temperature of fuel

        temp_c = u_vec[-1] # get temperature of coolant

        # initialize f_vec to zero
        species_decay = params['species_decay']
        lambda_vec    = np.array(species_decay)
        n_species     = len(lambda_vec)

        assert len(lambda_vec)==len(c_vec)

        f_tmp = np.zeros(1+n_species+2,dtype=np.float64) # vector for f_vec return

        #----------------
        # neutron balance
        #----------------
        rho_t    = self.__rho_func(time, n_dens, (temp_f+temp_c)/2.0, params)

        beta     = params['beta']
        gen_time = params['gen_time']

        q_source_t = self.__q_source(time, params)

        f_tmp[0] = (rho_t - beta)/gen_time * n_dens + lambda_vec @ c_vec + q_source_t

        #-----------------------------------
        # n species balances (implicit loop)
        #-----------------------------------

        species_rel_yield = params['species_rel_yield']
        beta_vec = np.array(species_rel_yield) * beta

        assert len(beta_vec)==len(lambda_vec)

        f_tmp[1:-2] = beta_vec/gen_time * n_dens - lambda_vec * c_vec

        #--------------------
        # fuel energy balance
        #--------------------
        rho_f    = params['fuel_dens']
        cp_f     = params['cp_fuel']
        vol_fuel = params['fuel_volume']

        pwr_dens = self.__nuclear_pwr_dens_func( time, (temp_f+temp_c)/2, n_dens, params )

        heat_sink = self.__heat_sink_rate( time, temp_f, temp_c, params )

        f_tmp[-2] = - 1/rho_f/cp_f * ( pwr_dens - heat_sink/vol_fuel )

        #-----------------------
        # coolant energy balance
        #-----------------------
        rho_c    = params['coolant_dens']
        cp_c     = params['cp_coolant']
        vol_cool = params['coolant_volume']

        temp_in = params['inflow-cool-temp']

        tau = params['tau_fake']

        heat_source = - heat_sink

        f_tmp[-1] = - 1/tau * (temp_c - temp_in) + 1./rho_c/cp_c/vol_cool * heat_source

        return f_tmp
