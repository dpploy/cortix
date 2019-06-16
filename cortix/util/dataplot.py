from cortix.src.module import Module

import os
import numpy as npy
from threading import Thread
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator

class DataPlot(Module):
    def __init__(self):
        super().__init__()

        # Time data: port -> data
        self.time_data = {}

    def run(self):
        # Spawn a thread to handle each module
        for port in self.ports:
            thread = Thread(target=self.plot_data, args=(port,))
            thread.start()

    def plot_data(self, port):
        while True:
            data = self.recv(port)
            print("Got data = {}".format(data))
