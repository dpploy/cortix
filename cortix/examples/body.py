from cortix.src.module import Module
from cortix.src.port import Port

import numpy as np



class Body(Module):
    def __init__(self, mass=0, rad=0, pos=np.array([0, 0, 0]), vel=np.array([0,0,0])):
        super().__init__()

        self.G = 6.67408e-11
        self.mass = mass
        self.rad = rad
        self.pos = pos
        self.vel = vel
        self.acc = None
        self.other_bodies = None

    def acceleration(self):
        self.acc = np.zeros(3)
        for (mass, pos) in self.other_bodies:
            r = np.linalg.norm(self.pos - pos)
            coef = self.G * mass / r**3
            self.acc += coef * (pos - self.pos)
        return self.acc

    def position(self):
        self.pos += (self.vel + (self.acc / 2))
        return self.pos

    def velocity(self):
        self.vel += self.acc
        return self.vel

    def update(self, time_step):
        pass

    def run(self):
        # Broadcast (mass, pos) to every body
        for port in self.ports:
            payload = np.array([self.mass, self.pos])
            self.send((self.mass, self.pos), port)

        # Receive (mass, pos) from every body 
        other_bodies = [self.recv(port) for port in self.ports]



    def __repr__(self):
        return "{}".format([self.mass, self.rad, self.vel, self.acc])
