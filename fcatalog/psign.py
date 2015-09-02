# Profiling code for the sign function.

import random
from catalog1 import sign,strong_hash

def rand_bytes(n):
    """
    Get n random bytes.
    """
    return bytes(random.getrandbits(8) for i in range(n))

def go():
    # Pick an initial seed, for determinisim.
    random.seed(a='A seed for determinism of this test.')

    num_funcs = 0xf0
    func_size = 0xf0
    func_name_len = 0x20


    for i in range(num_funcs):
        # Generate function data:
        func_data = rand_bytes(func_size)
        # Calculate signature:
        s = sign(func_data,16)

    print('done!')


if __name__ == '__main__':
    go()
