from cortix.src.module import Module

from cortix.examples.dummy_module import DummyModule
from cortix.examples.dummy_module import DummyModule2

from cortix.src.cortix_main import Cortix

def mpi_send_recv():

    c = Cortix()

    m1 = DummyModule()
    c.add_module(m1)
    p1 = m1.get_port('test-port1')

    m2 = DummyModule2()
    c.add_module(m2)
    p2 = m2.get_port('test-port2')

    p1.connect(p2)

    c.run()

if __name__ == "__main__":
    mpi_send_recv()
