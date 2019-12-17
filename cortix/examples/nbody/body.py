from cortix import Module
from cortix import Port
import numpy as np

class Body(Module):
    def __init__(self, mass, pos, vel, time, dt, name=None):
        super().__init__()

        self.name = name if name else "body_{}.csv".format(id(self))
        self.mass = mass
        self.vel = vel
        self.pos = pos

        self.ep = 1e-20

        self.other_bodies = None
        self.dt = dt
        self.time = time

        self.trajectory = []

    def force(self, mass, pos):
        G = 6.67408e-11
        delta = [i - j for i, j in zip(self.pos, pos)]

        r = np.sqrt(delta[0] ** 2 + delta[1] ** 2 + delta[2]**2)
        sin_theta = [d/r for d in delta]
        force = (G * self.mass * mass) / r**2

        res = [force * s for s in sin_theta]

        return res

    def total_force(self):
        total_force = 0
        for (mass, pos) in self.other_bodies:
            total_force += self.force(mass, pos)
        return total_force

    def step(self):
        accel = self.total_force() / self.mass
        self.vel = self.vel + accel * self.dt
        self.pos = self.vel * self.dt

    def broadcast_data(self):
        # Broadcast (mass, pos) to every body
        print((self.mass, self.pos))
        for port in self.ports:
            self.send((self.mass, self.pos), port)

    def gather_data(self):
        # Get (mass, pos) from every other body
        self.other_bodies = [self.recv(port) for port in self.ports]

    def run(self):
        t = 0.0
        while t < self.time:
            self.broadcast_data()
            self.gather_data()
            self.step()
            self.trajectory.append(self.pos)
            t += self.dt
        self.dump()

    def dump(self, file_name=None):
        file_name = file_name if file_name else self.name + ".csv"
        with open(file_name, "w") as f:
            for (x, y, z) in self.trajectory:
                f.write("{}, {}, {}\n".format(x, y, z))

    def __repr__(self):
        return "{}".format([self.mass, self.pos, self.vel])
