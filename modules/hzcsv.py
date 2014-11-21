#!/usr/bin/env python


"""
CSV Utility Module
"""


import csv
import re


__version__ = '0.0.0'


#=============================================================================
class reader( csv.reader ):
    """
    Implements similar functionality as the built-in CSV reader module, but
    maps data to be contained in objects (rather than lists or dicts), and
    also converts data to more useful types suitable for data analysis.
    In this implementation, it is assumed that the first row of a CSV file
    _always_ contains column names.
    """

    #=========================================================================
    def __init__( self, csvfile, dialect = 'excel', **fmtparams ):
        """
        Initializes a reader object.
        """

        # get a reference to the parent object instance
        self._parent = super( reader, self )

        # invoke parent constructor
        self._parent.__init__( csvfile, dialect, **fmtparams )

        # load column name list
        self._columns = []
        columns = self._parent.next()
        for column in columns:
            self._columns.append( wordify( column ) )

        # create an initial record to lazily pass data back to the user
        self.record = record( self._columns )


    #=========================================================================
    def keys( self ):
        """
        Returns the list of column names.
        """
        return self._columns


    #=========================================================================
    def next( self ):
        """
        Override the next() method to return objects rather than lists.
        """

        # get the next row out of the CSV file
        row = self._parent.next()

        # update the internal record object
        self.record.load( row )

        # return the record instance
        return self.record


#=============================================================================
class record( object ):
    """
    Manage a record of CSV data (one per row).
    """

    #=========================================================================
    def __init__( self, columns, values = None ):
        """
        Initializes a record object.
        @param columns List of column names (keys) for use as attribute names
                       Note: It is assumed that each string is safe for use
                       as an attribute name.
        @param values  Optional initial list of data values for this record
        """

        # make a copy of the columns list
        self._columns = list( columns )

        # create attributes for each column
        for index in range( len( self._columns ) ):

            # load data into object
            setattr( self, self._columns[ index ], None )

        # see if any data was specified
        if values is not None:

            # load the values into the object's state
            self.load( values )


    #=========================================================================
    def __getitem__( self, index ):
        """
        Retrieves a value from numeric index using list notation.
        @param index The numeric index for which to fetch a requested value
        @return      The requested value at the given index
        """

        # return the attribute at the given numeric index
        return getattr( self, self._columns[ index ] )

    #=========================================================================
    def __iter__( self ):
        """
        Return an iterable copy of the data to support the iterator protocol.
        @return A list of values from the object's state
        """
        return self.values()


    #=========================================================================
    def __len__( self ):
        """
        Return length of record to support the sequence protocol.
        @return The number of values in this record
        """
        return len( self._columns )


    #=========================================================================
    def keys( self ):
        """
        Returns the list of attribute names.
        """
        return self._columns


    #=========================================================================
    def load( self, values ):
        """
        Loads values into the object.
        @param values List of data values (strings) to load into the object
        """

        # count number of columns
        num_columns = len( self._columns )

        # count the number of passed values
        num_values = len( values )

        # even it out, if necessary
        if num_values < num_columns:
            values.extend( [ None ] * ( num_columns - num_values ) )

        # load data into each attribute
        for index in range( num_columns ):

            # load data into object
            setattr(
                self,
                self._columns[ index ],
                type_convert( values[ index ] )
            )


    #=========================================================================
    def values( self ):
        """
        Constructs a list of values in the object.
        @return A list of values from the object's state
        """

        # count expected number of values
        num_columns = len( self._columns )

        # always return enough data for a full record
        values = [ None ] * num_columns

        # load data from object into list
        for index in range( num_columns ):
            values[ index ] = self.__getitem__( index )

        # return the list of values in this record
        return values


#=============================================================================
def type_convert( value ):
    """
    Performs pattern-style type conversion for CSV-originating data.
    """

    # looks like a normal integer
    if re.match( r'^-?\d+$', value ) is not None:
        return int( value )

    # looks like an integer in hexadecimal notation
    elif re.match( r'^0(x|X)[a-fA-F0-9]+$', value ) is not None:
        return int( value, 16 )

    # looks like a fractional number
    elif re.match(
        r'^-?((\d+\.\d*)|(\d*\.\d+))((e|E)-?\d+)?$',
        value
    ) is not None:
        return float( value )

    # do not attempt type conversion
    return value


#=============================================================================
def wordify( string ):
    """
    Attempts to check/convert any string into a word suitable for use in
    a programming language.
    """

    # trim the string
    string = string.trim()

    # check for internal whitespace
    string = re.sub( r'[ \t\r\n]+', '_', string )

    # sanitize for allowed characters
    string = re.sub( r'[^a-zA-Z0-9_]', '', string )

    # make sure string begins with a valid alphabetic character
    string = re.sub( r'^\d+', '', string )

    # return the wordified string
    return string


#=============================================================================
def run_tests():
    """
    Execute built-in unit tests.
    """

    import cStringIO

    example = """a,b_2,c-3,d 4,e
1,2,3,4,5
5,4,3,2,1
-5,3.14,1e6,1.2e-2,0x15
hello,world,"other, stuff",4th column,fifth column"""

    csv_file_handle = cStringIO( example )

    reader = reader( csv_file_handle )

    print reader.keys()

    for rec in reader:
        print rec.values()


#=============================================================================
def main( argv ):
    """
    Script execution entry point
    @param argv         Arguments passed to the script
    @return             Exit code (0 = success)
    """

    # imports when using this as a script
    import argparse

    # create and configure an argument parser
    parser = argparse.ArgumentParser(
        description = 'CSV Utility Module',
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

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # execute built-in unit tests
    return run_tests()


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )

