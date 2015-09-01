
from funcs_db import FuncsDB

def test_hello(tmpdir):
    p = tmpdir.mkdir('sub')
    db_path = str(p.dirpath('my_db.db'))

    fdb = FuncsDB(db_path,16)




