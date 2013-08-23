##############################################################################
#
#   scancsv.py - Scan CSV Data for Significant Events
#
#   Scans any CSV file looking for dramatic changes in a specific field's
#   data.  The output is a CSV file of the same format (including the header
#   row, if present) that contains only rows where a field value exceeded
#   the row-to-row difference threshold.
#
#   scancsv.py <in file> [<out file>]
#       [<column name>|<column index>] [<threshhold>]
#
#   <in file>       Input CSV file name
#   <out file>      Output CSV file name
#   <column name>   Name of column to detect changes (column header)
#   <column index>  Numeric index of column to detect changes (no headers)
#   <threshold>     Row-to-row difference threshold to trigger an event
#
##############################################################################


import csv
import re


#===============================================================================
class detection_filter:
    """
    A detection filter object maintains filter state between successive calls
    to check for a trigger in input data values.  The filter can be used with
    a moving window average to help remove excessive jitter from the input.
    """

    #===========================================================================
    def __init__( self, thold = 100, init = 0, wsize = 1 ):
        """
        Object constructor
        @param thold Trigger threshold value
        @param init  The initial seed value of the filter
        @param wsize The number of values in the averaging window
        """

        # initialize object
        self.thold  = thold
        self.wsize  = wsize
        self.window = [ init ] * self.wsize

    #===========================================================================
    def trigger( self, value ):
        """
        Check if the specified value triggers a notable event condition.
        @param value The value to input into the filter
        """

        # assume there will not be an event
        result = False

        # determine the previous filter state
        avg = sum( self.window ) / self.wsize

        # compare to filter input to see if it exceeds the threshold
        if abs( avg - value ) >= self.thold:
            result = True

        # pop first element off list, append new value (FIFO)
        self.window.pop( 0 )
        self.window.append( value )

        # return trigger result
        return result


#===============================================================================
def main( argv ):
    """ Script execution entry point """

    in_name      = 'index.csv'
    out_name     = 'scan.csv'
    use_names    = False
    column_index = 0
    column_name  = 'id'
    threshold    = 2000.0

    if len( argv ) > 1:
        if argv[ 1 ] == 'help':
            print 'Usage: scancsv.py <in file> [<out file>]' \
                  + ' [<column name>|<column index>] [<threshhold>]'
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
        threshold = float( argv[ 4 ] )

    ifile = open( in_name, 'rb' )
    ofile = open( out_name, 'wb' )

    reader = csv.reader( ifile )

    if use_names == True:
        fields       = reader.next()
        column_index = fields.index( column_name )
        ofile.write( ','.join( fields ) + '\n' )

    df = detection_filter( thold = threshold, init = 0.0 )

    ecount = 0

    for row in reader:
        if df.trigger( float( row[ column_index ] ) ) == True:
            ofile.write( ','.join( row ) + '\n' )
            ecount += 1

    ofile.close()
    ifile.close()

    print 'Copied %d possible events from %s to %s.' \
          % ( ecount, in_name, out_name )

    # Return success.
    return 0


#===============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
