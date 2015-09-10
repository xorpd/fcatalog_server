# Profiling code for the sign function.

import os
import random
from ..catalog1 import sign,strong_hash
from ..funcs_db import FuncsDB

DB_PATH = '/tmp/my_test_db.db'
NUM_HASHES = 16

def rand_bytes(n):
    """
    Get n random bytes.
    """
    return bytes(random.getrandbits(8) for i in range(n))

def go():
    # Pick an initial seed, for determinisim.
    random.seed(a='A seed for determinism of this test.')

    # Delete a current db if existent:
    try:
        os.remove(DB_PATH)
    except FileNotFoundError:
        pass

    # Build db:
    print('Building db...')
    fdb = FuncsDB(DB_PATH,NUM_HASHES)

    num_funcs = 640
    func_size = 0x200
    func_name_len = 0x20


    print('Inserts...')
    # Add some functions:
    for i in range(num_funcs):
        # Generate function data:
        func_data = rand_bytes(func_size)
        # Calculate signature:
        # s = sign(func_data,16)
        # Add the function to the DB:
        fdb.add_function('name',func_data,'comment')

    fdb.commit_funcs()

    print('Queries...')
    # Perform some queries:
    for i in range(10):
        func_data = rand_bytes(func_size)
        fdb.get_similars(func_data,5)

    fdb.close()

    print('done!')


if __name__ == '__main__':
    go()
