import sqlite3
import os

from catalog1 import sign,strong_hash

class FuncsDBError(Exception):
    pass


class FuncsDB:
    def __init__(self,db_path,num_hashes):
        # Keep as members:
        self._db_path = db_path
        self._num_hashes = num_hashes

        # Check if the db has existed before:
        db_existed = False
        if os.path.isfile(db_path):
            db_existed = True

        # Open a connection to the database.
        self._conn = sqlite3.connect(self._db_path)
        self._is_open = True
        
        # If the database file did not exist, we create an empty database:
        if not db_existed:
            self._build_empty_db()
        

    def _check_is_open(self):
        """
        Make sure that this FuncsDB instance is open.
        """
        if not self._is_open:
            raise FuncsDBError('FuncsDB instance is closed')


    def close(self):
        """
        Close the connection to the database.
        """
        self._check_is_open()
        self._conn.close()



    def _build_empty_db(self):
        """
        Build an initial empty database.
        Create tables and indices.
        """
        self._check_is_open()
        c = self._conn.cursor()

        cmd_tbl = \
            """CREATE TABLE funcs(
                hash BLOB PRIMARY KEY,
                func_name TEXT NOT NULL,
                func_comment TEXT NOT NULL"""

        for i in range(self._num_hashes):
            cmd_tbl += ',\n'
            cmd_tbl += 'c' + str(i+1) + ' INTEGER NOT NULL'

        cmd_tbl += ');'

        # Create the funcs table:
        print(cmd_tbl)
        c.execute(cmd_tbl)

        # Add index for each of the 'c{num}' columns:
        for i in range(self._num_hashes):
            cname = 'c' + str(i+1)
            cmd_index = 'CREATE INDEX idx_' + cname + ' ON ' + \
                    'funcs(' + cname + ');'
            c.execute(cmd_index)

        self._conn.commit()


    def add_function(self,func_name,func_data,func_comment):
        """
        Add a (Reversed) function to the database.
        """
        self._check_is_open()
        s = sign(func_data,self._num_hashes)
        func_hash = strong_hash(func_data)

        c = self._conn.cursor()

        cmd_insert = \
                """INSERT OR REPLACE into funcs 
                    (hash,func_name,func_comment"""

        for i in range(self._num_hashes):
            cmd_insert += ',c' + str(i+1) + ' '

        cmd_insert += ') values (?,?,?' + (',?' * self._num_hashes) + ');'

        self._conn.execute(cmd_insert,[\
                sqlite3.Binary(func_hash),func_name,func_comment] + s)

        self._conn.commit()


    def get_similars(self,func_data,num_similars):
        """
        Get a list of at most num_similars similar functions to a given
        function. The list will be ordered by similarity. The first element is
        the most similar one.
        """
        self._check_is_open()
        pass

