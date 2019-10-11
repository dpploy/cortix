#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
from cortix import Module
from cortix import Port
from cortix import Network
from cortix import Cortix

from cortix.tests.dataplot import DataPlot

class PlotData(Module):
    def __init__(self):
        super().__init__()

    def run(self):
        i = 0
        while i < 10:
            data = (i, i**2)
            self.send(data, "plot-out")
            print("Sent {}!".format(data))
            i += 1
        self.send("DONE", "plot-out")
        print("Finished sending!")

if __name__ == "__main__":

    # Cortix built-in DataPlot module
    d = DataPlot()
    #d.set_title("Test Plot")
    #d.set_xlabel("Time")
    #d.set_ylabel("Position")

    d.title = 'Test Plot'
    d.xlabel = 'Time'
    d.ylabel = 'Position'

    # Custom class to send dummy data
    p = PlotData()

    p1 = Port("plot-in")
    p2 = Port("plot-out")
    p1.connect(p2)

    d.ports.append(p1)
    p.ports.append(p2)

    c = Cortix()
    c.network = Network()
    c.network.add_module(d)
    c.network.add_module(p)
    c.use_mpi = False
    c.run()
