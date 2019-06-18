#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org

import numpy as np
from threading import Thread
import matplotlib.pyplot as plt
from cortix.src.module import Module
from cortix.support.phase import Phase
from cortix.support.specie import Specie
from cortix.support.quantity import Quantity

class Vortex(Module):
    '''
    Vortex module used to model fluid flow using Cortix.
    '''

    def __init__(self):
        super().__init__()

        species = []
        quantities = []

        air = Specie(name='air', formula_name='Air', phase='gas')
        air.massCCUnit = 'g/cc'
        air.molarCCUnit = 'mole/cc'
        air.molarMass = 0.3 * 16 * 2 + 0.7 * 14 *2
        species.append(air)

        # Domain box dimensions: LxLxH m^3 box with given H.
        # z coordinate pointing upwards. -L <= x <= L, -L <= y <= L, 
        # z component is positive => vortex is blowing upwards.
        self.box_half_length = 250.0 # vortex box [m] 
        self.box_height      = 250.0 # [m]

        # Vortex parameters.
        self.min_core_radius = 2.5 # [m]
        self.outer_v_theta   = 1.0 # m/s # angular speed
        self.v_z_0 = 0.50 # [m/s]

        self.time_step = 0.1

    def run(self):
        for i in range(100):
            time = 0.0
            for drop_index in range(int(len(self.ports) / 2)):
                request_port = "droplet-request-{}".format(drop_index)
                velocity_port = "velocity-{}".format(drop_index)

                # Query the droplet for a request
                (droplet_time, droplet_position) = self.recv(request_port)

                # Compute the vortex velocity using the droplet position
                velocity = self.compute_velocity(droplet_position)

                # Send the vortex velocity to the droplet
                self.send((time,velocity), velocity_port)
            time += 0.1
        #self.plot_vortex_velocity()

    def compute_velocity(self, position):
        '''
        Compute the vortex velocity at the given external
        position using a vortex flow model

        Parameters
        ----------
        position: numpy.ndarray(3)

        Returns
        -------
        vortex_velocity: numpy.ndarray(3)
        '''

        outer_cylindrical_radius = np.hypot(self.box_half_length, self.box_half_length)
        circulation = 2 * np.pi * outer_cylindrical_radius * self.outer_v_theta # m^2/s
        core_radius = self.min_core_radius

        x = position[0]
        y = position[1]
        z = position[2]

        relax_length = self.box_height / 2.0
        z_relax_factor = np.exp(-(self.box_height-z)/relax_length)
        v_z = self.v_z_0 * z_relax_factor

        cylindrical_radius = np.hypot(x,y)
        azimuth = np.arctan2(y,x)

        v_theta = (1 - np.exp(-cylindrical_radius**2 / 8 / core_radius**2)) *\
                   circulation / 2 / np.pi / max(cylindrical_radius,self.min_core_radius) *\
                   z_relax_factor

        v_x = - v_theta * np.sin(azimuth)
        v_y =   v_theta * np.cos(azimuth)

        return np.array([v_x,v_y,v_z])

    def plot_vortex_velocity(self):
        '''
        Plot the vortex velocity as a function of height
        '''
        (fig,axs) = plt.subplots(2,2)
        fig.subplots_adjust(hspace=0.5, wspace=0.5)

        for z in np.flip(np.linspace(0, self.box_height,3), 0):
            xval = []
            yval = []
            for x in np.linspace(0, self.box_half_length, 500):
                xval.append(x)
                y = 0.0
                vortex_velocity = self.compute_velocity(np.array([x,y,z]))
                yval.append(vortex_velocity[1])

            axs[0,0].plot(xval, yval, label='z =' + str(round(z,2))+' [m]')

        axs[0,0].set_xlabel('Radial distance [m]')
        axs[0,0].set_ylabel('Tangential speed [m/s]')
        axs[0,0].legend(loc='best')
        fig.suptitle('Vortex Flow')
        axs[0,0].grid(True)

        xval = []
        yval = []
        for z in np.linspace(0,self.box_height,50):
            yval.append(z)
            vortex_velocity = self.compute_velocity(np.array([0.0,0.0,z]) )
            xval.append(vortex_velocity[2])

        axs[0,1].plot(xval,yval)
        axs[0,1].set_xlabel('Vertical speed [m/s]')
        axs[0,1].set_ylabel('Height [m]')
        axs[0,1].grid(True)

        fig.savefig('vortex_velocity.png',dpi=200)
