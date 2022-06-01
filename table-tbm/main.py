from tbm_generator import generate

from random import randint

def gen_random_testcase(prefix: str):
    """
    Generates a random 32-bit IP address (given in hex) given a prefix
    """
    for i in range(32-len(prefix)):
        prefix += str(randint(0, 1))
    val = hex(int(prefix, 2))[2:]
    # separate by spaces for copying into P4 simulator
    return val[:2] + " " + val[2:4] + " " + val[4:6] + " " + val[6:]


next_hop_map = {
    "101": 1,
    "111": 2,
    "11001": 3,
    "1": 4,
    "0": 5,
    "10001110": 6,
    "11110100000000": 7,
    "100": 8,
    "110": 9,
    "": 0,
    "1111001100100": 10
}

if __name__ == "__main__":
    generate(next_hop_map, stride_length=5)

    # print(gen_random_testcase("11110100000000"))
