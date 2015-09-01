import sqlite3
import os

from catalog1 import sign


class FuncsDB:
    def __init__(self,db_path,num_hashes):
        # Keep as members:
        self._db_path = db_path
        self._num_hashes = num_hashes

        # If the database file does not exist, we create an empty database:
        if not os.path.isfile(db_path):
            self._build_empty_db()


    def _build_empty_db(self):
        """
        Build an initial empty database.
        Create tables and indices.
        """

        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()

        cmd_tbl = \
            """CREATE TABLE funcs(
                hash BLOB PRIMARY KEY,
                func_name TEXT NOT NULL,
                head_comment TEXT NOT NULL"""

        for i in range(self._num_hashes):
            cmd_tbl += ',\n'
            cmd_tbl += 'c' + str(i+1) + ' INTEGER NOT NULL'

        cmd_tbl += ')'

        # Create the funcs table:
        print(cmd_tbl)
        c.execute(cmd_tbl)

        # Add index for each of the 'c{num}' columns:
        for i in range(self._num_hashes):
            cname = 'c' + str(i+1)
            cmd_index = 'CREATE INDEX idx_' + cname + ' ON ' + \
                    'funcs(' + cname + ')'
            c.execute(cmd_index)

        conn.commit()
        conn.close()


    def add_function(self,func_data):
        pass

    def get_similars(self,func_data,num_similars):
        pass


