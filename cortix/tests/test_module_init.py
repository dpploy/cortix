from cortix.src.module import Module
from cortix.src.port import Port
from cortix.src.port import PortType
from util.dummy_module import DummyModule

def test_module_init():
    # Initialize the module
    m = DummyModule()

    # Construct ports
    p1 = Port("test-use", PortType.USE)
    p2 = Port("test-provide", PortType.PROVIDE)

    # Add ports to the module
    m.add_port(p1)
    m.add_port(p2)

    # Output the list of ports
    print(m.ports)
    assert(len(m.ports) == 2)

if __name__ == "__main__":
    test_module_init()
