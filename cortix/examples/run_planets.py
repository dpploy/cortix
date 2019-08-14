#!/usr/bin/env python
from cortix import Cortix
from cortix.src.module import Module
from cortix.src.port import Port
from body import Body

def main():
    um = False
    num_bodies = 10

    cortix = Cortix(use_mpi=um)
    for i in range(num_bodies):
        cortix.add_module(Body())

    for x, i in enumerate(cortix.modules):
        for y, j in enumerate(cortix.modules):
            pi = Port("body_{}".format(y), um)

            if x != y and pi not in i.ports:
                i.ports.append(pi)

                pj = Port("body_{}".format(x), um)
                j.ports.append(pj)

                pj.connect(pi)

    for mod in cortix.modules:
        print(mod.ports)
    #cortix.run()

if __name__ == "__main__":
    main()
