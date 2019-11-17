from cortix import Module
from cortix import Port
import numpy as np


class Body(Module):
    def __init__(self, mass, rad, pos, vel, time, dt):
        super().__init__()

        self.mass = mass
        self.vel = vel
        self.pos = pos
        self.rad = rad

        self.G = 6.67408e-11
        self.ep = 1e-20

        self.mass = mass
        self.rad = rad

        self.vel = vel
        self.acc = [0, 0, 0]

        self.other_bodies = None
        self.dt = dt
        self.time = time

        self.trajectory = []

    def force_from(self, other_mass, other_rad):
        rad = np.linalg.norm(other_rad - self.rad)
        if rad == 0:
            print("Collision!")
            exit(1)
        return (self.G * self.mass * other_mass) / (rad ** 2)

    def step(self):
        self.acc = np.zeros(3)
        total_force = np.zeros(3)

        for (body_mass, body_rad) in self.other_bodies:
            x = self.force_from(body_mass, body_rad)
            print("Printing now!")
            print(total_force)
            total_force += x
            print(total_force)


        self.acc = total_force / self.mass
        self.vel = self.vel + self.acc * self.dt
        print(self.vel)

        

        print(type(self.vel[0] * self.dt))
        print(self.rad[0])
        print(type(self.rad[0]))
        self.rad[0] += self.vel[0] * self.dt
        self.rad[1] -= self.vel[1] * self.dt

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
        self.dump()

    def dump(self, file_name=None):
        if file_name is None:
            file_name = "body_{}.csv".format(id(self))
        with open(file_name, "w") as f:
            for (x, y, z) in self.trajectory:
                f.write("{}, {}\n".format(x, y))

    def __repr__(self):
        return "{}".format([self.mass, self.rad, self.vel, self.acc])
