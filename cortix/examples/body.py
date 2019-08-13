from cortix.src.module import Module
from cortix.src.port import Port

class Body(Module):
    def __init__(self, mass=0, rad=0, pos=(0, 0, 0), vel=(0,0,0)):
        super().__init__()

        self.mass = mass
        self.rad = rad
        self.pos = pos
        self.vel = vel
        self.acc = None

    def acceleration(self, body):
        G = 6.67408e-11
        r = sum([(self.pos[i] - body.pos[i])**2 for i in range(3)])
        r = math.sqrt(r)
        coef = G * body.mass / r**3
        return [coef * (bod.pos[i] - self.pos[i]) for i in range(3)]

    def run(self):
        print(self.ports)
        for port in self.ports:
            self.send(self.mass, port)
            self.send(self.pos, port)

        print("DONE WITH SENDING")

        for port in self.ports:
            other_mass = self.recv(port)
            print("other mass: ", other_mass)

        print("DONE!")

    def __repr__(self):
        return "{}".format([self.mass, self.rad, self.vel, self.acc])
