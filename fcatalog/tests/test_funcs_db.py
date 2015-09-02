import pytest
import os
import shutil
import tempfile
import sqlite3

from funcs_db import FuncsDB


class DebugFuncsDB(FuncsDB):
    def count(self):
        """
        Count the amount of lines inside the funcs table.
        """
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()

        cmd_count = "SELECT COUNT(*) from funcs"
        c.execute(cmd_count)
        res = c.fetchone()[0]
        conn.close()

        return res


@pytest.fixture(scope='module')
def fdb(request):
    """
    Create a FuncsDB instance (A new database on disk).
    """
    # Create a temporary directory:
    p = tempfile.mkdtemp()
    db_path = os.path.join(p,'my_db.db')
    fdb = DebugFuncsDB(db_path,16)

    def fin():
        """Finalization of the fixture"""
        # Remove the database:
        shutil.rmtree(db_path)
    return fdb


def test_funcs_db_basic(fdb):
    """
    Create a new database using FuncsDB.
    """
    pass


def test_add_function(fdb):
    """
    Try to add a 'reversed' new function into the database.
    """
    assert fdb.count() == 0
    fdb.add_function('func_name',b'func_data','func_comment')
    assert fdb.count() == 1


