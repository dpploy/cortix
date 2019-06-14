from cortix.src.module import Module
from cortix.src.port import PortType

class MyModule(Module):
    def __init__(self):
        print("Hello from MyModule constructor")

if __name__ == "__main__":
    m = MyModule()

    m.add_port("test-use", PortType.use)
    m.add_port("test-provide", PortType.provide)

    print(m.ports)
