from cortix.src.module import Module

from cortix.src.port import Port
from cortix.src.port import PortType


class MyModule(Module):
    def __init__(self):
        print("Hello from MyModule constructor")

if __name__ == "__main__":

    # Initialize the module
    m = MyModule()

    # Add ports via parameters
    m.add_port("test-use", PortType.USE)
    m.add_port("test-provide", PortType.PROVIDE)

    # Output the list of ports
    print(m.ports)
