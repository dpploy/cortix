import random, string
from cortix import Module
from cortix import Port
import numpy as np
from numpy.random import rand

class Body(Module):
    def __init__(self, mass=1, rad=1, pos=None, vel=None, ts=100):
        super().__init__()
        
        self.G = 6.67408e-11
        self.mass = mass
        self.rad = rad
        self.name = ''.join([random.choice(string.ascii_lowercase+string.digits) for f in range(10)])
        self.pos = np.array([abs(i*500) for i in rand(3)])
        self.vel = vel if vel else np.array([i for i in rand(3)])
        self.acc = np.zeros(3)
        self.envelope = dict(pos=self.pos,vel=self.vel,mass=mass,rad=rad,name=self.name)
        self.other_bodies = None
        self.time_steps = ts

    def acceleration(self):
        ep = 1e-7
        self.acc = np.array([0.0, 0.0, 0.0])
        for body in self.other_bodies:
            r = np.linalg.norm(self.pos - body['pos'])
            coef = self.G * self.mass / r**3
            self.acc += (coef * (body['pos'] - self.pos)) + ep
        return self.acc

    def position(self):
        self.pos += (self.vel + (self.acc / 2))
        print(self.pos)
        return self.pos

    def velocity(self):
        self.vel += self.acc
        return self.vel

    def step(self):

        self.acceleration()
        self.envelope['vel'] = self.velocity()
        self.envelope['pos'] = self.position()

    def broadcast_data(self):
        # Broadcast (mass, pos) to every body
        for port in self.ports:
            payload = np.array([self.mass, self.pos,self.name])
            
            self.send(self.envelope, port)
            if 'plot' in str(port):
                _ = self.recv(port)
        return
    def gather_data(self):
        self.other_bodies = []
        for port in self.ports:            
            if 'plot' in str(port):                
                continue
            data = self.recv(port)
            self.other_bodies.append(data)
        
        return
    def run(self):
        self.broadcast_data()

        self.mass = 42
        self.pos = 32
        self.rad = 52

        # Receive (mass, pos) from every body 
        self.gather_data()

        for t in range(self.time_steps):
            print(t)
            self.step()
            self.broadcast_data()
            self.gather_data()
        print('Done')
        for port in self.ports:
            if 'plot' in str(port):
                self.send('Done',port)
        print(self)

    def __repr__(self):
        return "{}".format([self.mass, self.rad, self.vel, self.acc])
