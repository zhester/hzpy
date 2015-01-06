#!/usr/bin/env python


"""
Markdown Parser Module
"""


import io
import re
import StringIO


__version__ = '0.0.0'


#=============================================================================
class Input( object ):
    """
    Text data input object.  This acts like a read-only file stream for other
    parts of the module.
    """

    #=========================================================================
    def __init__( self, source = None ):
        """
        Initializes an Input object.
        """
        super( Input, self ).__init__()
        self._autoclose = False
        self._stream    = None
        if source is not None:
            if hasattr( source, 'read' ) == True:
                self._stream = source
            else:
                self._autoclose = True
                self._stream    = StringIO.StringIO( source )


    #=========================================================================
    def __del__( self ):
        """
        Releases resources needed for an Input object.
        """
        if self._autoclose == True:
            self._stream.close()


    #=========================================================================
    def __getattr__( self, name ):
        """
        Catches attribute references that are not defined locally.
        """
        if hasattr( self._stream, name ):
            return getattr( self._stream, name )
        raise AttributeError(
            'Attribute "{}" undefined in object.'.format( name )
        )


    #=========================================================================
    def __str__( self ):
        """
        Creates the simple string-like representation of this stream.
        """
        if hasattr( self._stream, 'getvalue' ):
            return self._stream.getvalue()
        self._stream.seek( 0, io.SEEK_SET )
        return self._stream.read()


    #=========================================================================
#    def read( self, size = None ):
#        """
#        Implements reading from the input stream.
#        """
#        if size is None:
#            return self._stream.read()
#        return self._stream.read( size )


#=============================================================================
class BlockInput( Input ):
    """
    Specializes the text stream input class to be aware of "block level"
    divisions in the source.  This provides additional benefit to stream-based
    parsing without needing to read entire files into memory.
    """

    #=========================================================================
    def __init__( self, *args, **kwargs ):
        """
        Initializes a BlockInput object.
        """
        super( BlockInput, self ).__init__( *args, **kwargs )
        self.nblocks = 0      # number of blocks encountered
        self.nlines  = 0      # number of lines read from source


    #=========================================================================
    def __iter__( self ):
        """
        Declare support for the iterator protocol.
        """
        self.nblocks = 0
        self.nlines  = 0
        self._stream.seek( 0, io.SEEK_SET )
        return self


    #=========================================================================
    def next( self ):
        """
        Implements iterator-style retrieval of the next block in the input
        stream.
        """
        result = self.readblock()
        if result == None:
            raise StopIteration()
        return result


    #=========================================================================
    def readblock( self ):
        """
        Similar in function to the ubiquitous `readline()` I/O function, this
        method is block-aware.

        Note: Blocks, here, are defined differently than the rules defined by
        Markdown.  Markdown allows for separation of blocks by lines
        containing whitespace characters other than newlines.  For
        stream-based parsing, this creates a number of challenges.  For
        simplicity and efficiency, I've decied to modify the definition of an
        empty line to be that which contains only a newline character.
        """

        # define a local function to test the emptiness of any line
        def is_empty_line( string ):
            return ( string == '\n' ) or ( string == '\r\n' )

        # read lines until we have a string to begin buffering
        line = self._readline()
        while ( line != '' ) and ( is_empty_line( line ) == True ):

            # read the next line
            line = self._readline()

        # readline() returns an empty string at the end of the file
        if line == '':
            return None

        # start buffering this block with the first non-empty line
        block = line

        # read lines until we hit an empty line or the EOF
        line = self._readline()
        while ( line != '' ) and ( is_empty_line( line ) == False ):

            # add line to buffer
            block += line

            # read the next line out of the file
            line = self._readline()

        # return the block we read from the stream
        self.nblocks += 1
        return block


    #=========================================================================
    def _readline( self ):
        """
        Implements an internal version of readline for accounting purposes.
        """
        line = self._stream.readline()
        if line != '':
            self.nlines += 1
        return line


#=============================================================================
class Document( object ):
    """
    Models a Markdown document.
    """

    #=========================================================================
    def __init__( self ):
        """
        Initializes a Document object.
        """
        super( Document, self ).__init__()




#=============================================================================
def convert_files( target, source, target_format = None ):
    """
    Converts a Markdown file into another format.  The target format is
    determined by the target file name's extension, or if it is explicitly
    given in the optional argument.  The target format is specified by file
    name extension string (e.g. `html`).

    Current list of supported target formats:
    - html
    """
    pass


#=============================================================================
def _test( *args ):
    """
    Run internal unit tests.
    """

    # create a simple test Markdown document
    source = """Heading 1
=========

Paragram under heading 1.

Heading 2
---------

Paragraph under heading 2.
This paragraph has multiple lines.

### Heading 3

Another **type** of _heading_.

"""

    ### ZIH early testing
    block_reader = BlockInput( source )
    for block in block_reader:
        print '=== Start Block ==='
        print block
        print '=== End Block ==='
        print 'Num Lines: {}\nNum Blocks: {}'.format(
            block_reader.nlines,
            block_reader.nblocks
        )



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
        description = 'Markdown Parser Module',
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
        '-t',
        '--test',
        default = False,
        help    = 'Run all internal unit tests.',
        action  = 'store_true'
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
        'source',
        default = None,
        nargs   = '?',
        help    = 'Markdown document to convert.'
    )
    parser.add_argument(
        'target',
        default = None,
        nargs   = '?',
        help    = 'Conversion output document.'
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # check for running the built-in unit tests
    if ( 'test' in args ) and ( args.test == True ):
        test_result = _test( argv[ 2 : ] )
        return os.EX_OK if test_result == True else os.EX_SOFTWARE

    # assume we are using the module to convert a document
    result = convert_files( args.target, args.source )

    # return result of convertion
    if result == True:
        return os.EX_OK
    return os.EX_SOFTWARE


#=============================================================================
if __name__ == "__main__":
    import os
    import sys
    sys.exit( main( sys.argv ) )


