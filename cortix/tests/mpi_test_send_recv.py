from cortix.src.module import Module
from cortix.src.port import Port

from cortix.examples.dummy_module import DummyModule
from cortix.examples.dummy_module import DummyModule2

from cortix.src.cortix_main import Cortix

def mpi_send_recv():

    # Create and connect P1 to P2
    p1 = Port("test-port1")
    p2 = Port("test-port2")
    p1.connect(p2)

    m1 = DummyModule()
    m1.add_port(p1)

    m2 = DummyModule2()
    m2.add_port(p2)

    c = Cortix()
    c.add_module(m1)
    c.add_module(m2)
    c.run()


if __name__ == "__main__":
    mpi_send_recv()
