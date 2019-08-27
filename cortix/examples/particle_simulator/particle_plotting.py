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

class Particle_Plot(Module):
    def __init__(self, shape,modules=5,runtime=None):
        super().__init__()
        self.filetime = str(datetime.datetime.now())[:10]
        self.dir = '/tmp/bb'
        self.fps = 60
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        self.filename = os.path.join(self.dir,'bb_data'+self.filetime+'.csv')
        self.length = modules
        self.shape = shape
        self.timestamp=str(datetime.datetime.now())
        self.bndry = []
        coords = list(self.shape.exterior.coords)
        #Parse the box(LineRing) to create a list of line obstacles
        self.colordic = dict()
        for c,f in enumerate(coords):
            try:
                cr = geo.LineString([coords[c],coords[c+1]])
            except IndexError:
                cr = geo.LineString([coords[c],coords[-1]])
                break
            
            self.bndry.append(cr)

    def run(self):
        print('start plot')
        self.dic = {}
        c = 0
        
        writer = animation.FFMpegFileWriter(fps=self.fps)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        x,y = self.shape.exterior.xy
        ax.plot(x,y,'black')
        ax.axis('off')
        ax.autoscale()
        ax.set_aspect( 'equal', adjustable='datalim')
        ax.relim()
        
        modcount,self.oe=0,0
        self.linedic = {}
        tempdir='.writer'
        self.dpi = 90
        anifilename = 'bb_animation.mp4'
        writer.setup(fig,anifilename, dpi=self.dpi)
        self.tke=0
        self.ke,self.elapsed = [],[]
        while True:
            for i in self.ports:
                if not 'plot' in str(i):
                    continue
                lis = self.recv(i)
                self.send('hi',i)
                if isinstance(lis,str):
                    c+=1
                    self.color=lis
                    if c >=self.length:
                        writer.finish()
                        print(len(self.ke))
                        fig = plt.figure()
                        plt.plot(self.elapsed,self.ke)
##                        plt.autoscale()
##                        plt.relim()
                        plt.title("Total Kinetic Energy vs Time")
                        plt.savefig('energy_vs_time.png')
                        return
                    continue
                
                for line in lis:
                    self.colordic[line.name] = [line.color, line.r]
                    if line.name not in self.dic:
                        self.dic[line.name]=[]
                        self.linedic[line.name], = ax.plot([],[],self.colordic[line.name][0])
                    self.tke += line.ke
                    pnt = geo.point.Point(line.p)
                    circle = pnt.buffer(self.colordic[line.name][1])
                    x,y = circle.exterior.xy
                    self.linedic[line.name].set_data(x,y)
                modcount+=1
                elapsed = line.elapsed
                if round(elapsed,1) > self.oe:
                    print('Elapsed Time:', round(elapsed,1))
                    self.oe=round(elapsed,1)
                if modcount >= self.length:
                    self.ke.append(self.tke)
                    self.elapsed.append(elapsed)
                    self.tke=0
                    writer.grab_frame()
                    modcount = 0
