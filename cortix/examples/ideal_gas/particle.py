import os, time, datetime, threading, random, sys, string, math
import numpy as np
from cortix import Module
from cortix import Network
from cortix import Cortix

class Messenger:
    def __init__(self, circle=None, collision = [], timestamp='0'):
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
        self.total_collisions = 0

class Particle:
    def __init__(self,shape,bn=[0,0,20,20],color='b',r=1):
        super().__init__()
        coords = shape
        self.bndry = []
        self.t_step = 0.01
        for c,f in enumerate(coords):
            
            try:
                cr = (coords[c],coords[c+1])
            except IndexError:
                cr = (coords[c],coords[-1])
##            
            self.bndry.append(cr)
        self.r=r
        for i in range(100): #Attempt to spawn ball within boundary
            self.p0 = [random.uniform(bn[0],bn[2]),random.uniform(bn[1],bn[3])]
            break
        if i>85:
            print('Warning, ball took:',i,'attempts to spawn')
        self.v0 = [random.uniform(-50,50),random.uniform(-30,30)]
        self.cor = 0.60
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
            if self.name==ball.name:
                continue
            #ball is Messenger class object
            dif = np.subtract(self.p0,ball.p)
            dis = math.sqrt(dif[0]**2 + dif[1]**2)
            
            name = ball.name
            if dis <= self.r + ball.r:# self.circle.crosses(shape) or self.circle.touches(shape) or self.circle.intersects(shape):
                coldic = dict(name=ball.name,v0=self.v0,p0=self.p0,elapsed=self.messenger.elapsed)
                self.mycollisions.append(coldic)
                self.messenger.collision.append(coldic)
                self.ball_collision(ball,ball.p,ball.v)
                self.ball_shift(ball,ball.p,ball.v)
                coldic['p0'] = self.p0
        
        for ball in self.ball_list: #Detects collision with other objects
            #Reacts to intersection between this object and another
            for c,line in enumerate(ball.collision): #Undetected Collisions received as a message
                if self.name == line['name'] and line not in self.mycollisions:
                    p0,v0 = line['p0'],line['v0']
                    dif = np.subtract(self.p0,p0)
                    dis = math.sqrt(dif[0]**2 + dif[1]**2)
##                    print('Collision%', self.name,dis)
                    self.ball_collision(ball,p0,v0)
                    if dis <= self.r + ball.r:
                        self.ball_shift(ball,p0,v0)
                    del ball.collision[c]
                for d, col in enumerate(self.mycollisions):
                    if line == col and col!= []:
                        del self.mycollisions[d]
                        del ball.collision[c]
        
                
        #Gravity calculations for timestep
        self.p0[1] = 0.5*self.a[1]*t**2+self.v0[1]*t+self.p0[1]
        self.p0[0] = 0.5*self.a[0]*t**2+self.v0[0]*t+self.p0[0]
        self.v0[1] = self.a[1]*t + self.v0[1]
        self.v0[0] = self.a[0]*t + self.v0[0]
        
        
        
                
        
        for (c1,c2) in self.bndry: #Detects collision with boundary
            dif = np.subtract(self.p0,c1)
            dis = math.sqrt(dif[0]**2 + dif[1]**2)
            clen = np.subtract(c1,c2)
            clen = math.sqrt(clen[0]**2 + clen[1]**2)
            angle = math.atan2(self.p0[1]-c1[1], self.p0[0]-c1[0]) - math.atan2(c2[1]-c1[1], c2[0]-c1[0])
            wall_distance = math.sin(angle)*dis
            closest_dis = math.cos(angle)*dis
            
            #Wall detection: https://stackoverflow.com/questions/1073336/circle-line-segment-collision-detection-algorithm
            if abs(wall_distance) <= self.r and 0<closest_dis <clen:
##                print('Wall Collision',(c1,c2))
    
                self.ke = 0.5*self.m*((self.v0[0]**2+self.v0[1]**2)**0.5)**2
##                print(self.name,'wall collision. Kinetic Energy: ',self.ke)
                self.wall_collision(c1,c2,wall_distance)
##                if self.ke != 0.5*self.m*((self.v0[0]**2+self.v0[1]**2)**0.5)**2:
##                    print("ENERGY CHANGED!!!",self.ke - 0.5*self.m*((self.v0[0]**2+self.v0[1]**2)**0.5)**2)
        self.messenger.v = self.v0
        self.messenger.p = self.p0
        self.ke = 0.5*self.m*((self.v0[0]**2+self.v0[1]**2)**0.5)**2
        self.messenger.ke = self.ke
        return self.messenger

    def wall_collision(self,c1,c2,d):
        angle3 = np.arctan2(c2[1] - c1[1], c2[0] - c1[0])+np.pi/2
        self.p0 = [self.p0[0]-(self.r+d)*np.cos(angle3), self.p0[1]-(self.r+d)*np.sin(angle3)]
        angle2 = np.arctan2(self.v0[1], self.v0[0])
        v = (self.v0[0]**2+self.v0[1]**2)**0.5
        theta = (angle2-angle3)
        vbi, vbj = v*np.sin(theta), v*np.cos(theta)
        vbj = -vbj *self.cor
        v = (vbi**2+vbj**2)**0.5
        angle4 = np.arctan2(vbj, vbi)
        angle1 = angle4-angle3
        self.collisions+=1
        self.v0 = [np.sin(angle1)*v, np.cos(angle1)*v]
        self.messenger.total_collisions += 1
        
    def ball_shift(self,ball,p,v):
        angle = np.arctan2(p[1] - self.p0[1], p[0] - self.p0[0])
        pnp = np.array(p)
        dif = np.subtract(self.p0,p)
        d = math.sqrt(dif[0]**2 + dif[1]**2)
        self.p0 = [self.p0[0]-(self.r+ball.r-d)*np.cos(angle),self.p0[1]-(self.r+ball.r-d)*np.sin(angle)]
        
    def ball_collision(self,messenger,p0,v0):
##        print('A ball collision',self.name,messenger.name)
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
