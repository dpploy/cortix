from cortix import Module
from cortix import Port
from time import sleep

class DummyModule(Module):
    def __init__(self):

        # Call the Module class constructor
        super().__init__()

    def run(self):
        # Simulate sending data every second
        i = 0
        while i < 10:
            sleep(1)
            self.send(i, "test-port1")
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
            print("Received {}!".format(data))

            assert(data == i)
            i += 1

        print("Finished Receiving!")
