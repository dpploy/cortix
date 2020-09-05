#simple script to test the condenser
from params import get_params
from condenser import Condenser

input = get_params()
input['start-time'] = 0
input['end-time'] = 0

condenser = Condenser(input)
condenser.tester()

