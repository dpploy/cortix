from cortix.src.module import Module
from cortix.src.port import Port
from cortix.util.dataplot import DataPlot
from cortix.src.cortix_main import Cortix

from cortix.examples.droplet import Droplet
from cortix.examples.vortex import Vortex

if __name__ == "__main__":

    dp1 = DataPlot()
    dp1.set_title('Radial Position')
    dp1.set_xlabel('Time')
    dp1.set_ylabel('Radius')

    dp2 = DataPlot()
    dp2.set_title('Speed')
    dp2.set_xlabel('Time')
    dp2.set_ylabel('Speed')

    d = Droplet()

    p1 = Port('radius')
    p2 = Port('radius')
    p1.connect(p2)

    v = Vortex()

    p3 = Port('velocity')
    p4 = Port('velocity-request')

    p5 = Port('velocity')
    p6 = Port('droplet-request')

    p6.connect(p4)
    p5.connect(p3)

    p7 = Port('speed')
    p8 = Port('speed')

    p7.connect(p8)

    d.add_port(p3)
    d.add_port(p4)

    v.add_port(p5)
    v.add_port(p6)

    dp1.add_port(p1)
    dp2.add_port(p7)

    d.add_port(p2)
    d.add_port(p8)

    # Custom class to send dummy data
    c = Cortix()
    c.add_module(dp1)
    c.add_module(dp2)
    c.add_module(d)
    c.add_module(v)
    c.run()
