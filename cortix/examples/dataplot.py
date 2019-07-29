import sys
import logging
from threading import Thread
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
matplotlib.use('Agg', warn=False)
import matplotlib.pyplot as plt
from cortix.src.module import Module

class DataPlot(Module):


    def __init__(self):

        super().__init__()

        self.same_axes = False
        self.dpi = 200

        self.xlabel = 'x'
        self.ylabel = 'y'
        self.zlabel = 'z'
        self.title = None

        self.log = logging.getLogger('cortix')
        self.debug = False
        self.print_freq = 10

        self.data = dict()

    def run(self):
        # Spawn a thread to handle each module
        threads = []
        for port in self.ports:
            thread = Thread(target=self.recv_data, args=(port,))
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

        self.new_plot_data()

    def recv_data(self, port):
        data = []
        i = 1
        while True:
            d = self.recv(port)
            if self.debug and i % self.print_freq == 0:
                self.log.info('DataPlot::'+port.name+' received: {}'.format(d))
            if isinstance(d, str) and d == "DONE":
                #self.plot_data(data, port)
                self.data[port.name] = data
                sys.exit(0)
            i += 1

            data.append(d)

    def plot_data(self, data, port):
        x = [i[0] for i in data]
        y = [i[1] for i in data]

        # 2D-Plot
        if data and len(data[0]) == 2:
            fig = plt.figure(port.name)
            plt.xlabel(self.xlabel)
            plt.ylabel(self.ylabel)
            plt.title(self.title)
            plt.plot(x, y)

        # 3D-Plot
        elif data and len(data[0]) == 3:
            fig = plt.figure(port.name)
            ax = fig.add_subplot(111, projection='3d')
            ax.set_xlabel(self.xlabel)
            ax.set_ylabel(self.ylabel)
            ax.set_zlabel(self.zlabel)
            ax.set_title(self.title)
            ax.plot(x, y, [i[2] for i in data])

        plt.savefig('{}.png'.format(port.name), dpi=self.dpi)

    def new_plot_data(self):

        if self.same_axes:
            fig = plt.figure(1)
            ax = None

        for (key,data) in self.data.items():

            x = [i[0] for i in data]
            y = [i[1] for i in data]

        # 2D-Plot
            if data and len(data[0]) == 2:
                if not self.same_axes:
                    fig = plt.figure(key)
                plt.xlabel(self.xlabel)
                plt.ylabel(self.ylabel)
                plt.title(self.title)
                plt.plot(x, y)

        # 3D-Plot
            elif data and len(data[0]) == 3:

                if self.same_axes and ax is None:
                    ax = fig.add_subplot(111, projection='3d')
                    ax.set_xlabel(self.xlabel)
                    ax.set_ylabel(self.ylabel)
                    ax.set_zlabel(self.zlabel)
                    ax.set_title(self.title)

                if not self.same_axes:
                    fig = plt.figure(key)
                    ax = fig.add_subplot(111, projection='3d')
                    ax.set_xlabel(self.xlabel)
                    ax.set_ylabel(self.ylabel)
                    ax.set_zlabel(self.zlabel)
                    ax.set_title(self.title)

                ax.plot(x, y, [i[2] for i in data])

                if not self.same_axes:
                    plt.savefig('{}.png'.format(key), dpi=self.dpi)

        if self.same_axes:
            plt.savefig('{}.png'.format(key.split(':')[0]), dpi=self.dpi)
