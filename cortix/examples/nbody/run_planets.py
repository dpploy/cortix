#!/usr/bin/env python
from cortix import Cortix
from cortix import Module
from cortix import Network
from cortix import Port
from cortix.examples import Body
from cortix.examples import Body_Plot

def main():
    um = False
    num_bodies = 10

    cortix = Cortix(use_mpi=um)
    cortix.network = Network()
    modlist = []
    for i in range(num_bodies):
        b = Body()
        b.save = True
        cortix.network.module(b)
        modlist.append(b)
    plot = Body_Plot(num_bodies)
    cortix.network.module(plot)
    
    for x, i in enumerate(modlist):
        cortix.network.connect([i,'plot_send_{}'.format(x)],[plot,'plot_recv_{}'.format(x)])
        for y, j in enumerate(modlist):
            pi = Port("body_{}".format(y), um)

            if x != y and pi not in i.ports:
                i.ports.append(pi)

                pj = Port("body2_{}".format(x), um)
                j.ports.append(pj)

                pj.connect(pi)

    cortix.run()

if __name__ == "__main__":
    main()
