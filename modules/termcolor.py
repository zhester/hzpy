#!/usr/bin/env python


"""
Terminal Colorization
=====================

This module contains a class for sending strings with color and other
attributes to a terminal application.

Simple Usage Example
--------------------

Print bold and bright red text on a white background.

    import termcolor
    termcolor.cprint(
        'Hello World',
        fg    = termcolor.brred,
        bg    = termcolor.white,
        attrs = termcolor.bold
    )

More Lax Usage
--------------

    import termcolor
    termcolor.cprint( 'Greetings Region', 'brred', 'white', 'bold' )

Cleaner Usage
-------------

When performance matters, do not use the convenience method.  Create a
`ColorStream` object, and call the `cprint()` method.

    import sys
    import termcolor
    cs = termcolor.ColorStream( sys.stdout )
    cs.cprint( 'Howdy All', 'green', 'brblack', 'bold underline' )

Style-like Usage
----------------

Nothing wrong with using some Python syntax.

    import termcolor
    style = { 'fg' : 'yellow', 'bg' : 'black', 'attrs' : 'underline' }
    termcolor.cprint( "Stylin'", **style )

New-lines
---------

By default, new-line characters are appended to the output sent by `cprint()`.
To use a different character (or an empty string), just update the
`cprint_suffix` property.

    import termcolor
    cs = termcolor.ColorStream()
    cs.cpring_suffix = ''
    for i in range( 16 ):
        cs.cprint( ' {:X} '.format( i ), i )
    cs.write( '\n' )

The `seq()` Function
--------------------

Most of the power lies in the implementation of the `seq()` function to
generate the ANSI escape sequences for a foreground, background, and other
attribute combinations.  `seq()` provides a fairly terse, but flexible
interface to generating the sequence attribute values.  The `cprint()`
function and method just pass their arguments into `seq()`, and users of the
class may find this method useful for their own output.

The color values (either foreground or background) can be given with either an
integer (0 to 15) or a shorthand string ('black', 'red', 'green', 'yellow',
'blue', 'magenta', 'cyan', 'white', 'brblack', 'brred', 'brgreen', 'bryellow',
'brblue', 'brmagenta', 'brcyan', 'brwhite').

The additional attribute value may be an integer (0 to 9) or a shorthand
string ('normal', 'bold', 'faint', 'italic', 'underline', 'blink', 'blink2',
'inverse', 'conceal', 'crossed').  To specify multiple attributes for the
sequence, a list of integers and/or strings, or a space-separated string of
the shorthand values may be used.  The following are all the same.

    import termcolor
    bu_0 = termcolor.seq( attrs = 'bold underline' )
    bu_1 = termcolor.seq( attrs = [ 1, 4 ] )
    bu_2 = termcolor.seq( attrs = [ termcolor.bold, termcolor.underline ] )
    if ( bu_0 == bu_1 ) and ( bu_1 == bu_2 ):
        print bu_0, 'This is bold and underlined.', termcolor.seq()

Note: Not all the listed attributes will be supported by any given terminal.
The only relatively reliable attributes are bold and underline.  Inverse tends
to work most of the time, as well.

"""


import sys


__version__ = '0.0.0'


#=============================================================================
# Module Constants

# invalid color value "clears" the current foreground or background color
clear = -1

# normal 8-color base values
black   = 0
red     = 1
green   = 2
yellow  = 3
blue    = 4
magenta = 5
cyan    = 6
white   = 7

# synthetic interface color values for 16-color support
brblack   = 8
brred     = 9
brgreen   = 10
bryellow  = 11
brblue    = 12
brmagenta = 13
brcyan    = 14
brwhite   = 15

# glyph/display attributes
normal    = 0
bold      = 1
faint     = 2
italic    = 3
underline = 4
blink     = 5
blink2    = 6
inverse   = 7
conceal   = 8
crossed   = 9

# maximum regular color value
_max_color  = white

# minimum "bright" color value
_min_bright = brblack

# color code offsets
_fg_offset   = 30
_bg_offset   = 40
_brfg_offset = 90
_brbg_offset = 100

# ANSI escape
_escape = '\x1b['

# reference values
_fg_reset = 39
_bg_reset = 49
_reset    = 0


#=============================================================================
class ColorStream( object ):
    """
    Sends strings to a stream with ANSI escape codes for colorization.
    """

    #=========================================================================
    def __init__( self, stream = None ):
        """
        Initializes a ColorStream object.
        """
        self.cprint_suffix = '\n'
        self.stream        = stream if stream is not None else sys.stdout


    #=========================================================================
    def __getattr__( self, name ):
        """
        Proxies the hosted stream attributes.
        """
        if hasattr( self.stream, name ):
            return getattr( self.stream, name )
        else:
            raise AttributeError(
                '\'{}\' object has no attribute \'{}\''.format(
                    self.__class__.__name__,
                    name
                )
            )


    #=========================================================================
    def clear( self, fg = False, bg = False, attrs = False ):
        """
        Selectively clears attributes on the stream.
        Note: If clearing glyph/display attributes, color is also reset.

        @param fg    Set to True to clear the current foreground color
        @param bg    Set to True to clear the current background color
        @param attrs Set to True to clear ALL attributes (including colors)
        """

        # see if the user wishes to clear glyph/display attributes
        if attrs == True:

            # clear all colors and attributes
            self.stream.write( seq() )

        # not clearing glyph/display attributes
        else:

            # prepare arguments to build the escape sequence
            kwargs = {}

            # selectively reset colors
            if fg == True:
                kwargs[ 'fg' ] = clear
            if bg == True:
                kwargs[ 'bg' ] = clear

            # set the new attributes
            if len( kwargs ) > 0:
                self.set( **kwargs )


    #=========================================================================
    def cprint( self, string, fg = None, bg = None, attrs = None ):
        """
        Prints strings to the stream with optional color.  Once printed, the
        attributes used to display the text are reset to their default values.

        See documentation for the `seq()` function for parameter information.

        @param string The string to send to the stream
        @param fg     Foreground color value
        @param bg     Background color value
        @param attrs  Glyph/display attributes
        """

        # send starting sequence, string, clear sequence, and suffix string
        self.stream.write(
            '{}{}{}{}'.format(
                seq( fg, bg, attrs ),
                string,
                seq(),
                self.cprint_suffix
            )
        )


    #=========================================================================
    def set( self, fg = None, bg = None, attrs = None ):
        """
        Sets an escape sequence on the stream.  All future output will be
        affected until the attributes are cleared/changed.

        See the `seq()` function's documentation for parameter information.
        """

        # send the escape sequence to the string
        self.stream.write( seq( fg, bg, attrs ) )


    #=========================================================================
    def _test_pattern( self ):
        """
        Sends a test pattern to the stream.
        """

        # reset color/attributes sequence
        reset = seq()

        # set up some alternating attributes
        deco = [ None, 'bold', 'underline', 'bold underline' ]

        # content legend
        self.stream.write( ' FB  ' )

        # foreground value headings
        for fg in range( 16 ):
            self.stream.write( '{:X}   '.format( fg ) )
        self.stream.write( '\n' )

        # each row iterates the backgrounds
        for bg in range( 16 ):

            # background value heading
            self.stream.write( '  {:X} '.format( bg ) )

            # each column iterates the foregrounds
            for fg in range( 16 ):

                # generate the escape sequence for this combination
                sequence = seq( fg, bg, deco[ ( fg + bg ) % 4 ] )

                # render some hex digits to display the colors/attributes
                data = '{} {:X}{:X} {}'.format( sequence, fg, bg, reset )

                # send the display example to the stream
                self.stream.write( data )

            # end of row
            self.stream.write( '\n' )


#=============================================================================
def cprint( *args, **kwargs ):
    """
    Convenience method for quick module access.

    See `ColorStream.cprint()` for interface information.
    """
    cs = ColorStream( sys.stdout )
    cs.cprint( *args, **kwargs )


#============================================================================
def seq( fg = None, bg = None, attrs = None ):
    """
    Retrieves an escape sequence for a color/attribute combination.

    To get a "reset" or "clear" sequence, do not specify any parameters to the
    method.

    @param fg    Foreground color value (numeric or string shorthand)
    @param bg    Background color value (numeric or string shorthand)
    @param attrs A list of attributes to add to the escape sequence.  The list
                 may be given as a sequence or a space-separated string.  Each
                 attribute may be any of the following: 'normal', 'bold',
                 'faint', 'italic', 'underline', 'blink', 'blink2', 'inverse',
                 'conceal', or 'crossed'.
                 Note: Few terminals will support all of these attributes.
    @return      A string containing the escape sequence bytes
    """

    # called without arguments, resets all colors and attributes
    if ( fg is None ) and ( bg is None ) and ( attrs is None ):
        return '{}{}m'.format( _escape, _reset )

    # dictionary of module variables
    mvars = globals()

    # set up the sequence buffer
    sequence = []

    # determine the foreground attribute
    if fg is not None:

        # support string shorthand
        if ( type( fg ) is str ) and ( fg in mvars ):
            fg = mvars[ fg ]

        # "clear" the foreground color
        if fg == clear:
            fg = _fg_reset

        # support 16-color values
        elif fg > _max_color:
            fg = _brfg_offset + ( fg - _min_bright )

        # support 8-color values
        else:
            fg = _fg_offset + fg

        # set the foreground attribute for this sequence
        sequence.append( str( fg ) )

    # determine the background attribute
    if bg is not None:

        # support string shorthand
        if ( type( bg ) is str ) and ( bg in mvars ):
            bg = mvars[ bg ]

        # "clear" the background color
        if bg == clear:
            bg = _bg_reset

        # support 16-color values
        elif bg > _max_color:
            bg = _brbg_offset + ( bg - _min_bright )

        # 8-color value
        else:
            bg = _bg_offset + bg

        # set the background attribute for this sequence
        sequence.append( str( bg ) )

    # determine extra glyph/display attributes
    if attrs is not None:

        # support space-separated strings
        if type( attrs ) is str:
            attrs = attrs.split()

        # support singular integers
        elif type( attrs ) is int:
            attrs = [ attrs ]

        # determine all attribute values
        for attr in attrs:

            # integer values are used directly
            if type( attr ) is int:
                sequence.append( str( attr ) )

            # string notation references the integer in the object
            elif attr in mvars:
                sequence.append( str( mvars[ attr ] ) )

    # construct the complete escape sequence
    return '{}{}m'.format( _escape, ';'.join( sequence ) )



#=============================================================================
def _test_colorstream( log ):
    """
    Tests the ColorStream class.
    """

    # escapes the escapes for test log output
    def escesc( string ):
        result = ''
        for c in string:
            oc = ord( c )
            if oc < 32:
                result += '\\x{:x}'.format( oc )
            else:
                result += c
        return result

    # sequence generation test cases
    cases = [
        # no parameters to `seq()`, sends a "reset"
        [ [],                                         '\x1b[0m'          ],
        # black foreground
        [ [ 'black' ],                                '\x1b[30m'         ],
        # red foreground
        [ [ 'red' ],                                  '\x1b[31m'         ],
        # black foreground, white background
        [ [ 'black', 'white' ],                       '\x1b[30;47m'      ],
        # black fg, white bg, bold glyphs
        [ [ 'black', 'white', 'bold' ],               '\x1b[30;47;1m'    ],
        # bright green fg, bright black bg, bold glyphs, underlined text
        [ [ 'brgreen', 'brblack', 'bold underline' ], '\x1b[92;100;1;4m' ],
        # integer usage test
        [ [ 2, 3, [ 1, 4 ] ],                         '\x1b[32;43;1;4m'  ]
    ]

    # check each test case
    log.put( 'Testing escape sequence generation.' )
    for case in cases:
        actual = seq( *case[ 0 ] )
        if actual != case[ 1 ]:
            log.fail(
                '{} != {}'.format( escesc( actual ), escesc( case[ 1 ] ) )
            )

    # set/clear test cases
    cases = [
        # no parameters to set, uses the default parameters to `seq()`
        [ 'set',   {},                    '\x1b[0m'  ],
        # set black
        [ 'set',   { 'fg' : 'black' },    '\x1b[30m' ],
        # set white
        [ 'set',   { 'bg' : 'white' },    '\x1b[47m' ],
        # set bold
        [ 'set',   { 'attrs' : 'bold'  }, '\x1b[1m'  ],
        # no change, test method will report previous sequence
        [ 'clear', {},                    '\x1b[1m'  ],
        # clear the background color
        [ 'clear', { 'bg' : True },       '\x1b[49m' ]
    ]

    # dummy stream for testing
    class dummy_stream:
        def __init__( self ):
            self.value = ''
        def get_last_sequence( self ):
            index = self.value.rindex( '\x1b' )
            return self.value[ index : ]
        def write( self, string ):
            self.value += string
    ds = dummy_stream()

    # check each test case
    log.put( 'Testing cumulative escape sequences.' )
    scs = ColorStream( ds )
    for case in cases:
        getattr( scs, case[ 0 ] )( **case[ 1 ] )
        actual = ds.get_last_sequence()
        if actual != case[ 2 ]:
            log.fail(
                '{} != {}'.format( escesc( actual ), escesc( case[ 2 ] ) )
            )

    # generate a test pattern for visual verification
    log.put( 'Displaying test pattern on stdout.' )
    cs = ColorStream( sys.stdout )
    cs._test_pattern()

    # return success to the user
    return True


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
        description = 'Terminal Colorization',
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
    sys.exit( main( sys.argv ) )

