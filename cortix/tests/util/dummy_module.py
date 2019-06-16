from cortix.src.module import Module
from cortix.src.port import Port
from time import sleep

class DummyModule(Module):
    def __init__(self):

        # Call the Module class constructor
        super().__init__()

    def run(self):
        # Simulate sending data every second
        i = 0
        while i < 10:
            sleep(5)
            self.send("test-port1", i)
            print("Sent {}!".format(i))
            i += 1

        print("Finished Sending!")

class DummyModule2(Module):
    def __init__(self):

        # Call the Module class constructor
        super().__init__()

    def run(self):
        # Simulate receiving data every two seconds 
        i = 0
        while i < 10:
            sleep(1)

            # Receive data from all connected ports
            print("Receiving {}!".format(i))
            data = self.recv("test-port2")

            # Extract the data only from test-port1

            port1_data = data["test-port1"]
            print("Received {}!".format(port1_data))

            assert(port1_data == i)
            i += 1

        print("Finished Receiving!")
