#!/usr/bin/env python

def oopy():
    import MySQLdb as mdb
    con = mdb.connect( 'localhost', 'hz', 'noodletruck', 'hz' )
    cur = con.cursor()
    cur.execute( 'select * from cdb_projects' )
    rows = cur.fetchall()
    print len(rows), 'records in set'
    for row in rows:
        strs = []
        for col in row:
            strs.append(str(col))
        print ','.join(strs)
    con.close()

def proc():
    import _mysql
    con = _mysql.connect( 'localhost', 'hz', 'noodletruck', 'hz' )
    con.query( 'select * from cdb_projects' )
    res = con.store_result()
    num = res.num_rows()
    print num, 'records in set'
    for i in range(num):
        strs = []
        row = res.fetch_row()[ 0 ]
        for col in row:
            strs.append(str(col))
        print ','.join(strs)
    con.close()

def main(argc, argv):

    #oopy()

    proc()

    return 0;

if __name__ == "__main__":
    import sys
    sys.exit(main(len(sys.argv), sys.argv))