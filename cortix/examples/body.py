from cortix.src.module import Module
from cortix.src.port import Port

import numpy as np

class Body(Module):
    def __init__(self, mass=0, rad=0, pos=np.array([0.0, 0.0, 0.0]),
            vel=np.array([0.0,0.0,0.0]), ts=10):
        super().__init__()

        self.G = 6.67408e-11
        self.mass = mass
        self.rad = rad
        self.pos = pos
        self.vel = vel
        self.acc = None
        self.other_bodies = None
        self.time_steps = ts

    def acceleration(self):
        self.acc = np.array([0.0, 0.0, 0.0])
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
            print(self)
            self.broadcast_data()
            self.gather_data()
            print("Time step: {}".format(t))
            print(self.other_bodies)

    def __repr__(self):
        return "{}".format([self.mass, self.rad, self.vel, self.acc])
