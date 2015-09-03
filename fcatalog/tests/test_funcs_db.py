import unittest
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


########################################
########################################


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


def num_matches(s1,s2):
    """
    Calculate the amount of entries where s1[i] == s2[i]
    """
    assert len(s1) == len(s2)
    return sum(1 for i in range(len(s1)) if s1[i] == s2[i])

def test_num_matches():
    """
    Make sure that num_matches works correctly.
    """
    s1 = [1,2,3,4]
    s2 = [1,2,8,4]
    s3 = [0,9,4,3]
    assert num_matches(s1,s2) == 3
    assert num_matches(s1,s1) == 4
    assert num_matches(s1,s3) == 0

def change_random_byte(bs):
    """
    Change a random byte to another random byte in a stream of bytes.
    Return the new bytes stream.
    """
    # Nothing to do if bs is empty:
    if len(bs) == 0:
        return bs

    # Pick a random index:
    idx = random.randrange(len(bs))
    return bs[:idx] + rand_bytes(1) + bs[idx+1:]


class TestGetSimilars(unittest.TestCase):
    def setUp(self):
        """Tests setup"""
        # Build database in memory. Should be quicker.
        self.fdb_mem = DebugFuncsDB(':memory:',NUM_HASHES)

        # Pick an initial seed, for determinisim.
        random.seed(a='A seed for determinism of this test.')

        self.num_funcs = 0x400
        self.func_size = 0xf0
        self.func_name_len = 0x20

        # Index of the special function. We will later search a small variation
        # of the function inside the database, and expect to find this
        # function.
        special_func_idx = random.randrange(self.num_funcs)
        special_func = None

        # Insert functions to db:
        for i in range(self.num_funcs):
            # Generate function data:
            func_data = rand_bytes(self.func_size)
            # Generate random name and comment:
            func_name = rand_ascii_lowercase(self.func_name_len)
            func_comment = rand_ascii_lowercase(self.func_name_len)

            # s = sign(func_data,16)
            # Add the function:
            self.fdb_mem.add_function(func_name,func_data,func_comment)

            # If this is the special function, we keep it for later.
            if i == special_func_idx:
                self.special_func_data = bytes(func_data)
                self.special_func_name = func_name
                self.special_func_comment = func_comment


    def test_match_random_func(self):
        """
        Try to find similarity for a random function. We expect that now
        results will show up at all.
        """
        # Generate a random function:
        func_data = rand_bytes(self.func_size)
        sims = self.fdb_mem.get_similars(func_data,1)
        # We assume that no function is similar to func_data (Even in one entry),
        # so we expect to get no results. Getting a result is possible, but very
        # surprising.
        assert len(sims) == 0

    def test_match_special_func(self):
        """
        Try to find similarity for the special function. We expect to find it.
        """
        sims = self.fdb_mem.get_similars(self.special_func_data,5)
        # We assume that only the special function will return:
        assert len(sims) == 1

        assert sims[0].func_hash == strong_hash(self.special_func_data)
        assert sims[0].func_name == self.special_func_name
        assert sims[0].func_comment == self.special_func_comment
        assert sims[0].func_sig == sign(self.special_func_data,NUM_HASHES)


    def test_match_like_special_func(self):
        """
        Try to find similarity for a function that is just a bit different from
        the special function. We expect to find the special function.
        """
        func_data = self.special_func_data
        # Change some bytes randomly:
        for i in range(5):
            func_data = change_random_byte(func_data)

        sims = self.fdb_mem.get_similars(func_data,5)
        # We assume that only the special function will return:
        assert len(sims) == 1

        assert sims[0].func_hash == strong_hash(self.special_func_data)
        assert sims[0].func_name == self.special_func_name
        assert sims[0].func_comment == self.special_func_comment
        assert sims[0].func_sig == sign(self.special_func_data,NUM_HASHES)


    def tearDown(self):
        """Tests teardown"""
        # Close the database:
        self.fdb_mem.close()


