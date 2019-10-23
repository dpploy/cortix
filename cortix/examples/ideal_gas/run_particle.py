import os, time, datetime, threading, random, sys, string
import numpy as np
from cortix import Module
from cortix import Network
from cortix import Cortix
from cortix.examples import Particle_Plot
from cortix.examples import Particle_Handler

class Run_Particle:
    def __init__(self):
        self.n_list = [15,]

        self.procs = 15
        self.runtime=30
        self.t_step = 0.01
        
        self.r=1
        self.mod_list = []
        self.shape = [(-40, -50), (-40, 90), (90, 60),(60,-30),(30,-50),(-40, -50)]
        self.a = (0,0)
        self.cor = 1
        self.fps = 60

    def run(self):
        if not isinstance(self.n_list, list):
            self.n_list=[self.n_list,]
        for c,i in enumerate(self.n_list):
            self.cortix = Cortix(use_mpi=False)
            self.net = Network()
            self.cortix.network = self.net
            self.plot = Particle_Plot(self.shape,balls=i,modules=self.procs,runtime=self.runtime)
            self.plot.fps = self.fps
            self.net.add_module(self.plot)
            print(c+1,'iterations')
            self.balls = i
            self.balleach = int(self.balls/self.procs)
            remainder = self.balls % self.procs
            self.mod_list = []
            for i in range(self.procs):
                balls = self.balleach
                if remainder > 0:
                    balls+=1
                    remainder -= 1
                app = Particle_Handler(self.shape, balls=balls,runtime = self.runtime)
                app.r=self.r
                app.a=self.a
                app.cor = self.cor
                app.t_step = 0.01
                self.mod_list.append(app)
                self.net.add_module(app)
            for c,i in enumerate(self.mod_list):
                self.net.connect([i,'plot-send{}'.format(c)],[self.plot,'plot-receive{}'.format(c)])
                for j in self.mod_list:
                    if i == j:
                        continue
                    name = '{}{}'.format(i.name,j.name)
                    name2 = '{}{}'.format(j.name,i.name)
                    self.net.connect([i,name], [j,name2])
##            threading.Thread(target=self.plotting,daemon=True).start()
            self.cortix.run()
            self.cortix.close()
            del self.cortix
            print('finished sim')


if __name__ == '__main__':
    sim = Run_Particle()
    sim.runtime = int(input('How many seconds do you want the simulation?: '))
    sim.r = 1
    sim.fps = 100
    sim.shape = [(-40, -50), (-40, 90), (90, 60),(60,-30),(30,-50),(-40, -50)]
##    sim.shape = [(0, 0), (0, 30), (30, 30),(30,25),
##                                  (65,25),(65,-20),(85,-20),(85,-40),
##                                  (45,-40),(45,-20),(49,-20),(49,15),
##                                  (30,15),(30,0),(0,0)]
    sim.t_step = 0.01
    sim.a = (0,0)
    sim.cor = 1
    sim.procs = int(input("How many processes would you like to use?: "))
    sim.n_list = int(input("How many particles would you like to simulate?: "))
    sim.n_list = [sim.n_list,]
    sim.run()

