#!/usr/bin/env python
from cortix import Cortix
from cortix import Module
from cortix import Network
from cortix import Port
from body import Body

def main():
    um = False
    num_bodies = 10

    cortix = Cortix(use_mpi=um)
    cortix.network = Network()
    for i in range(num_bodies):
        b = Body()
        b.save = True
        cortix.network.module(b)

    for x, i in enumerate(cortix.network.modules):
        for y, j in enumerate(cortix.network.modules):
            pi = Port("body_{}".format(y), um)

            if x != y and pi not in i.ports:
                i.ports.append(pi)

                pj = Port("body_{}".format(x), um)
                j.ports.append(pj)

                pj.connect(pi)

    cortix.run()

if __name__ == "__main__":
    main()
