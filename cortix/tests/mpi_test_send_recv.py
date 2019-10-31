from cortix.src.cortix_main import Cortix
from cortix.src.network import Network

from cortix.tests.dummy_module import DummyModule
from cortix.tests.dummy_module import DummyModule2

def mpi_send_recv():

    c = Cortix()

    c.network = Network()

    m1 = DummyModule()
    c.network.add_module(m1)
    p1 = m1.get_port('test-port1')

    m2 = DummyModule2()
    c.network.add_module(m2)
    p2 = m2.get_port('test-port2')

    c.network.connect([m1,p1],[m2,p2],'bidirectional')

    c.run()

if __name__ == "__main__":
    mpi_send_recv()
