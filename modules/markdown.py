#!/usr/bin/env python


"""
Markdown Parser Module
======================

References
----------

http://daringfireball.net/projects/markdown/syntax#html
"""


import collections
import io
import re
import StringIO


__version__ = '0.0.0'


#=============================================================================
# Position information named tuple.
Position = collections.namedtuple(
    'Position',
    [ 'offset', 'line', 'column' ]
)


#=============================================================================
# Token content named tuple.
Token = collections.namedtuple( 'Token', [ 'ident', 'value', 'position' ] )


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
            'Attribute "{}" undefined in Input object.'.format( name )
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
    def getch( self ):
        """
        Retrieves the next character from the stream in a slightly more
        readable/documented interface.
        """
        return self._stream.read( 1 )


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
class Lexer( object ):
    """
    Very minimal/inefficient stream-style lexical parser.
    """

    #=========================================================================
    def __init__( self, stream = None, tspecs = None ):
        """
        Initializes a Lexer object.
        `stream` is a text input stream of some type.  It should support a
            `read()`, `seek()`, and `getch()` method.
        `tspecs` is a list of 2-tuples that specify token identifiers and
            their regular expressions for matching the token.
        """
        super( Lexer, self ).__init__()

        self._reo   = re.compile( r'\s' )
                                    # tokenizing regular expression object
        self._next  = self._reo.match
                                    # regular expression match iterator
        self._temp  = ''            # temporary stream storage (fix me!)
        self.column = 1             # current column in the current line
        self.line   = 1             # current line in the input
        self.offset = 0             # current offset into the input
        self.stream = stream        # text input stream
        self.tspecs = []            # token specification (list of 2-tuples)
        if tspecs is not None:
            self.tspecs = tspecs


    #=========================================================================
    def __iter__( self ):
        """
        Declare support for the iterator protocol.
        """
        self.stream.seek( 0, io.SEEK_SET )
        self._temp  = self.stream.read()
        self._reo   = re.compile(
            '|'.join(
                '(?P<{}>{})'.format( i, r ) for ( i, r ) in self.tspecs
            )
        )
        self._next  = self._reo.match
        self.column = 1
        self.line   = 1
        self.offset = 0
        return self


    #=========================================================================
    def next( self ):
        """
        Retrieve the next token from the input stream.
        """

        # attempt to match the next token in the "stream"
        match = self._next( self._temp, self.offset )

        # no token found, stop tokenizing
        if match is None:
            raise StopIteration()

        # retrieve the token identifier
        ident = match.lastgroup

        # retrieve the token string
        value = match.group( ident )

        # determine this token's position in the stream
        ### ZIH - need a good way to calculate the column
        position = Position( match.start(), self.line, -1 )

        # create the token tuple for reporting
        token = Token( ident, value, position )

        # see if this token contained newlines
        num_newlines = value.count( '\n' )
        if num_newlines > 0:
            self.line += num_newlines

        # update the offset into the string
        self.offset = match.end()

        # return the latest token
        return token


#=============================================================================
class Element( object ):
    """
    Models any element within a document.
    This class should be considered purely abstract.  Use BlockElement and
    InlineElement for building documents.
    """


    #=========================================================================
    def get_html( self ):
        """
        All inheriting classes must implement this method.
        """
        raise NotImplementedError()


    #=========================================================================
    def __init__( self, source ):
        """
        Initializes an Element object.
        """

        # invoke the parent initializer
        super( Element, self ).__init__()

        # set the Markdown source string
        self.source = source

        # initialize object state
        self.attributes = {}
        self.contents   = self.source.strip()
        self.name       = 'p'
        self.position   = {
            'offset' : -1,
            'line'   : -1,
            'column' : -1
        }

        # invoke customizeable element initialization
        self._initialize_element()


    #=========================================================================
    def __str__( self ):
        """
        Get the bare string representation of this element.
        """
        return self.contents


    #=========================================================================
    def set_position( self, offset, line = -1, column = -1 ):
        """
        Interface to load string position information into the object.
        """
        self.position[ 'offset' ] = offset
        self.position[ 'line' ]   = line
        self.position[ 'column' ] = column


    #=========================================================================
    def _get_html_attribute_string( self ):
        """
        Constructs an HTML attribute string for this element.
        """

        # start with a list of key-value pair strings
        pairs = [
            '{}="{}"'.format( k, v )
            for k, v in self.attributes.items()
        ]

        # check for need to use attributes
        if len( pairs ) > 0:

            # prepend a space for simple insertion into a tag string
            return ' ' + ' '.join( pairs )

        # no attributes necessary
        return ''


    #=========================================================================
    def _get_html_tag_string( self ):
        """
        Constructs an HTML tag string for this element.
        """

        # build attribute string
        attributes = self._get_html_attribute_string()

        # build tag string
        return '<{0}{1}>{2}</{0}>'.format(
            self.name,
            attributes,
            self.contents
        )


    #=========================================================================
    def _initialize_element( self ):
        """
        Method that inheriting classes may define if they require customized
        object initialization.
        """
        pass


#=============================================================================
class BlockElement( Element ):
    """
    Models a block element in a document.
    """

    #=========================================================================
    # list of element detection rules
    #   the first item is a unique-ish name for the type of element
    #   the second item is a pattern to test the entire block against
    #   note: these should be specified, roughly, in order of frequency as
    #       once a match is found, no further matches are tested
    #   note: if nothing matches, the element is assumed to be a paragraph
    rules = [
        ( 'h_underline', r'([^\n]+)\n([=-]+)' ),
        ( 'h_hash'     , r'^(#+) *(.+)'       ),
        ( 'pre'        , r'^\t| {4,}(.+)'     ),
        ( 'blockquote' , r'^\s*> *(.+)'       ),
        ( 'ul'         , r'^\s*[*+-] *(.+)'   ),
        ( 'ol'         , r'^\s*\d+\. *(.+)'   )
    ]


    #=========================================================================
    def _init_block( self, rule_id, match ):
        """
        Initialize internal details for the block element.
        """
        if rule_id == 'h_underline':
            if match.group( 2 )[ 0 ] == '-':
                self.name = 'h2'
            else:
                self.name = 'h1'
            self.contents = match.group( 1 ).strip()
        elif rule_id == 'h_hash':
            level = min( len( match.group( 1 ) ), 6 )
            self.name = 'h{}'.format( level )
            self.contents = match.group( 2 ).strip()
            self.contents = re.sub( r'(\s|#)+$', '', self.contents )
        ### ZIH - implement other blocks
        else:
            self.name = 'p'


    #=========================================================================
    def _parse_inlines( self ):
        """
        Parses the current block for all inline elements.
        """
        ### ZIH - impelement me
        pass


    #=========================================================================
    def get_html( self ):
        """
        Implement HTML fragment construction for any block element.
        """

        # construct the attribute string
        attributes = self._get_html_attribute_string()

        # start the block element markup
        html = '<{}{}>'.format( self.name, attributes )

        # detect and parse inline elements
        ### ZIH

        # assemble all the inline elements into the contents of the block
        ### ZIH

        ### ZIH - temp
        html += self.contents

        # return the completed block markup
        return '{}</{}>'.format( html, self.name )


    #=========================================================================
    def _initialize_element( self ):
        """
        Perform internal element type detection and content capturing.
        """

        # attempt to determine the type of block
        for rule in self.rules:
            match = re.match( rule[ 1 ], self.source, re.M )
            if match is not None:
                self._init_block( rule[ 0 ], match )


#=============================================================================
class InlineElement( Element ):
    """
    Models an inline element in a document.
    """


    #=========================================================================
    def get_html( self ):
        """
        Implement HTML fragment construction for any inline element.
        """

        # ZIH - determine if this tag is self-closing

        # construct the simple tag string
        return self._get_html_tag_string()


    #=========================================================================
    def _initialize_element( self ):
        """
        Perform internal element type detection and content capturing.
        """
        pass


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
This must support `inline code`.

#### Heading 4 #

This demonstrates [simple](http://hzian.com/) inline anchors.  Here's
[another](http://hzian.com/) link.

##### Heading 5 #####

    /* pre-formatted code is indented                           */
    /* this might be shell commands or programming code         */

    while( still_going = 1 ) {

        //it would be nice to intelligently "connect" successive code blocks
        //  (my editor leaves the empty lines free of indentation)

        printf( "<%s src=\\"%s\\"/>", "img", "image.png" );

    }

###### Heading 6

There are \*many\* characters that may be escaped:

\\\\back-slashes\\\\
\`back-ticks\`
\*asterisks\*
\_underscores\_
\{braces\}
\[brackets\]
\(parenthesis\)
\#hash marks\#
\+plus signs\+
\-hyphens\-
\.periods\.
\!exclamation points\!

# Another Heading 1

* A
* Bullet-ed
* List

1. An
2. Enumerated
3. List

> This is a block
> quote.

# HTML Target Documents

When the output document is HTML, the document output will convert certain
things into their HTML entities.  This include angle brackets: < and >,
and ampersands: &.

This is a final paragraph followed by some trailing empty lines.

"""

    ### ZIH early testing
    if False:
        block_reader = BlockInput( source )
        for block in block_reader:
            print '=== Start Block ==='
            print block
            print '=== End Block ==='
            print 'Num Lines: {}\nNum Blocks: {}'.format(
                block_reader.nlines,
                block_reader.nblocks
            )
    elif False:
        block_reader = BlockInput( source )
        for block in block_reader:
            eblock = BlockElement( block )
            print '=== Block: "{}"'.format( eblock.name )
            print eblock.get_html()
    else:
        syntax = 'a + b - c'
        source = Input( syntax )
        lexer = Lexer(
            stream = source,
            tspecs = [ ( 'L', r'\w' ), ( 'O', r'[+-]' ) ]
        )
        for token in lexer:
            print 'found {} with value of {} at {}'.format(
                token.ident,
                token.value,
                token.position.offset
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


