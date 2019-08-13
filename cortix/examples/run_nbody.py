from cortix import Cortix
from cortix.src.module import Module
from cortix.src.port import Port
from body import Body

def main():
    cortix = Cortix(use_mpi=False)

    num_bodies = 10

    for i in range(num_bodies):
        cortix.add_module(Body())

    for i in cortix.modules:
        for j in cortix.modules:
            if i != j:
                i.connect(j)

    cortix.run()

if __name__ == "__main__":
    main()
