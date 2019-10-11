#!/usr/bin/env python

from cortix.tests.dummy_module import DummyModule

def test_module_init():
    # Initialize the module
    m = DummyModule()

    # get ports
    p1 = m.get_port('test-1')
    p2 = m.get_port('test-2')

    # Output the list of ports
    print(m.ports)
    assert(len(m.ports) == 2)

if __name__ == "__main__":
    test_module_init()
