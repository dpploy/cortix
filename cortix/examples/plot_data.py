from cortix.src.module import Module
from cortix.src.port import Port
from cortix.util.dataplot import DataPlot
from cortix.src.cortix_main import Cortix

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
    d.set_title("Test Plot")
    d.set_xlabel("Time")
    d.set_ylabel("Position")

    # Custom class to send dummy data
    p = PlotData()

    p1 = Port("plot-in")
    p2 = Port("plot-out")
    p1.connect(p2)

    d.add_port(p1)
    p.add_port(p2)

    c = Cortix()
    c.add_module(d)
    c.add_module(p)
    c.use_mpi = False
    c.run()
