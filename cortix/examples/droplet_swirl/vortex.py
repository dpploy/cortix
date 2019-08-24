#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import logging

import numpy as np
import scipy.constants as const
from collections import namedtuple
import matplotlib
matplotlib.use('Agg', warn=False)
import matplotlib.pyplot as plt

from cortix.src.module import Module
from cortix.support.phase import Phase
from cortix.support.specie import Specie
from cortix.support.quantity import Quantity

class Vortex(Module):
    '''
    Vortex module used to model fluid flow using Cortix.

    Notes
    -----
    Any `port` name and any number of ports are allowed.

    '''

    def __init__(self):
        '''
        Attributes
        ----------
        initial_time: float
        end_time: float
        time_step: float
        show_time: tuple
            Two-element tuple, `(bool,float)`, `True` will print to standard
            output.

        '''

        super().__init__()

        species = list()
        quantities = list()

        self.initial_time = 0.0
        self.end_time = 5*const.minute
        self.time_step = 0.1
        self.show_time = (False,1*const.minute)
        self.log = logging.getLogger('cortix')

        air = Specie(name='air', formula_name='Air', phase='gas')
        air.massCCUnit = 'g/cc'
        air.molarCCUnit = 'mole/cc'
        air.molarMass = 0.3 * 16 * 2 + 0.7 * 14 *2
        species.append(air)

        # Constant values for the vortex fluid.
        self.mass_density  = 0.1 * const.gram / const.centi**3 # [kg/m^3]
        self.dyn_viscosity = 1.81e-5 # kg/(m s)

        # Domain box dimensions: LxLxH m^3 box with given H.
        # z coordinate pointing upwards. -L <= x <= L, -L <= y <= L, 
        # z component is positive => vortex is blowing upwards.
        self.box_half_length = 250.0 # vortex box [m] 
        self.box_height      = 500.0 # [m]

        # Vortex parameters.
        self.min_core_radius = 2.5 # [m]
        self.outer_v_theta   = 1.0 # m/s # angular speed
        self.v_z_0 = 0.50 # [m/s]

        self.period = 20 # wind change period

    def run(self, *args):

        # namedtuple does not pickle into send message; investigate later: vfda TODO
        #Props = namedtuple('Props',['mass_density','dyn_viscosity'])
        #fluid_props = Props( self.mass_density, self.dyn_viscosity )
        fluid_props = ( self.mass_density, self.dyn_viscosity )

        time = self.initial_time

        while time < self.end_time:

            if self.show_time[0] and abs(time%self.show_time[1]-0.0)<=1.e-1:
                self.log.info('Vortex::time[min] = '+str(round(time/const.minute,1)))

            # Interactions in all nameless ports (lower level port send/recv used)
            #---------------------------------------------------------------------

            for port in self.ports:
                (message_time, position) = port.recv()

                # Compute the vortex velocity using the given position
                velocity = self.compute_velocity(message_time, position)

                # Send the vortex velocity to caller
                port.send( (message_time, velocity, fluid_props) )

            time += self.time_step

        return

    def compute_velocity(self, time, position):
        '''
        Compute the vortex velocity at the given external
        position using a vortex flow model

        Parameters
        ----------
        time: float
            Time in SI unit.
        position: numpy.ndarray(3)
            Spatial position in SI unit.

        Returns
        -------
        vortex_velocity: numpy.ndarray(3)

        '''
        import math

        cycle_freq  = 1/self.period
        radian_freq = 2*math.pi*cycle_freq

        outer_cylindrical_radius = np.hypot(self.box_half_length, self.box_half_length)
        circulation = 2 * np.pi * outer_cylindrical_radius * self.outer_v_theta # m^2/s
        core_radius = self.min_core_radius

        x = position[0]
        y = position[1]
        z = position[2]

        relax_length = self.box_height / 2.0
        z_relax_factor = np.exp(-(self.box_height-z)/relax_length)
        v_z = self.v_z_0 * z_relax_factor * abs(math.cos( radian_freq * time))

        cylindrical_radius = np.hypot(x,y)
        azimuth = np.arctan2(y,x)

        v_theta = (1 - np.exp(-cylindrical_radius**2 / 8 / core_radius**2)) *\
                   circulation / 2 / np.pi /\
                   max(cylindrical_radius,self.min_core_radius) *\
                   z_relax_factor * abs(math.cos( radian_freq * time))

        v_x = - v_theta * np.sin(azimuth)
        v_y =   v_theta * np.cos(azimuth)

        return np.array([v_x,v_y,v_z])

    def plot_velocity(self, time=None):
        '''
        Plot the vortex velocity as a function of height.

        '''

        if time is None:
            time = self.initial_time

        (fig,axs) = plt.subplots(2,2)
        fig.subplots_adjust(hspace=0.5, wspace=0.5)

        for z in np.flip(np.linspace(0, self.box_height,3), 0):
            xval = list()
            yval = list()
            for x in np.linspace(0, self.box_half_length, 500):
                xval.append(x)
                y = 0.0
                vortex_velocity = self.compute_velocity( time,np.array([x,y,z]) )
                yval.append(vortex_velocity[1])

            axs[0,0].plot(xval, yval, label='z =' + str(round(z,2))+' [m]')

        axs[0,0].set_xlabel('Radial distance [m]')
        axs[0,0].set_ylabel('Tangential speed [m/s]')
        axs[0,0].legend(loc='best')
        fig.suptitle('Vortex Flow at '+str(round(time,1))+' [s]')
        axs[0,0].grid(True)

        xval = list()
        yval = list()
        for z in np.linspace(0,self.box_height,50):
            yval.append(z)
            vortex_velocity = self.compute_velocity( time,np.array([0.0,0.0,z]) )
            xval.append(vortex_velocity[2])

        axs[0,1].plot(xval,yval)
        axs[0,1].set_xlabel('Vertical speed [m/s]')
        axs[0,1].set_ylabel('Height [m]')
        axs[0,1].grid(True)

        fig.savefig('vortex_velocity.png',dpi=200)
        plt.close(fig)

        return
