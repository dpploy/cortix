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

class Messenger:
    def __init__(self, circle=None, collision = [], timestamp='0'):
##        self.collision = [dict(name='',v0=[0.0,0.0],p0=[0.0,0.0])] #format
        self.collision = []
        self.timestamp = timestamp
        self.m = 1
        self.r = 1
        self.v = [0.0,0.0]
        self.p = [0.0,0.0]
        self.name = ''
        self.ke = 0
        self.color = 'b'
        self.elapsed = 0

class Particle:
    def __init__(self,shape,bn=None,color='b',r=1):
        super().__init__()
        self.shape = shape
        self.bndry = []
        coords = list(self.shape.exterior.coords)
        self.bndic = dict()
        self.t_step = 0.01
        #Parse the box(LineRing) to create a list of line obstacles
        for c,f in enumerate(coords):
            try:
                cr = geo.LineString([coords[c],coords[c+1]])
                self.bndic[str(cr)] = geo.LineString([coords[c],coords[c+1]])
            except IndexError:
                cr = geo.LineString([coords[c],coords[-1]])
                self.bndic[str(cr)] = geo.LineString([coords[c],coords[-1]])
                           
                break
            
            self.bndry.append(cr)
        if bn==None:
            bn = self.shape.bounds
        self.r=r
        for i in range(100): #Attempt to spawn ball within boundary
            self.p0 = [random.uniform(bn[0],bn[2]),random.uniform(bn[1],bn[3])]
            self.pnt = geo.point.Point(self.p0[0],self.p0[1])
            self.circle = self.pnt.buffer(self.r)
            if self.shape.contains(self.circle):
                break
        if i>85:
            print('Warning, ball took:',i,'attempts to spawn')
        self.v0 = [random.uniform(-50,50),random.uniform(-30,30)]
        self.cor = 1.0
        self.a = (0,0)
        self.m = 1
        self.ke = 0.5*self.m*((self.v0[0]**2+self.v0[1]**2)**0.5)**2
        self.timestamp=str(datetime.datetime.now())
        self.collision=[]
        self.name = ''.join([random.choice(string.ascii_lowercase+string.digits) for f in range(10)])
        #Customize container class that is sent to other modules
        self.messenger = Messenger()
        self.messenger.timestamp = self.timestamp
        self.messenger.m,self.messenger.r = self.m,self.r
        self.messenger.v = self.v0
        self.messenger.p = self.p0
        self.messenger.name = self.name
        self.messenger.color = color
        self.messenger.elapsed = 0
        self.messenger.ke = self.ke
        self.mycollisions = []

    def run(self, ball_list):
        self.ball_list = ball_list
        self.collisions=0
        t = self.t_step
        self.messenger.elapsed += t

        for ball in self.ball_list: #Detects collision with other objects
            #Reacts to intersection between this object and another
            for c,line in enumerate(ball.collision): #Undetected Collisions received as a message
                pnt = geo.point.Point(line['p0'])
                shape = pnt.buffer(ball.r)
##                print(line, self.mycollisions)
                if self.name == line['name'] and line not in self.mycollisions:
##                    print('messenger:', self.name,line['name'],[f['name'] for f in self.mycollisions])
##                    print('Check!!!!')
                    p0,v0 = line['p0'],line['v0']
                    self.ball_collision(ball,p0,v0)
                    if self.circle.crosses(shape) or self.circle.touches(shape) or self.circle.intersects(shape):
                        self.ball_shift(shape)
                    del ball.collision[c]
##                    print(ball.collision)
                for d, col in enumerate(self.mycollisions):
                    if line == col and col!= []:
                        del self.mycollisions[d]
                        del ball.collision[c]
                        
        #Gravity calculations for timestep
        self.p0[1] = 0.5*self.a[1]*t**2+self.v0[1]*t+self.p0[1]
        self.p0[0] = 0.5*self.a[0]*t**2+self.v0[0]*t+self.p0[0]
        self.v0[1] = self.a[1]*t + self.v0[1]
        self.v0[0] = self.a[0]*t + self.v0[0]
        #Update position and velocity variables
        self.pnt = geo.point.Point(self.p0[0],self.p0[1])
        self.circle = self.pnt.buffer(self.r)
        self.messenger.v = self.v0
        
        
        for ball in self.ball_list: #Detects collision with other objects
            if self.name==ball.name:
                continue
            #ball is Messenger class object
            pnt = geo.point.Point(ball.p)
            shape = pnt.buffer(ball .r)
            name = ball.name
            
            if self.circle.crosses(shape) or self.circle.touches(shape) or self.circle.intersects(shape):
                coldic = dict(name=ball.name,v0=self.v0,p0=self.p0,elapsed=self.messenger.elapsed)
                self.mycollisions.append(coldic)
                self.messenger.collision.append(coldic)
                self.ball_collision(ball,ball.p,ball.v)
##                print(self.name,ball.name)
                self.ball_shift(shape)
                
        
        for shape in self.bndry: #Detects collision with boundary
            if self.circle.crosses(shape) or self.circle.touches(shape) or self.circle.intersects(shape):
                self.wall_collision(shape)            
        self.messenger.p = self.p0
        self.ke = 0.5*self.m*((self.v0[0]**2+self.v0[1]**2)**0.5)**2
        self.messenger.ke = self.ke
        return self.messenger

    def wall_collision(self,shape):
        
        p1,p2 = shapely.ops.nearest_points(self.pnt,shape)
        angle3 = np.arctan2(p2.y - p1.y, p2.x - p1.x)
        d = shape.distance(self.pnt)
        self.p0 = [self.p0[0]-(self.r-d)*np.cos(angle3), self.p0[1]-(self.r-d)*np.sin(angle3)]
        self.pnt = geo.point.Point(self.p0[0],self.p0[1])
        self.circle = self.pnt.buffer(self.r)
        
        angle2 = np.arctan2(self.v0[1], self.v0[0])
        v = (self.v0[0]**2+self.v0[1]**2)**0.5
        theta = angle2-angle3
        vbi, vbj = v*np.sin(theta), v*np.cos(theta)
        vbj = -vbj *self.cor
        v = (vbi**2+vbj**2)**0.5
        angle4 = np.arctan2(vbj, vbi)
        angle1 = angle4 - angle3
        self.collisions+=1
        self.v0 = [np.sin(angle1)*v, np.cos(angle1)*v]

        
    def ball_shift(self,shape):
        p1,p2 = shapely.ops.nearest_points(self.pnt,shape)
        angle = np.arctan2(p2.y - p1.y, p2.x - p1.x)
        d = shape.distance(self.pnt)
        self.p0 = [self.p0[0]-(self.r*1.01-d)*np.cos(angle),self.p0[1]-(self.r*1.01-d)*np.sin(angle)]
        self.pnt = geo.point.Point(self.p0[0],self.p0[1])
        self.circle = self.pnt.buffer(self.r)
        
    def ball_collision(self,messenger,p0,v0):
##        pnt = geo.point.Point(p0[0],p0[1])
##        shape = pnt.buffer(messenger.r)
        v2,m = v0,messenger.m
        v3 = (v2[0]**2+v2[1]**2)**0.5
        phi = np.arctan2(v2[1],v2[0])
        p2x,p2y = p0[0],p0[1]
        angle = np.arctan2(p2y - self.p0[1], p2x - self.p0[0]) 
        angle2 = np.arctan2(self.v0[1], self.v0[0])
        v = (self.v0[0]**2+self.v0[1]**2)**0.5
        
        #Equation source: https://en.wikipedia.org/wiki/Elastic_collision
        vpx=((v*np.cos(angle2-angle)*(self.m-m)+2*m*v3*np.cos(phi-angle))/(self.m+m))*np.cos(angle)+v*np.sin(angle2-angle)*np.cos(angle+np.pi/2)
        vpy=((v*np.cos(angle2-angle)*(self.m-m)+2*m*v3*np.cos(phi-angle))/(self.m+m))*np.sin(angle)+v*np.sin(angle2-angle)*np.sin(angle+np.pi/2)
        vp = (vpx**2+vpy**2)**0.5
        self.v0 = [vpx,vpy]
