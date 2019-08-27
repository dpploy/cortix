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
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd

class Body_Plot(Module):
    def __init__(self,modules=5):
        super().__init__()
        self.filetime = str(datetime.datetime.now())[:10]
        self.dir = '/tmp/bb'
        self.fps = 60
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        self.filename = os.path.join(self.dir,'bb_data'+self.filetime+'.csv')
        self.length = modules
        self.timestamp=str(datetime.datetime.now())


    def run(self):
        print('start plot')
        self.dic = {}
        c = 0
        
        writer = animation.FFMpegFileWriter(fps=self.fps)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlim3d(0,1000)
        ax.set_ylim3d(0,1000)
        ax.set_zlim3d(0,1000)
##        ax.axis('off')
##        ax.set_aspect( 'equal', adjustable='datalim')
        self.linedic = {}
        self.dpi = 90
        anifilename = 'nbody_animation.mp4'
        writer.setup(fig,anifilename, dpi=self.dpi)
        modcount=0
        while True:
            for i in self.ports:
                if not 'plot' in str(i):
                    continue
                line = self.recv(i)
                self.send('hi',i)
##                print(line)
                if isinstance(line,str):
                    c+=1
                    if c >=self.length:
                        writer.finish()
                        return
                    continue
                
                if line['name'] not in self.dic:
                    self.dic[line['name']]=[]
                    self.linedic[line['name']], = ax.plot([],[],[],'bo')
                x,y,z = line['pos']
                self.linedic[line['name']].set_data(x,y)
                self.linedic[line['name']].set_3d_properties(z)
##                ax.relim()
##                ax.auto_scale_xyz(X=True, Y=True, Z=True)#(tight=True, scalex=True, scaley=True, scalez=True)
##                ax.relim()
##                ax.autoscale_view()
                modcount+=1
                if modcount >= self.length:
                    ax.relim()
                    ax.autoscale_view(True,True,True)
                    writer.grab_frame()
                    modcount = 0
