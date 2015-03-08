#!/usr/bin/env python


"""
Text Handling and Formatting Utilities
======================================

TODO
----

- add the ability to specify alignment of each column's data and heading
  - (<,>,^) : (left,right,center)
- add an option to format the table as a markdown table
- add an option to not treat the first row as headings
- add an option to specify a list of headings separately from the data
- add an option to align items on an arbitrary character (e.g. '.')
"""


import bisect
import collections
import re


__version__ = '0.0.0'


#=============================================================================

# column information container
column_info = collections.namedtuple( 'column_info', 'min max avg isnum' )

# patterns to detect numeric strings
type_patterns = [
    ( 'DECIMAL',     r'\d*\.\d*(?:[eE][+-]?\d+)?' ),
    ( 'HEX_INTEGER', r'0(?:x|X)[0-9a-fA-F]+'      ),
    ( 'INTEGER',     r'\d+(?:[eE][+-]?\d+)?'      ),
]


#=============================================================================
def tabular( data, width = 80 ):
    """
    Formats a two-dimensional list in a tabular text format.

    @param data  A two-dimensional list of data to display
    @param width The maximum width of the table in characters
    @return      A textual representation of a table
    """

    # measure the data
    info        = _column_info( data )
    num_columns = len( info )

    # data item formatting, separators, padding
    sep    = '|'
    pad    = ' '
    joiner = pad + sep + pad
    left   = sep + pad
    right  = pad + sep
    bsep   = '+'
    bfill  = '-'
    trunc  = '\xc2' # double, right-angle quote
    ifmt   = '{{:<{}}}'

    # generates a width-calculation function
    def make_get_table_width( brdr_width, join_width ):
        def closure( widths ):
            return sum( widths ) + brdr_width + join_width
        return closure

    # widths of table decorations
    join_width = len( joiner ) * ( num_columns - 1 )
    brdr_width = len( left ) + len( right )

    # build the width-calculation function
    get_table_width = make_get_table_width( brdr_width, join_width )

    # calculate total width of table with the given data
    minimums    = [ i.min for i in info ]
    maximums    = [ i.max for i in info ]
    averages    = [ i.avg for i in info ]
    table_width = get_table_width( maximums )

    # initial widths of each column
    widths = maximums

    # see if we should attempt to resize the table
    if table_width > width:

        # get a list of trancate-able columns in order of shorted to longest
        truncable = []
        tr_widths = []
        for index in range( num_columns ):
            col = info[ index ]
            if col.isnum == False:
                insert_index = bisect.bisect( tr_widths, col.max )
                truncable.insert( insert_index, index )
                tr_widths.insert( insert_index, col.max )
        num_truncable = len( truncable )

        # make sure there's something worth truncating
        if num_truncable > 0:

            # reverse the list of columns for longest to shortest
            truncable = truncable[ : : -1 ]

            # length of truncation markers (if all columns need them)
            marker_lengths = len( trunc ) * num_truncable

            # set up a list of "new" widths
            new_widths = widths

            # calculate a average and minimum table width
            avg_table_width = get_table_width( averages ) + marker_lengths
            min_table_width = get_table_width( minimums ) + marker_lengths

            # see if we can reach the new width using averages
            if avg_table_width <= width:
                for tri in truncable:
                    new_widths[ tri ] = info[ tri ].avg
                    if get_table_width( new_widths ) <= width:
                        break

            # see if we can reach the new width using minimums
            elif min_table_width <= width:
                for tri in truncable:
                    new_widths[ tri ] = info[ tri ].min
                    if get_table_width( new_widths ) <= width:
                        break

            # truncate all truncate-able columns
            else:
                trunc_all = ( min_table_width - width ) / num_truncable
                for tri in truncable:
                    new_widths[ tri ] = trunc_all

            # calculate the new width of the table
            table_width = get_table_width( new_widths )

            # see if we can grow the longest column to fill it back out
            if table_width < width:
                refill = width - table_width
                new_widths[ truncable[ 0 ] ] += refill

            # re-assign the widths list to truncate items in each column
            widths = new_widths

            # generate the list of per-column item format strings
            ### ZIH - temporary: add truncation markers
            item_formats = []
            for i in range( num_columns ):
                if i in truncable:
                    item_formats.append(
                        '{{:<{}.{}}}'.format( widths[ i ], widths[ i ] )
                    )
                else:
                    item_formats.append(
                        ifmt.format( widths[ i ] )
                    )

    # item truncation not needed, or not feasible
    else:

        # generate the list of per-column item format strings
        item_formats = [ ifmt.format( w ) for w in widths ]

    # render a separator bar
    bar = '{}{}{}'.format(
        bsep,
        bsep.join( bfill * ( w + ( 2 * len( pad ) ) ) for w in widths ),
        bsep
    )

    # create a per-row format string
    row_format = left + joiner.join( item_formats ) + right

    # pull the heading row
    headings = data[ 0 ]

    # construct the table
    return '\n'.join(
        [
            bar,
            row_format.format( *headings ),
            bar,
            '\n'.join( row_format.format( *row ) for row in data[ 1 : ] ),
            bar
        ]
    )


#=============================================================================
def _column_info( data, heads = True ):
    """
    Extracts column information from a two-dimensional list.

    Note: This assumes each sub-list in the list contains the same number of
    items as the first sub-list.

    @param data  Two-dimensional list of data
    @param heads True if we consider the first row headings
    @return      A list of column_info named tuples
    """

    # number of sub-lists
    num_lists = len( data )

    # number of columns
    num_cols = len( data[ 0 ] )

    # column details (minimum, maximum, sum, is number?)
    info = []

    # check for headings
    if heads:
        first    = data[ 1 ]
        num_rows = num_lists - 1
    else:
        first    = data[ 0 ]
        num_rows = num_lists

    # detect types and initialize statistical information
    for item in first:
        ct = type( item )
        if ct is str:
            isnum = _is_number( item )
        elif ( ct is int ) or ( ct is float ):
            item  = str( item )
            isnum = True
        else:
            item  = str( item )
            isnum = False
        length = len( item )
        info.append( [ length, length, 0, isnum ] )

    # iterate through each "row" in the data
    for sublist in data:

        # iterate through each column in this sub-list
        for index in range( num_cols ):

            # length of item in column
            length = len( str( sublist[ index ] ) )

            # minimum
            if length < info[ index ][ 0 ]:
                info[ index ][ 0 ] = length

            # maximum
            if length > info[ index ][ 1 ]:
                info[ index ][ 1 ] = length

            # sum
            info[ index ][ 2 ] += length

    # return the column information as a list of named tuples
    return [
        column_info( i[ 0 ], i[ 1 ], ( i[ 2 ] / num_rows ), i[ 3 ] )
        for i in info
    ]


#=============================================================================
def _is_number( string ):
    """
    Determines if a string contains a numeric value.
    """
    for pattern in type_patterns:
        result = re.match( pattern[ 1 ], string )
        if result is not None:
            return True
    return False


#=============================================================================
def _test_tabular( log ):
    """
    Tests the tabular formatting function.
    """

    import subprocess

    log.put( 'Testing tabular()' )
    data = [
        [ 'A', 'B', 'C',  'I',       'F', 'String' ],
        [ 'a', 'b', 'c',   42,   3.14159, 'longer column' ],
        [ 'a', 'b', 'c',    3,   1.2345,  'a longer column' ],
        [ 'a', 'b', 'c',    9,   0.876,   'a slightly longer column' ],
        [ 'a', 'b', 'c', 1259, 201.3,     'a longish column' ],
    ]
    log.put( tabular( data ) )

    log.put( 'Testing tabular() (truncation)' )
    data[ 2 ][ 5 ] = 'this is a very long column that will make the table' \
        + ' extend past column eighty'
    log.put( tabular( data ) )

    dims = subprocess.check_output( [ 'stty', 'size' ] )
    rows, columns = dims.split()
    columns = int( columns )
    log.put( 'Testing tabular() (console width = {})'.format( columns ) )
    log.put( tabular( data, width = columns ) )


#=============================================================================
def _test():
    """
    Executes all module test functions.

    @return True if all tests pass, false if one fails.
    """

    # imports for testing only
    import inspect

    # set up a simple logging facility to capture or print test output
    class TestError( RuntimeError ):
        pass
    class TestLogger( object ):
        def fail( self, message ):
            caller = inspect.getframeinfo( inspect.stack()[ 1 ][ 0 ] )
            output = '## FAILED {}: {} ##'.format( caller.lineno, message )
            self.put( output )
            raise TestError( output )
        def put( self, message ):
            sys.stdout.write( '{}\n'.format( message ) )
    log = TestLogger()

    # list of all module members
    members = globals().copy()
    members.update( locals() )

    # iterate through module members
    for member in members:

        # check members for test functions
        if ( member[ : 6 ] == '_test_' ) and ( callable( members[ member ] ) ):

            # execute the test
            try:
                members[ member ]( log )

            # catch any errors in the test
            except TestError:

                # return failure to the user
                return False

    # if no test fails, send a helpful message
    log.put( '!! PASSED !!' )

    # return success to the user
    return True


#=============================================================================
def main( argv ):
    """
    Script execution entry point
    @param argv List of arguments passed to the script
    @return     Shell exit code (0 = success)
    """

    # imports when using this as a script
    import argparse

    # create and configure an argument parser
    parser = argparse.ArgumentParser(
        description = 'Text Handling and Formatting Utilities',
        add_help    = False
    )
    parser.add_argument(
        '-h',
        '--help',
        default = False,
        help    = 'Display this help message and exit.',
        action  = 'help'
    )
    parser.add_argument(
        '-v',
        '--version',
        default = False,
        help    = 'Display script version and exit.',
        action  = 'version',
        version = __version__
    )
    parser.add_argument(
        '-t',
        '--test',
        default = False,
        help    = 'Execute built-in unit tests.',
        action  = 'store_true'
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # user requests built-in unit tests
    if args.test != False:
        result = _test()
        if result == False:
            return os.EX_SOFTWARE
        return os.EX_OK

    # check args.* for script execution here
    else:
        print 'Module executed as script.'
        return os.EX_USAGE

    # return success
    return os.EX_OK


#=============================================================================
if __name__ == "__main__":
    import os
    import sys
    sys.exit( main( sys.argv ) )

