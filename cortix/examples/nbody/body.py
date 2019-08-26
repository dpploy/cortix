from cortix import Module
from cortix import Port
import numpy as np
from numpy.random import rand

class Body(Module):
    def __init__(self, mass=1, rad=1, pos=None, vel=None, ts=10):
        super().__init__()

        self.G = 6.67408e-11
        self.mass = mass
        self.rad = rad

        self.pos = pos if pos else np.array([i*5 for i in rand(3)])
        self.vel = vel if vel else np.array([i*10 for i in rand(3)])
        self.acc = np.zeros(3)
        self.other_bodies = None
        self.time_steps = ts

    def acceleration(self):
        ep = 1e-7
        self.acc = np.array([0.0, 0.0, 0.0])
        for (mass, pos) in self.other_bodies:
            r = np.linalg.norm(self.pos - pos)
            coef = self.G * self.mass / r**3
            self.acc += (coef * (pos - self.pos)) + ep
        return self.acc

    def position(self):
        self.pos += (self.vel + (self.acc / 2))
        return self.pos

    def velocity(self):
        self.vel += self.acc
        return self.vel

    def step(self):

        self.acceleration()
        self.position()
        self.velocity()

    def broadcast_data(self):
        # Broadcast (mass, pos) to every body
        for port in self.ports:
            payload = np.array([self.mass, self.pos])
            self.send((self.mass, self.pos), port)

    def gather_data(self):
        self.other_bodies = [self.recv(port) for port in self.ports]

    def run(self):
        self.broadcast_data()

        self.mass = 42
        self.pos = 32
        self.rad = 52

        # Receive (mass, pos) from every body 
        self.gather_data()

        for t in range(self.time_steps):
            self.step()
            self.broadcast_data()
            self.gather_data()

        print(self)

    def __repr__(self):
        return "{}".format([self.mass, self.rad, self.vel, self.acc])
