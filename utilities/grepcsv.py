##############################################################################
#
#   grepcsv.py - Grep CSV Data for Specified Values
#
#   grepcsv.py <in file> [<out file>]
#       [<column name>|<column index>] [<value>]
#
#   <in file>       Input CSV file name
#   <out file>      Output CSV file name
#   <column name>   Name of column to detect changes (column header)
#   <column index>  Numeric index of column to detect changes (no headers)
#   <value>         Value of column to copy into output
#
##############################################################################


import csv
import re


#===============================================================================
def main( argv ):
    """ Script execution entry point """

    in_name      = 'index.csv'
    out_name     = 'scan.csv'
    use_names    = False
    column_index = 0
    column_name  = 'id'
    value        = ''

    if len( argv ) > 1:
        if argv[ 1 ] == 'help':
            print 'Usage: grepcsv.py <in file> [<out file>]' \
                  + ' [<column name>|<column index>] [<value>]'
            return 0
        in_name = argv[ 1 ]
    if len( argv ) > 2:
        out_name = argv[ 2 ]
    if len( argv ) > 3:
        m = re.match( r'^\d+$', argv[ 3 ] )
        if m is not None:
            column_index = int( m.group( 0 ) )
        else:
            use_names   = True
            column_name = argv[ 3 ]
    if len( argv ) > 4:
        value = argv[ 4 ]

    ifile = open( in_name, 'rb' )
    ofile = open( out_name, 'wb' )

    reader = csv.reader( ifile )

    if use_names == True:
        fields       = reader.next()
        column_index = fields.index( column_name )
        ofile.write( ','.join( fields ) + '\n' )

    ecount = 0

    for row in reader:
        if row[ column_index ] == value:
            ofile.write( ','.join( row ) + '\n' )
            ecount += 1

    ofile.close()
    ifile.close()

    print 'Copied %d records from %s to %s.' \
          % ( ecount, in_name, out_name )

    # Return success.
    return 0


#===============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
