#!/usr/bin/env python

from cortix.src.cortix_main import Cortix
from cortix.src.module import Module
from cortix.src.network import Network

from cortix.tests.dummy_module import DummyModule

def test_cortix_add_module():
    # Init the Cortix object
    c = Cortix()
    c.network = Network()

    num_modules = 100
    module_list = list()

    # Add 100 modules to the Cortix object
    for i in range(num_modules):
        # Initialize the module
        m = DummyModule()
        c.network.add_module(m)

        # Get ports
        p1 = m.get_port('test1-{}'.format(i))
        p2 = m.get_port('test2-{}'.format(i))

    # Make sure we have the correct modules
    assert len(c.network.modules) == num_modules
    for mod in c.network.modules:
        assert isinstance(mod, Module)
        assert len(mod.ports) == 2

if __name__ == "__main__":
    test_cortix_add_module()
