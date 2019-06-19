import sys
import logging
from threading import Thread
import matplotlib
matplotlib.use('Agg', warn=False)
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from cortix.src.module import Module

class DataPlot(Module):
    def __init__(self):
        super().__init__()

        self.xlabel = None
        self.ylabel = None
        self.title = None

        self.log = logging.getLogger("cortix")

    def run(self):
        # Spawn a thread to handle each module
        threads = []
        for port in self.ports:
            thread = Thread(target=self.recv_data, args=(port,))
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

    def recv_data(self, port):
        data = []
        print_every = 100
        i = 1
        while True:
            d = self.recv(port)
            if i % print_every == 0:
                self.log.info("Received: {}".format(d))
            if d == "DONE":
                self.plot_data(data, port)
                sys.exit(0)
            i += 1

            data.append(d)

    def plot_data(self, data, port):
        '''
        Make plot.

        Parameters
        ----------
        data: list(tuple)
        '''

        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.title)

        x = [i[0] for i in data]
        y = [i[1] for i in data]

        if x and len(data[0]) == 2:
            plt.plot(x, y)
        elif x and len(data[0]) == 3:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.plot(x, y, [i[2] for i in data])

        plt.savefig("{}.png".format(port.name), dpi=200)

    def set_xlabel(self, xlabel):
        self.xlabel = xlabel

    def set_ylabel(self, ylabel):
        self.ylabel = ylabel

    def set_title(self, title):
        self.title = title
