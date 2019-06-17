from cortix.src.module import Module
from cortix.src.port import Port
from cortix.util.dataplot import DataPlot
from cortix.src.cortix_main import Cortix

from cortix.examples.droplet import Droplet
from cortix.examples.vortex import Vortex

if __name__ == "__main__":
    c = Cortix(use_mpi=True)
    v = Vortex()

    for i in range(5):
        droplet = Droplet()
        data_plot = DataPlot()

        data_plot.set_title('Radial Position')
        data_plot.set_xlabel('Time')
        data_plot.set_ylabel('Radius')


        # Initialize ports
        drop_port = Port("radius")
        plot_port = Port("radius-{}".format(i))
        droplet_req_port = Port("droplet-request-{}".format(i))
        velocity_port = Port("velocity-{}".format(i))
        vortex_req_port = Port("velocity-request")
        vortex_velocity_port = Port("velocity")


        # Connect ports
        drop_port.connect(plot_port)
        droplet_req_port.connect(vortex_req_port)
        velocity_port.connect(vortex_velocity_port)

        # Add ports to module
        data_plot.add_port(plot_port)
        droplet.add_port(drop_port)
        droplet.add_port(vortex_req_port)
        droplet.add_port(vortex_velocity_port)
        v.add_port(droplet_req_port)
        v.add_port(velocity_port)

        # Add modules to Cortix
        c.add_module(droplet)
        c.add_module(data_plot)

    c.add_module(v)
    c.run()