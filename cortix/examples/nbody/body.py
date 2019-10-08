from cortix import Module
from cortix import Port
import numpy as np

class Body(Module):
    def __init__(self, mass=1, rad=(0, 0, 0), vel=(0, 0, 0), time=100, dt=0.01):
        super().__init__()

        self.G = 6.67408e-11
        self.ep = 1e-20

        self.mass = mass
        self.rad = rad

        self.vel = vel
        self.acc = np.zeros(3)

        self.other_bodies = None
        self.dt = dt
        self.time = time

        self.trajectory = []


    def force_from(self, other_mass, other_rad):
        delta = np.linalg.norm(other_rad - self.rad)
        if delta == 0:
            print("Collision!")
            exit(1)
        return (self.G * self.mass * other_mass) / (delta ** 2)

    def step(self):
        self.acc = np.zeros(3)
        total_force = np.zeros(3)

        for (body_mass, body_rad) in self.other_bodies:
            total_force += self.force_from(body_mass, body_rad)

        acc = total_force / self.mass
        self.acc = self.acc + acc
        self.vel = self.vel + acc * self.dt
        self.rad = self.rad + self.vel * self.dt

    def broadcast_data(self):
        # Broadcast (mass, pos) to every body
        for port in self.ports:
            self.send((self.mass, self.rad), port)

    def gather_data(self):
        # Get (mass, pos) from every other body
        self.other_bodies = [self.recv(port) for port in self.ports]

    def run(self):
        t = 0.0
        while t < self.time:
            self.broadcast_data()
            self.gather_data()
            self.step()
            self.trajectory.append(tuple(self.rad.flatten()))
            t += self.dt
            print(t)
        self.dump()

    def dump(self, file_name=None):
        if file_name is None:
            file_name = "body_{}.csv".format(id(self))
        with open(file_name, "w") as f:
            for (x, y, z) in self.trajectory:
                f.write("{}, {}, {}\n".format(x, y, z))

    def __repr__(self):
        return "{}".format([self.mass, self.rad, self.vel, self.acc])
