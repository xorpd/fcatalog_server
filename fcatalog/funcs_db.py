import sqlite3
import os
import collections

from catalog1 import sign,strong_hash

class FuncsDBError(Exception):
    pass


DBSimilar = collections.namedtuple('DBSimilar',\
        ['func_hash','func_name','func_comment','func_sig'])


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
                func_hash BLOB PRIMARY KEY,
                func_name TEXT NOT NULL,
                func_comment TEXT NOT NULL"""

        for i in range(self._num_hashes):
            cmd_tbl += ',\n'
            cmd_tbl += 'c' + str(i+1) + ' INTEGER NOT NULL'

        cmd_tbl += ');'

        # Create the funcs table:
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
                    (func_hash,func_name,func_comment"""

        for i in range(self._num_hashes):
            cmd_insert += ',c' + str(i+1) + ' '

        cmd_insert += ') values (?,?,?' + (',?' * self._num_hashes) + ');'

        c.execute(cmd_insert,[\
                sqlite3.Binary(func_hash),func_name,func_comment] + s)

        self._conn.commit()


    def get_similars(self,func_data,num_similars):
        """
        Get a list of at most num_similars similar functions to a given
        function. The list will be ordered by similarity. The first element is
        the most similar one.
        """
        # A list to keep results:
        res_list = []

        self._check_is_open()
        s = sign(func_data,self._num_hashes)
        func_hash = strong_hash(func_data)

        c = self._conn.cursor()

        # Get all potential candidates for similarity:
        lselects = ['SELECT * FROM funcs WHERE c' + str(i+1) + '=?' \
                for i in range(self._num_hashes)]
        # Also search for exact match (Using strong hash):
        sel_hash = 'SELECT * FROM funcs WHERE func_hash=?'
        lselects.append(sel_hash)
        selects = "\nUNION\n".join(lselects)

        # Find best matching rows
        matching = 'SELECT func_hash,func_name,func_comment,'

        sig_vals = ",".join(['c' + str(i+1) for i in range(self._num_hashes)])
        matching += sig_vals

        # Make an expression (c1=sig[0]) + (c2=sig[1]) + ...
        # Which will be the grade of every row (The amount of matches of the
        # signature).
        sig_sum = ' + '.join(\
                ['(c' + str(i+1) + '=?)' for i in range(self._num_hashes)])
        matching += ',(' + sig_sum + ') AS grade '

        matching += 'FROM (' + selects + ') '

        # Find the num_similars rows with highest grade:
        matching += 'ORDER BY grade DESC LIMIT ?'

        c.execute(matching,s + s + [func_hash,num_similars])

        for res in c.fetchall():
            res_hash,res_name,res_comment = res[:3]
            # We don't want to include the last superficial column grade, this
            # is why we have -1 here:
            res_sig = list(res[3:-1])
            sres = DBSimilar(\
                    func_hash=res_hash,\
                    func_name=res_name,\
                    func_comment=res_comment,\
                    func_sig=res_sig)

            # If we have exact match (Using strong hash), we move the result to
            # the beginning of res_list. Otherwise, we just append to the end.
            # The exact match will always be at the beginning.
            if res_hash == func_hash:
                res_list.insert(0,sres)
            else:
                res_list.append(sres)

        return res_list

