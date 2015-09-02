import pytest
import sqlite3
import random
import string

from funcs_db import FuncsDB
from catalog1 import sign,strong_hash


# Num hashes used for testing purposes:
NUM_HASHES = 16


class DebugFuncsDB(FuncsDB):
    def count(self):
        """
        Count the amount of lines inside the funcs table.
        """
        c = self._conn.cursor()

        cmd_count = "SELECT COUNT(*) from funcs"
        c.execute(cmd_count)
        res = c.fetchone()[0]

        return res


@pytest.fixture(scope='function')
def fdb_mem(request):
    """
    Create a FuncsDB instance (A new database on disk).
    """
    # Build database in memory. Should be quicker.
    fdb = DebugFuncsDB(':memory:',NUM_HASHES)

    def fin():
        """Finalizer for fdb"""
        # Make sure to close fdb.
        fdb.close()

    request.addfinalizer(fin)
    return fdb


def test_funcs_db_basic(fdb_mem):
    """
    Create a new database using FuncsDB.
    """
    pass


def test_add_function(fdb_mem):
    """
    Try to add a 'reversed' new function into the database.
    """
    # No functions at the beginning:
    assert fdb_mem.count() == 0
    # Add one function:
    fdb_mem.add_function('func_name1',b'func_data1','func_comment1')
    assert fdb_mem.count() == 1
    # Add another function:
    fdb_mem.add_function('func_name2',b'func_data2','func_comment2')
    assert fdb_mem.count() == 2
    # Add a function with func_data that already exists. Should replace the
    # earlier func_data2 record (Instead of adding a new row).
    fdb_mem.add_function('func_name3',b'func_data2','func_comment3')
    assert fdb_mem.count() == 2


def test_get_similars_basic(fdb_mem):
    """
    Try to run get_similars and see if it doesn't crash.
    """
    res = fdb_mem.get_similars(b'adfasdfasdf',5)
    assert isinstance(res,list)

    # Add a function and request a function similar to that function. We expect
    # to get one result:
    fdb_mem.add_function('func_name',b'func_data','func_comment')
    res = fdb_mem.get_similars(b'func_data',num_similars=3)
    assert len(res) == 1

    # Add another function, and request functions similar to that function. We
    # expect to get all the functions, where func2 will be first on the list:
    fdb_mem.add_function('func_name2',b'func_data2','func_comment2')
    res = fdb_mem.get_similars(b'func_data2',num_similars=3)
    assert len(res) == 2

    # Hash should match:
    assert res[0].func_hash == strong_hash(b'func_data2')
    assert res[1].func_hash != strong_hash(b'func_data2')

    # Signature should match:
    assert res[0].func_sig == sign(b'func_data2',NUM_HASHES)

    # Request for just one similars, and make sure we get only one, although
    # the DB contains two functions:
    res = fdb_mem.get_similars(b'func_data',num_similars=1)
    assert len(res) == 1


def test_random_seed(fdb_mem):
    """
    We expect consistency when using python's random with seed.
    """
    random.seed(a='this is the seed')
    res = random.randint(0,0xffffffff)
    random.seed(a='this is the seed')
    assert res == random.randint(0,0xffffffff)


def rand_bytes(n):
    """
    Get n random bytes.
    """
    return bytes(random.getrandbits(8) for i in range(n))

def rand_ascii_lowercase(n):
    """
    Get n random lowercase ascii characters. Returns a string of size n.
    """
    return ''.join(random.choice(string.ascii_lowercase) \
            for _ in range(n))



def test_get_similars(fdb_mem):
    """
    Test the operation of get_similars with many functions inside the DB.
    """
    # Pick an initial seed, for determinisim.
    random.seed(a='A seed for determinism of this test.')

    num_funcs = 0x30
    func_size = 0xf0
    func_name_len = 0x20

    # Index of the special function. We will later search a small variation of
    # the function inside the database, and expect to find this function.
    special_func_idx = random.randrange(num_funcs)
    special_func = None


    for i in range(num_funcs):
        # Generate function data:
        func_data = rand_bytes(func_size)
        # Generate random name and comment:
        func_name = rand_ascii_lowercase(func_name_len)
        func_comment = rand_ascii_lowercase(func_name_len)

        s = sign(func_data,16)
        # Add the function:
        # fdb_mem.add_function(func_name,func_data,func_comment)

        # If this is the special function, we keep it for later.
        if i == special_func_idx:
            special_func_data = bytes(func_data)
            special_func_name = func_name
            special_func_comment = func_comment






