import pytest
import sqlite3

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

    fdb_mem.add_function('func_name',b'func_data','func_comment')
    res = fdb_mem.get_similars(b'func_data',num_similars=3)
    assert len(res) == 1

    fdb_mem.add_function('func_name2',b'func_data2','func_comment2')
    res = fdb_mem.get_similars(b'func_data2',num_similars=3)
    assert len(res) == 2

    assert res[0].func_hash == strong_hash(b'func_data2')
    assert res[1].func_hash != strong_hash(b'func_data2')

    print(res[0].func_sig)
    print(sign(b'func_data2',NUM_HASHES))
    assert res[0].func_sig == sign(b'func_data2',NUM_HASHES)

