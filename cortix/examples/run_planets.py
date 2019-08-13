#!/usr/bin/env python
from cortix import Cortix
from cortix.src.module import Module
from cortix.src.port import Port
from body import Body

def main():
    um = False
    num_bodies = 10

    for loop in range(int(10e6)):
        print("STARTING {}".format(loop))
        cortix = Cortix(use_mpi=um)
        for i in range(num_bodies):
            cortix.add_module(Body())

        for x, i in enumerate(cortix.modules):
            for y, j in enumerate(cortix.modules):
                if x != y:
                    pi = Port("body_{}".format(y), um)
                    i.ports.append(pi)

                    pj = Port("body_{}".format(x), um)
                    j.ports.append(pj)

                    pj.connect(pi)

        cortix.run()
        for mod in cortix.modules:
            for port in mod.ports:
                port.q.close()

        del cortix

if __name__ == "__main__":
    main()
