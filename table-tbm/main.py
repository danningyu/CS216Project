from tbm_generator import generate
from network_util import get_prefixes

from random import randint
import sys

def gen_random_testcase(prefix: str):
    """
    Generates a random 32-bit IP address (given in hex) given a prefix
    """
    for i in range(32-len(prefix)):
        prefix += str(randint(0, 1))
    val = hex(int(prefix, 2))[2:]
    # separate by spaces for copying into P4 simulator
    return val[:2] + " " + val[2:4] + " " + val[4:6] + " " + val[6:]

# next_hop_map = {
#     "0000101000000000000000010000": (0x080000000110, 1), # 10.0.1.1/28
#     "0000101000000000000000010001": (0x080000000120, 2), #10.0.1.17
#     "0000101000000000000000":  (0x080000000210, 3), #10.0.0.1
#     "00001010000000000000001": (0x080000000220, 4), #10.0.2.17
# }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('ERROR: usage: python3 main.py <num_prefixes>')
        exit(1)

    next_hop_map = get_prefixes("../bgptable.csv", int(sys.argv[1]))
    
    generate(next_hop_map, stride_length=5)

    # print(gen_random_testcase("11110100000000"))
