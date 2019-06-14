from cortix.src.module import Module

class DummyModule(Module):
    def __init__(self):

        # Call the Module class constructor
        super().__init__()

    def run(self):
        # send data out of my port
        self.send("test-port1", 42)
        print("SENT 42!")

class DummyModule2(Module):
    def __init__(self):

        # Call the Module class constructor
        super().__init__()

    def run(self):
        # Recv data from test-port2 (should be 42) 
        data = self.recv("test-port2")
        assert(data["test-port1"] == 42)
