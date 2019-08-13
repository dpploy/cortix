#!/usr/bin/env python
from cortix import Cortix
from cortix.src.module import Module
from cortix.src.port import Port
from body import Body

def main():
    cortix = Cortix(use_mpi=False)

    num_bodies = 5

    for i in range(num_bodies):
        cortix.add_module(Body())

    for i in cortix.modules:
        for j in cortix.modules:
            if i !=j:
                pi = Port("body_{}".format(cortix.modules.index(i)))
                i.ports.append(pi)

                pj = Port("body_{}".format(cortix.modules.index(j)))
                j.ports.append(pj)

                pj.connect(pi)

    cortix.run()

if __name__ == "__main__":
    main()
