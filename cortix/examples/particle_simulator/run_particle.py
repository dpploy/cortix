import os, time, datetime, threading, random, sys, string
import numpy as np
from cortix.src.module import Module
from cortix.src.network import Network
from cortix.src.cortix_main import Cortix
import shapely.geometry as geo
import shapely.ops
import matplotlib.pyplot as plt
import matplotlib
##matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.animation as animation
import pandas as pd
from cortix.examples import Particle_Plot
from cortix.examples import Particle_Handler

class Simulation:
    def __init__(self):
        self.n_list = [15,]

        self.procs = 15
        self.runtime=30
        self.t_step = 0.01
        
        self.r=1
        self.mod_list = []
        self.shape = geo.Polygon([(0, 0), (0, 100), (100, 100),(100,0)])

        self.fps = 60

    def run(self):
        for c,i in enumerate(self.n_list):
            self.cortix = Cortix(use_mpi=False)
            self.net = Network()
            self.cortix.network = self.net
            self.plot = Particle_Plot(self.shape,modules=self.procs,runtime=self.runtime)
            self.plot.fps = self.fps
            self.net.add_module(self.plot)
            print(c,'iterations')
            self.balls = i
            self.balleach = int(self.balls/self.procs)
            self.mod_list = []
            for i in range(self.procs):    
                app = Particle_Handler(self.shape, balls=self.balleach,runtime = self.runtime)
                app.r=self.r
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
    def plotting(self):
        print('started thread')
        flist = sorted([f for f in os.listdir()])
        for f in flist:
            if f.startswith('_tmp') and f.endswith('.png'):
                os.remove(f)
        fig = plt.figure()
        fig.set_size_inches((8,8))
        ax = fig.add_subplot(111)
        ax.axis('off')
        img = 255 * np.ones(shape=[1200,1600,3], dtype=np.uint8)
        picture = ax.imshow(img,interpolation='nearest')
        plt.ion()
        piclist=[]
        while True:
            flist = sorted([f for f in os.listdir()])
            for f in flist:
                if f.startswith('_tmp') and f.endswith('.png') and f not in piclist:
                    try:
                        img=mpimg.imread(f)
                    except OSError:
                        time.sleep(0.1)
                        continue
                    picture.set_data(img)
                    piclist.append(f)
                    plt.draw()
                    plt.pause(0.05)

if __name__ == '__main__':
    sim = Simulation()
    sim.runtime = 6
    sim.r = 1
    sim.fps = 100
    sim.shape = geo.Polygon([(0, 0), (0, 20), (20, 20),(20,0)]).buffer(0.5)
    sim.t_step = 0.01
    sim.procs = 3
    sim.n_list = [3]
    sim.run()

