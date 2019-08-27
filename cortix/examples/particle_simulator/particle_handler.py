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
from cortix.examples import Particle

class Particle_Handler(Module):

    def __init__(self,shape=None, balls= 5, runtime=3,color='b'):
        super().__init__()
        self.color = color
        self.shape = shape
        self.balls = balls
        self.runtime = runtime
        self.local_balls = []
        self.local_messengers = []
        self.collisions = 0
        self.r = 1
        self.t_step = 0.01
        self.timestamp=str(datetime.datetime.now())
        self.elapsed, self.oe = 0,0
        self.name = ''.join([random.choice(string.ascii_lowercase+string.digits) for f in range(10)])
        
    def run(self):
        t = self.t_step
        for i in range(self.balls):
            ball = Particle(shape=self.shape,color=self.color,r=self.r)
            ball.t_step = self.t_step
            self.local_balls.append(ball)
            self.local_messengers.append(ball.messenger)
        
        its = round(self.runtime/self.t_step)

        ball_list = []
        
        for messenger in self.local_messengers:
            ball_list.append(messenger)
        for i in self.ports: #Send initial properties
            if 'plot' not in str(i):
                self.send(self.local_messengers,i)
        
        for i in self.ports:
            if 'plot' not in str(i):
                ex_balls = self.recv(i)
                for ball in ex_balls:
                    ball_list.append(ball)
        
        for i in range(its):
            self.elapsed += t
            for c,ball in enumerate(self.local_balls):
                messenger = ball.run(ball_list)
                self.local_messengers[c] = messenger
            for i in self.ports: #Send and receive messages for each timestep
                self.send(self.local_messengers,i)
                if 'plot' in str(i):
                    check = self.recv(i)
            ball_list = [f for f in self.local_messengers]   
            for i in self.ports:
                if 'plot' in str(i): #Not receiving messages from plotting
                    continue
                messengerlis = self.recv(i)
                for messenger in messengerlis:
                    ball_list.append(messenger)
                

        for i in self.ports: #Send 'done' string to plot module as end condition
            if 'plot' in str(i):
                self.send('Done',i)
        print('Done')
        return
